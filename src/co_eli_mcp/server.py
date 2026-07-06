"""FastMCP entry point - Colombian Constitutional Court (Corte Constitucional) tools.

Run:

    python -m co_eli_mcp.server

Configuration via env:

- ``CO_ELI_CACHE_DIR`` (default ``~/.matematic/cache/co-eli``)
- ``CO_ELI_AUDIT_DIR`` (default ``~/.matematic/audit``)
- ``CO_ELI_BASE_URL`` (default ``https://www.datos.gov.co/resource/v2k4-2t8s.json``)
"""

from __future__ import annotations

import dataclasses
import os

import httpx
from fastmcp import FastMCP
from mcp.types import ToolAnnotations

from .audit import AuditLogger, hash_input, timer
from .citations import build_citation, parse_sentencia
from .client import DEFAULT_BASE_URL, DatosGovClient

INSTRUCTIONS = """\
This MCP server exposes the datos.gov.co open-data record of decisions (sentencias) by the Colombian Constitutional Court (Corte Constitucional). It verifies whether a citation exists and gives its metadata - it does not fetch full decision text (this dataset has no full-text field).

## Call order

1. `co_search_sentencias` - free-text search (e.g. by keyword in `magistrado_a` or `proceso`).
2. `co_get_sentencia` - exact lookup by citation, e.g. `"T-012/92"`. Use this to verify a citation actually exists before trusting it (anti-hallucination check, similar in spirit to citation-grounding-pl).

## Hard constraints

- **No full-text retrieval** - only metadata (proceso, expediente, magistrado ponente, sala, fecha). The `source_url` points to the public Corte Constitucional relatoria page where the full text lives.
- **Every response has `human_readable_citation` + `source_url`** - cite both to the user.
- **Audit log JSONL** - every tool call appends to `~/.matematic/audit/co-eli-mcp.jsonl`.

## Error iteration

Tools return a structured error with a `[code]` prefix:
- `invalid_arg` - a parameter is missing or malformed.
- `not_found` - no sentencia matches that exact citation.
- `upstream_error` - a datos.gov.co API error (HTTP, timeout). Retry once before surfacing.

## Response style

- Cite decisions as `human_readable_citation`: "T-012/92".
- NEVER invent a sentencia citation, magistrado name or date - take each from the tool output. If `co_get_sentencia` returns `not_found`, say so plainly instead of guessing.
"""


class ToolError(Exception):
    """Structured error for co-eli MCP tools - visible to the LLM with a [code] prefix."""

    VALID_CODES = frozenset({"invalid_arg", "not_found", "upstream_error"})

    def __init__(self, code: str, message: str):
        if code not in self.VALID_CODES:
            raise ValueError(f"Unknown ToolError code: {code}. Valid: {sorted(self.VALID_CODES)}")
        self.code = code
        super().__init__(f"[{code}] {message}")


READ_ONLY = ToolAnnotations(
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True,
)

mcp: FastMCP = FastMCP(name="co-eli-mcp", instructions=INSTRUCTIONS)


def _base_url() -> str:
    return os.environ.get("CO_ELI_BASE_URL", DEFAULT_BASE_URL)


def _audit() -> AuditLogger:
    return AuditLogger()


def _map_upstream(exc: Exception) -> Exception:
    if isinstance(exc, (httpx.HTTPStatusError, httpx.TransportError, httpx.TimeoutException)):
        return ToolError("upstream_error", f"datos.gov.co API error: {type(exc).__name__}: {exc}")
    return exc


def _to_dict(s) -> dict:
    citation = build_citation(s)
    return {**dataclasses.asdict(s), **dataclasses.asdict(citation)}


# ---------------------------------------------------------------------------
# co_search_sentencias
# ---------------------------------------------------------------------------


@mcp.tool(annotations=READ_ONLY)
async def co_search_sentencias(query: str, limit: int = 20) -> dict:
    """Free-text search over Corte Constitucional decision metadata.

    Args:
        query: free text (e.g. part of a magistrado's name, or "tutela").
        limit: max results (default 20).

    Returns:
        ``{"total": int, "items": [...]}`` - each item carries the citation contract.
    """
    audit = _audit()
    if not query or not query.strip():
        raise ToolError("invalid_arg", "query must be a non-empty string.")
    input_hash = hash_input({"query": query, "limit": limit})

    with timer() as t:
        try:
            async with DatosGovClient(base_url=_base_url()) as client:
                raw_items = await client.search(query, limit)
        except Exception as exc:
            audit.log(tool="co_search_sentencias", input_hash=input_hash, output_count_or_size=0,
                      duration_ms=t.duration_ms if t.duration_ms else 0, status="error",
                      error=f"{type(exc).__name__}: {exc}")
            raise _map_upstream(exc) from exc

    items = [_to_dict(parse_sentencia(r)) for r in raw_items]
    audit.log(tool="co_search_sentencias", input_hash=input_hash, output_count_or_size=len(items),
              duration_ms=t.duration_ms, status="ok")
    return {"total": len(items), "items": items}


# ---------------------------------------------------------------------------
# co_get_sentencia
# ---------------------------------------------------------------------------


@mcp.tool(annotations=READ_ONLY)
async def co_get_sentencia(sentencia: str) -> dict:
    """Verify a Corte Constitucional citation and fetch its metadata.

    Args:
        sentencia: exact citation, e.g. ``"T-012/92"``.

    Returns:
        A dict with ``proceso``, ``expediente_tipo``, ``expediente_numero``,
        ``magistrado_ponente``, ``sala``, ``sentencia``, ``fecha_sentencia``,
        ``lex_uri``, ``human_readable_citation``, ``source_url``.
    """
    audit = _audit()
    if not sentencia or not sentencia.strip():
        raise ToolError("invalid_arg", "sentencia must be a non-empty string, e.g. 'T-012/92'.")
    input_hash = hash_input({"sentencia": sentencia})

    with timer() as t:
        try:
            async with DatosGovClient(base_url=_base_url()) as client:
                raw_items = await client.get_by_sentencia(sentencia)
        except Exception as exc:
            audit.log(tool="co_get_sentencia", input_hash=input_hash, output_count_or_size=0,
                      duration_ms=t.duration_ms if t.duration_ms else 0, status="error",
                      error=f"{type(exc).__name__}: {exc}")
            raise _map_upstream(exc) from exc

    if not raw_items:
        raise ToolError("not_found", f"No sentencia matching {sentencia!r} in Corte Constitucional records.")
    result = _to_dict(parse_sentencia(raw_items[0]))
    audit.log(tool="co_get_sentencia", input_hash=input_hash, output_count_or_size=1,
              duration_ms=t.duration_ms, status="ok")
    return result


def main() -> None:
    """Run the MCP server over stdio (default for Claude Code)."""
    mcp.run()


if __name__ == "__main__":
    main()
