"""Async httpx client for the Colombian open-data Socrata portal (datos.gov.co).

Keyless, JSON, dataset "Sentencias proferidas por la Corte Constitucional"
(resource id v2k4-2t8s). Metadata only - no full-text field in this dataset.
"""

from __future__ import annotations

import anyio
import httpx

from .cache import HttpCache

DEFAULT_BASE_URL = "https://www.datos.gov.co/resource/v2k4-2t8s.json"
DEFAULT_TIMEOUT = httpx.Timeout(40.0, connect=10.0)
USER_AGENT = "co-eli-mcp/0.1.0 (+https://github.com/matematicsolutions/co-eli-mcp)"

_RETRY_STATUS = frozenset({429, 500, 502, 503, 504})
_MAX_ATTEMPTS = 3


class DatosGovClient:
    """Async client. Use as ``async with DatosGovClient() as c: ...``."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        cache: HttpCache | None = None,
        timeout: httpx.Timeout = DEFAULT_TIMEOUT,
    ) -> None:
        self.base_url = base_url
        self._cache = cache or HttpCache()
        self._http = httpx.AsyncClient(
            timeout=timeout,
            headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
        )

    async def __aenter__(self) -> DatosGovClient:
        return self

    async def __aexit__(self, *_exc: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._http.aclose()
        self._cache.close()

    async def _get_json(self, params: dict[str, str], *, category: str) -> list[dict]:
        cache_key = self.base_url + "?" + "&".join(f"{k}={v}" for k, v in sorted(params.items()))
        cached = self._cache.get(cache_key)
        if cached is not None and isinstance(cached, list):
            return cached
        last_exc: Exception | None = None
        for attempt in range(_MAX_ATTEMPTS):
            try:
                resp = await self._http.get(self.base_url, params=params)
                resp.raise_for_status()
                data = resp.json()
                self._cache.set(cache_key, data, ttl=HttpCache.ttl_for(category))
                return data
            except httpx.HTTPStatusError as exc:
                last_exc = exc
                if exc.response.status_code not in _RETRY_STATUS or attempt == _MAX_ATTEMPTS - 1:
                    raise
            except (httpx.TransportError, httpx.TimeoutException) as exc:
                last_exc = exc
                if attempt == _MAX_ATTEMPTS - 1:
                    raise
            await anyio.sleep(0.5 * (2**attempt))
        assert last_exc is not None
        raise last_exc

    async def search(self, query: str, limit: int = 20) -> list[dict]:
        return await self._get_json({"$q": query, "$limit": str(limit)}, category="search")

    async def get_by_sentencia(self, sentencia: str) -> list[dict]:
        escaped = sentencia.replace("'", "''")
        return await self._get_json(
            {"$where": f"sentencia='{escaped}'"}, category="act"
        )
