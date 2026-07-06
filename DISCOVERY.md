# Discovery notes - Colombia

Date: 2026-07-06.

## Why Corte Constitucional metadata, not full text

An earlier regional sweep of Latin American sources ranked Colombia highest
by ROI outside Brazil and the US: highest lawyers-per-capita ratio in the
world (~425,000 lawyers, 801 per 100,000 people) and a confirmed
machine-readable, keyless dataset via the national open-data portal
(datos.gov.co, Socrata).

The dataset only carries metadata, not full decision text. That is enough
for a citation-verification tool - "does T-012/92 exist, who wrote it, when"
- which is a genuinely useful anti-hallucination check, in the same spirit as
`citation-grounding-pl`. Fetching full text would mean scraping
`corteconstitucional.gov.co/relatoria/...` HTML pages, a different (and more
fragile) class of connector than the rest of this fleet - not built here.

## SUIN-Juriscol (legislation) - not covered

SUIN-Juriscol (`suin-juriscol.gov.co`) indexes Colombian legislation but is
primarily an HTML search interface. Colombia does publish some legislative
data through datos.gov.co too, but that was not probed in this pass - a
natural v0.2 feature for this repo if it turns out to be structured data
rather than another HTML-only search.
