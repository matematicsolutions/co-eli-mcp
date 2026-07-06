"""Citation contract for co-eli-mcp.

Colombia has no ELI/ECLI-style identifier for Corte Constitucional decisions.
The citation itself (e.g. "T-012/92") already IS the human-readable form used
in practice; we derive the public relatoria URL from it plus the full year
(the sentencia string only carries a 2-digit year, so we take the 4-digit
year from `fecha_sentencia` instead of guessing a century).
"""

from __future__ import annotations

from typing import Any

from .models import Citation, Sentencia

_RELATORIA_URL = "https://www.corteconstitucional.gov.co/relatoria/{year}/{slug}.htm"


def parse_sentencia(raw: dict[str, Any]) -> Sentencia:
    return Sentencia(
        proceso=raw.get("proceso"),
        expediente_tipo=raw.get("expediente_tipo"),
        expediente_numero=raw.get("expediente_numero"),
        magistrado_ponente=raw.get("magistrado_a"),
        sala=raw.get("sala"),
        sentencia=raw["sentencia"],
        fecha_sentencia=raw.get("fecha_sentencia"),
    )


def build_citation(s: Sentencia) -> Citation:
    slug = s.sentencia.replace("/", "-")
    year = s.fecha_sentencia[:4] if s.fecha_sentencia else "19" + s.sentencia.split("/")[-1]
    source_url = _RELATORIA_URL.format(year=year, slug=slug)
    return Citation(lex_uri=source_url, human_readable_citation=s.sentencia, source_url=source_url)
