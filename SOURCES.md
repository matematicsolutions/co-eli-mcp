# Sources

## datos.gov.co - Sentencias proferidas por la Corte Constitucional (`v2k4-2t8s`)

- **Origin**: Corte Constitucional de Colombia, published via the national
  open-data portal (Socrata).
- **License**: open data.
- **Access**: keyless REST (Socrata SoQL), JSON.
- **Coverage**: all decisions from 1992 to the present, updated monthly per
  the dataset description. Metadata only - proceso, expediente, magistrado
  ponente, sala, sentencia citation, date. No full-text field.
- **Confirmed live** 2026-07-06: `$where=sentencia='T-012/92'` (exact lookup)
  and `$q=<text>` (free-text search) both work as documented.

## Public full-text source (not fetched by this connector)

`corteconstitucional.gov.co/relatoria/{year}/{TYPE}-{NUMBER}-{YY}.htm` serves
the full decision as HTML. Confirmed reachable (HTTP 200) for a 1992 citation.
Year in the URL path is the full 4-digit year (from `fecha_sentencia`), not
the 2-digit year suffix in the citation string itself.
