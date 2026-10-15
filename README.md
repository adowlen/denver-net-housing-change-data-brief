# Denver permitted 11,585 new buildings and demolished 3,837: the net housing ledger

A Machine Readable data brief (2026-10-15), the follow-up to
[denver-housing-permits-data-brief](https://github.com/adowlen/denver-housing-permits-data-brief).

Between January 2020 and October 2026, Denver issued permits for 11,585
new residential buildings and 3,837 demolitions, a net of 7,748
structures. 60.0 percent of the demolitions were followed by a
new-building permit at the same address. 11 of 78 neighborhoods
demolished more than they built, and 70.3 percent of the net growth sits
outside Blueprint Denver's designated growth areas.

Proposed repository name: **denver-net-housing-change-data-brief**
(full URL on publication: https://github.com/adowlen/denver-net-housing-change-data-brief)

## Contents

- `brief/brief.md` - the full brief, including "What this might mean" and "Who can act"
- `charts/` - hero.png plus five data charts (net change map, gainers and losses, yearly net, churn, growth-plan geography)
- `data/` - the two permit extracts, geography layers, and the derived neighborhood table (neighborhood_net.csv)
- `code/` - download.py, analyze.py, charts.py, compose_hero.py, verify.py
- `stats.json` - every headline figure in machine-readable form
- `sources.md` - numbered source audit
- `verification.md` - the independent verification ledger and methods checklist

## Data sources

City and County of Denver open data (ArcGIS): ODC_DEV_RESIDENTIALCONST-
PERMIT_P (layer 316) and ODC_DEV_DEMOLITIONPERMIT_P (layer 318), plus
the neighborhood, Blueprint Denver growth-area and zoning layers, all
pulled 2026-10-14. Full audit in sources.md.

## Reproduce

```
python code/download.py   # refreshes data/ extracts from the live services
python code/analyze.py    # writes stats.json and data/neighborhood_net.csv
python code/charts.py     # redraws the data charts
python code/verify.py     # independent second pass; writes verification_results.json
```

(Python environment: geopandas, pandas, matplotlib, Pillow.)

## Caveats (short version)

- All figures are structures (permits), not dwelling units; the permit
  data's unit fields are too incomplete to support unit counts.
- A permit issued is not a building finished, on either side of the
  ledger.
- Residential construction permits only - the same scope as the
  October 11 brief this one follows.
- Address pairing shares are floors (window edges and address-format
  variation).
- Demolitions may be understated by at most 13 records (0.3 percent).
