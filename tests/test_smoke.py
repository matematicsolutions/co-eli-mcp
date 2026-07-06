"""Live smoke test against the real datos.gov.co API. Network required."""

from __future__ import annotations

import pytest

from co_eli_mcp.citations import build_citation, parse_sentencia
from co_eli_mcp.client import DatosGovClient


@pytest.mark.asyncio
async def test_get_and_search_sentencia() -> None:
    async with DatosGovClient() as client:
        items = await client.get_by_sentencia("T-012/92")
        assert len(items) == 1

        s = parse_sentencia(items[0])
        citation = build_citation(s)
        assert citation.human_readable_citation == "T-012/92"
        assert citation.source_url == (
            "https://www.corteconstitucional.gov.co/relatoria/1992/T-012-92.htm"
        )

        results = await client.search("tutela", limit=2)
        assert len(results) == 2
