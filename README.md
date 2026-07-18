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


### Windows 11 with Smart App Control

Smart App Control blocks unsigned executables, which covers `uvx.exe`, `pip.exe`
and the `co-eli-mcp.exe` launcher that pip writes at install time. The `python.exe` and
`py.exe` from the python.org installer are signed by the Python Software
Foundation, so running the module through the interpreter works:

```bash
python -m pip install co-eli-mcp
python -m co_eli_mcp
```

`pip.exe` is blocked for the same reason, so install with `python -m pip`, not
`pip install`. If `python` is not on PATH, use the Windows launcher: `py -3 -m co_eli_mcp`.

```json
{ "mcpServers": { "co-eli-mcp": { "command": "python", "args": ["-m", "co_eli_mcp"] } } }
```

Do not turn Smart App Control off to work around this - it cannot be re-enabled
without reinstalling Windows.

## Configuration

| Env var | Default |
|---|---|
| `CO_ELI_CACHE_DIR` | `~/.matematic/cache/co-eli` |
| `CO_ELI_AUDIT_DIR` | `~/.matematic/audit` |
| `CO_ELI_BASE_URL` | `https://www.datos.gov.co/resource/v2k4-2t8s.json` |

## License

Apache-2.0 (code). datos.gov.co data is open data (see [SOURCES.md](SOURCES.md)).
