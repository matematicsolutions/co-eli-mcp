# co-eli-mcp

<!-- mcp-name: io.github.matematicsolutions/co-eli-mcp -->

MCP server for the datos.gov.co open-data record of decisions (sentencias) by
the Colombian Constitutional Court (Corte Constitucional). Verifies whether a
citation exists and returns its metadata.

## What this is not

This dataset (`v2k4-2t8s`, "Sentencias proferidas por la Corte Constitucional")
has no full-text field - only metadata: proceso, expediente, magistrado
ponente, sala, and date. `source_url` points to the public relatoria page
where the full decision text lives, but this connector does not fetch it.

## Tools

| Tool | Purpose |
|---|---|
| `co_search_sentencias` | Free-text search (e.g. by magistrado name or proceso type) |
| `co_get_sentencia` | Exact lookup by citation, e.g. `"T-012/92"` - verifies it exists |

Every response carries `lex_uri` and `source_url` (the public
corteconstitucional.gov.co relatoria page) and `human_readable_citation`
(the citation itself, e.g. `"T-012/92"` - already the form used in practice,
so no separate identifier scheme is needed here).

## Install

```bash
pip install co-eli-mcp
```

## Configuration

| Env var | Default |
|---|---|
| `CO_ELI_CACHE_DIR` | `~/.matematic/cache/co-eli` |
| `CO_ELI_AUDIT_DIR` | `~/.matematic/audit` |
| `CO_ELI_BASE_URL` | `https://www.datos.gov.co/resource/v2k4-2t8s.json` |

## License

Apache-2.0 (code). datos.gov.co data is open data (see [SOURCES.md](SOURCES.md)).
