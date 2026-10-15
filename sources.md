# Sources - Denver net housing change brief (permits layered with demolitions)

All data is City and County of Denver open data (ArcGIS Hub org
zdB7qR0BtYrg0Xpl, services1.arcgis.com), pulled 2026-10-14. Window for every
figure: permits ISSUED 2020-01-01 through 2026-10-12 (Denver dates);
2026-10-12 is the latest issue date present in either extract, and 2026 is
a partial year. Definitions replicate brief #1 (denver-housing-permits-
data-brief, 2026-10-11) exactly so the two briefs are comparable.

1. Residential construction permits - ODC_DEV_RESIDENTIALCONSTPERMIT_P,
   FeatureServer layer 316 (DEV_RESIDENTIALCONSTPERMIT_P). Accela RESCON
   permits, mapped by the city on a daily basis. Pulled with
   DATE_ISSUED >= 2020-01-01: 31,200 records; 31,005 not cancelled
   (CANCEL empty), 195 cancelled. Fields used: DATE_ISSUED, PERMIT_NUM,
   ADDRESS, CLASS, UNITS, CANCEL, NEIGHBORHOOD.
2. Demolition permits - ODC_DEV_DEMOLITIONPERMIT_P, FeatureServer layer
   318 (DEV_DEMOLITIONPERMIT_P). Service description (city's own text):
   permits with permit type 'DEMO' extracted from Accela and mapped daily;
   issue date is the date the permit was paid; the dataset only shows
   permits issued after June 7, 2015. Pulled with DATE_ISSUED >=
   2020-01-01: 5,152 records.
3. Demolitions definition (derived): records in source 2 whose CLASS is a
   WRECK variant ('WRECK', '6 - WRECK', '6 - Wreck', '6-Wreck'): 3,843
   records; 3,837 after removing 6 cancelled. The other 1,309 records in
   the DEMO service are non-wreck line items filed under DEMO applications
   (alteration, trade, addition and similar rows, e.g. '1515 WYNKOOP ST
   MECH'); they are not demolitions and are excluded.
4. Coverage cross-check, commercial permits - ODC_DEV_COMMERCIALCONST-
   PERMIT_P, layer 317: a live REST count of WRECK-class records issued
   2020-01-01 onward returns 0, so demolitions are not split across the
   commercial service.
5. Coverage cross-check, residential service (source 1): 13 WRECK-class
   records sit in the residential service instead of the demolition
   service; 10 of their addresses do not appear in the demolition service
   at all. Maximum effect on the demolition count: +13 (0.3%). Counted as
   a known, bounded undercount; headline uses source 2 only.
6. Neighborhoods - ODC_ADMN_NEIGHBORHOOD_A (statistical neighborhoods),
   saved extract from brief #1 (boundaries stable). 78 polygons. Records
   are assigned by spatial join (point within polygon), brief #1's method:
   99.5% of new-building permits and 99.5% of demolitions matched. The
   demolition service's own NEIGHBORHOOD field agrees with the spatial
   join on every record where both exist (verified).
7. Growth areas - ODC_PLAN_BPFUTUREPLACES_A (Blueprint Denver future
   places), saved extract from brief #1: polygons where GROWTH_FUTURE is
   not 'All other areas of the city'. "Inside a growth area" uses the
   plan's own geography and definitions (Blueprint Denver, adopted 2019,
   in effect for the whole window).
8. Zoning - ODC_ZONE_ZONING_A, saved extract from brief #1. ZONE_USE_FORM
   'SU' = single-unit zone districts (the city's own classification).
   Spatial join match rate 99.5% for both datasets.
9. Brief #1 figures used for comparison: 30,902 active permits and 11,559
   new-building permits, from denver-housing-permits-data-brief (pulled
   2026-10-11). Recomputed from brief #1's own saved extract in the
   verification pass (see verification.md for the bridge to this brief's
   31,005 / 11,585).
10. UNITS fields (sources 1 and 2): both are free-text fields in Accela.
    New-building permits: numeric value present on 6,473 of 11,585
    (55.9%); reported values sum to 6,622, are '1' in 98.9% of reporting
    records, and max out at 12 - behavior of a structure count, not a
    dwelling-unit count (large multifamily projects are permitted under
    PHASED CONSTRUCTION, a separate class). Demolition permits: numeric
    value present on 1,589 of 3,837 (41.4%); reported values sum to 2,032
    units, are '1' in 85.5% of reporting records, max 18. Because coverage
    is partial and the field does not behave as dwelling units, every
    headline figure in this brief is in STRUCTURES (permits), the same
    basis as brief #1. The recorded-units sums are reported only as the
    bounded statements in the brief.
11. Same-address pairing (derived): ADDRESS strings normalized two
    independent ways (exact string; street-address base of number +
    direction + street + street type, unit suffixes stripped). Shares of
    demolitions at an address that also has a new-building permit in the
    window: 36.3% exact, 62.5% base (62.4% under the second normalizer).
