# Verification - Denver net housing change brief

Independent second pass (code/verify.py), written separately from
code/analyze.py: headline counts recomputed from the saved extracts with
plain JSON parsing (no geopandas), live REST returnCountOnly queries
against the services, neighborhood figures cross-checked against the
services' own NEIGHBORHOOD field instead of the spatial join, spatial
splits recomputed with a polygon-side sjoin, address pairing recomputed
with a second normalizer, and brief #1's figures recomputed from brief
#1's own saved extract. Full ledger: verification_results.json.

## Outcome: 70 figures REPRODUCED / 0 CORRECTED / 3 CAVEATED or EXPLAINED

Reproduced exactly include: both extract row counts; active/cancelled
counts; new-building (11,585) and phased (2,069) totals; demolition WRECK
rows (3,843) and active demolitions (3,837); non-wreck line items
excluded (1,309); net structures (+7,748) and net including phased
(+9,817); gross activity (15,422); all 21 by-year figures (new buildings,
demolitions, net for 2020-2026); UNITS coverage and reported sums for
both datasets; earliest and latest issue dates; REST counts for permits,
demolition rows, WRECK rows and new-building rows; the commercial
service's zero WRECK count; new buildings inside growth areas (2,940),
demolitions inside growth areas (638), and both SU-zoning counts (4,222
and 2,142) under an independently written sjoin; and the neighborhood
figures for all ten spot-checked neighborhoods (including Sun Valley,
Civic Center, Globeville) under the NEIGHBORHOOD-field method.

## Caveated / explained

1. Same-address pairing share: analyze.py's normalizer gives 62.5% of
   demolitions at a street address with a new-building permit in the
   window; the verification normalizer gives 62.4%. Agreement within
   rounding across two independent implementations. The brief reports
   62% and also discloses the strict exact-string floor, 36.3%.
2. Brief #1 bridge: brief #1 published 30,902 active permits / 11,559
   new buildings from a 2026-10-11 pull. Recomputing from brief #1's own
   extract reproduces both numbers exactly once brief #1's own pipeline
   step - dropping 73 records whose geometry is null - is replicated
   (a naive recount without that step gives 30,975 / 11,575). This
   brief's fresh 2026-10-14 pull gives 31,005 / 11,585. The new-building
   delta of +26 decomposes as +6 permits issued 2026-10-12 (the extra
   day covered) and +20 records issued on or before 2026-10-11 that were
   added or revised in Accela between the two pulls. No figure in either
   brief is wrong; the extracts are snapshots three days apart.
3. Demolition undercount bound: 13 WRECK-class records sit in the
   residential service (10 at addresses absent from the demolition
   service). Headline demolitions (3,837) could be understated by at
   most 13 (0.3%). Disclosed in the brief.

## Methods checklist (standards section 3)

- Base rates and exposure: counts are permit structures, and the brief
  does not normalize by existing housing stock per neighborhood - no
  stock denominator is published at statistical-neighborhood level in
  the permit system, and building one from current parcel data would
  mix post-change stock into the denominator. Churn is therefore
  reported as a share of gross permit activity (internally normalized),
  and neighborhood net counts are always printed with their gross
  counts. No causal pattern is implied from raw shares.
- Direction of causality: the brief makes no causal claim. The pairing
  analysis is temporal association at an address (demolition, then a
  new-building permit at the same address); it does not establish that
  any specific demolition caused any specific replacement, and the
  brief says so.
- Category and definition changes: CLASS labels were restyled during
  the window in both services (ALL-CAPS through ~2023, Title Case from
  ~2024, plus a '6-Wreck' no-space variant) - a label change, not a
  class change; the same class set appears in both eras. Counting is
  case- and prefix-insensitive, and the REST variant-list counts match
  the normalized counts exactly, confirming no class was missed. The
  demolition service itself only carries permits issued after
  2015-06-07 (city's service text), which does not bind this window.
  Neighborhood boundaries and Blueprint geography are the current
  published layers, applied to the whole window, as in brief #1.
- Time windows: exact window stated on every figure (issued 2020-01-01
  to 2026-10-12, Denver dates; 2026 partial). Blueprint Denver (2019)
  was in effect for the entire window.
- Joins: spatial joins match 99.5% of records in both datasets
  (neighborhood and zoning). Unmatched records (56 new buildings, 19
  demolitions) are records without a valid city address point; there is
  no reason to expect them to cluster in particular neighborhoods, and
  the services' NEIGHBORHOOD field - which agrees with the spatial join
  on 100% of demolition records where both exist - reproduces the same
  neighborhood counts. Address pairing match rates: 36.3% exact-string,
  ~62.5% street-address base (see caveat 1).
- Small numbers: neighborhoods with gross activity under 30 permits are
  flagged in data/neighborhood_net.csv and excluded from the churn
  ranking. Of the 11 net-negative neighborhoods, 6 have gross activity
  under 30 (Kennedy's entire record is 1 demolition); the brief names
  the five with gross >= 30 separately.
- Official definitions: growth areas use Blueprint Denver's own
  GROWTH_FUTURE geography (source 7); single-unit zoning uses the
  city's ZONE_USE_FORM classification; 'demolition' uses the city's
  permit CLASS taxonomy within its own DEMO permit type.
- Layering admission test: 
  ADMITTED - Blueprint growth-area geography. Claim the brief could
  not make without it: netting demolitions leaves the growth-plan
  geography essentially unchanged (70.3% of net growth outside the
  designated areas, vs 74.6% of gross new buildings in brief #1), and
  demolitions are more concentrated outside the areas (83.4%) than
  new construction is.
  ADMITTED - Same-address pairing. Claim: most demolition is
  teardown-and-replace - 60.0% of demolitions are followed by a
  new-building permit at the same street address within the window
  (median 85 days). Neither dataset alone can show this.
  ADMITTED - Zoning. Claim: demolitions concentrate in single-unit
  zoning (56.1% of matched demolition sites) far more than new
  construction does (36.6%), locating most teardown activity in
  single-unit neighborhoods.
  CUT - Assessor / year-built join for demolished structures.
  Demolished buildings no longer exist in the city's current assessor
  and building-outline layers, so what was torn down (age, size, units)
  cannot be recovered from them; the only source is the demolition
  permit UNITS field, which is 41% complete. No claim was available
  that survives that gap.
  CUT - ACS tenure / income layer. No claim was specified in advance
  that this brief needs, and neighborhood-level ACS figures would
  require a tract-to-neighborhood allocation that was not validated
  in this build. Cut under the admission test rather than added for
  decoration; the displacement-adjacent questions it could inform are
  recorded in reviewer-notes.md as future work.
- Permits vs completions: an issued permit is not a finished building,
  on either side of the ledger. Cancelled permits are excluded (brief
  #1's definition); permits that lapse later or projects that stall
  are not observable in this data. The brief says 'permitted'
  throughout.
- Window edges: a demolition late in the window whose replacement is
  permitted after 2026-10-12 counts as unpaired, and a new building
  whose demolition was permitted in 2019 counts as unpaired. The
  pairing shares are therefore floors for teardown-and-replace
  activity, and the brief says so.

---

# Pre-flight audit (brief-writing standards, section 10)

Run 2026-10-15 against this package as built (window: permits issued
2020-01-01 to 2026-10-12, Denver dates). Method: a third, independent
implementation written for this audit - plain JSON parsing of the saved
extracts in data/ (no geopandas), Denver dates via zoneinfo, spatial
joins via a hand-rolled point-in-polygon index, and both address
normalizers (analyze.py's base_address and verify.py's base2). Every
figure below was recomputed from the raw data files, not copied from
stats.json or verification.md. Read-only audit: no package file was
modified.

## Gate summary

- 10.1.1 Zero/null sentinel traps: PASS (three observations recorded,
  none changes a published figure)
- 10.1.2 Filter polarity: PASS
- 10.1.3 Numerator/denominator unit agreement: PASS
- 10.1.4 Categorical exhaustiveness: PASS (full counters below)
- 10.2.1 Join hygiene: PASS (cross-street snapping NOT APPLICABLE - no
  linear-network snapping exists in this brief)
- 10.2.2 Built-in control group: PASS, qualified (cross-method
  consistency controls, not a ground-truth control group)
- 10.3.1 README/imports sync: FAIL (minor - Pillow missing from the
  README dependency list)
- 10.3.2 Brief numbers vs stats.json: FAIL (minor - one figure: the
  same-address replacement rate is 60.0%, printed as 60.1%)

## 10.1.1 Zero/null sentinel traps - PASS

No numeric field is range-bucketed anywhere in code/analyze.py, and no
published rate uses UNITS, VALUATION, or any other sentinel-carrying
field as a numerator or denominator (see 10.1.3). Field-by-field:

- DATE_ISSUED: zero nulls in either extract. Denver-date range of both
  extracts is exactly 2020-01-01 to 2026-10-12. No epoch/0 sentinels.
- CANCEL (the cancelled-permit sentinel): active is tested as
  "CANCEL is null" in both analyze.py and this audit, which is the
  correct test for this field. Non-null values are genuine timestamps:
  195 permit rows and 14 demolition-service rows carry one; the
  smallest non-null value in either file is 1578614400000
  (2020-01-02). No 0, empty-string, or -1 sentinels exist in the field.
- CLASS: 4 permit rows and 2 demolition rows have CLASS = null. They
  fall through to "other" / non-WRECK and are visible in the counters
  in 10.1.4; they are not silently counted in any published class.
- VALUATION (demolitions, active): 14 nulls, 22 zeros, no negatives.
  Median is $8,000 with zeros included and $8,000 with zeros excluded.
  The median is a context stat in stats.json and is not cited in the
  brief, so the zeros have no published effect.

Observation 1 - UNITS zeros are counted as coverage, not mapped to
"unknown". analyze.py's units_stats treats UNITS = 0 as numeric:
31 of 6,473 numeric new-building records and 33 of 1,589 numeric
demolition records are 0. Effect on published figures: none. The
brief's coverage figures (55.9% of new-building permits, 41.4% of
demolition permits) round identically whether coverage is computed as
numeric share, as field-nonnull share (6,475 of 11,585; 1,589 of
3,837), or as numeric-excluding-zero share. UNITS feeds no rate in the
brief; the only published UNITS aggregates are the coverage shares and
the recorded-units total below.

Observation 2 - three demolition records carry UNITS = "-1":
2022-DEMO-0000597 (1374 S VINE ST), 2022-DEMO-0000635 (759 S GAYLORD
ST), 2025-DEMO-0000011 (2335 N Irving ST). They are included in the
published "2,032 units recorded across 1,589 permits" (this audit
recomputed the sum as exactly 2,032 including the three -1 values;
excluding them gives 2,035). The brief phrases the figure as what the
city recorded, so the statement is accurate as written; the -1 values
are a source-data quality footnote. Two new-building records carry
non-numeric UNITS strings ("IRC", "1DAVID STALHEIM"); pd.to_numeric
coerces them to null, which is the correct handling, and this audit's
string-based count agrees (6,473 numeric).

Observation 3 - the zoning layer itself carries a sentinel-style code:
ZONE_USE_FORM = "999" on 1,452 of 3,777 zoning polygons (the real
use-form codes are alphabetic: SU, TU, RH, MU, MX, RX, MS, RO, CC,
IMX, MHC). analyze.py counts a site as zoning-matched when its point
falls in any zoning polygon, including a "999" polygon: 1,862
new-building sites and 241 demolition sites sit in "999" polygons and
are inside the denominators of the Finding 5 shares (4,222 of 11,529
and 2,142 of 3,818). If "999" were mapped to "unknown" and excluded,
the shares would be 43.7% (new buildings) and 59.9% (demolitions)
instead of 36.6% and 56.1%. The Finding 5 contrast survives and widens
under that treatment, and the "999" sites are counted symmetrically on
both sides and never counted as SU, so no published figure is
distorted; but a future brief using this layer should state how "999"
is treated.

## 10.1.2 Filter polarity - PASS

Window filter (date >= 2020-01-01 and date <= 2026-10-12 on
Denver-local dates) matches the stated intent in the analyze.py
docstring ("permits ISSUED 2020-01-01 through 2026-10-12"). Samples:

- Earliest 3 included records, all Denver date 2020-01-01:
  2019-RESCON-0002856 (NEW BUILDING, 660 W WARREN AVE),
  2018-RESCON-0007057 (NEW BUILDING, 1035 S COLUMBINE ST),
  2019-RESCON-0006929 (ALTERATION/TENANT FINISH, 417 S DALE CT).
- Latest 3 included records, all Denver date 2026-10-12:
  2026-RESCON-0003202 (New Building, 43 S Clarkson ST),
  2026-RESCON-0003234 (Alteration/Tenant Finish, 2685 W Water AVE),
  2026-DEMO-0000266 (6-Wreck, 1366 S Lincoln ST).
- Excluded sample: none exists in the saved extracts. download.py
  pre-filtered server-side (DATE_ISSUED >= 2020-01-01 UTC, no upper
  bound), and both extracts contain exactly zero rows whose Denver
  date falls outside the window - no pre-window rows despite the UTC
  server filter, and no post-2026-10-12 rows (2026-10-12 was the
  latest issue date in the services at pull time). Polarity is
  therefore confirmed by exact boundary inclusion at both ends plus
  verify.py's live REST counts for the same window, which matched the
  extract counts.

WRECK filter (equality on the normalized class, applied before the
active test). Matched sample: 2018-DEMO-0001240 (CLASS "6 - WRECK",
2021-06-24), 2019-DEMO-0000274 ("6 - WRECK", 2020-01-16; this row is
cancelled and is correctly removed by the later active test, not by
the class filter), 2019-DEMO-0000302 ("6 - WRECK", 2020-04-12).
Excluded sample: 2019-DEMO-0000297 and 2019-DEMO-0000298
("2 - ADDITION TO BUILDING"), 2019-DEMO-0000326 ("4 - ALTERATION").
Direction and intent agree; an equality filter has no inequality to
invert.

## 10.1.3 Numerator/denominator unit agreement - PASS

Every rate in stats.json was recomputed from this audit's own counts.
In each case the numerator and denominator are the same unit of
observation - permit structures. The units-vs-permits question is
resolved in favor of structures throughout, as the brief states.

- churn_citywide_pct 24.9 = 3,837 demolitions / 15,422 gross
  structures (11,585 new buildings + 3,837 demolitions). Agrees.
- demos_per_100_new 33.1 = 3,837 / 11,585 structures. Agrees.
- new_building_in_growth_pct 25.4 = 2,940 / 11,585. Agrees.
- demolitions_in_growth_pct 16.6 = 638 / 3,837. Agrees.
- SU zoning shares use matched-site denominators on both sides:
  demolitions 56.1 = 2,142 / 3,818 matched sites; new buildings
  36.6 = 4,222 / 11,529 matched sites. The brief prints both
  denominators. Agrees (see observation 3 in 10.1.1 for the "999"
  composition of the matched sets).
- Pairing shares: demolition shares are over 3,837 demolitions,
  new-building shares over 11,585 new buildings (10.2.1). Agrees.
- Neighborhood churn_pct = demolitions / gross structures per
  neighborhood. Agrees.
- UNITS appears in no rate. The published UNITS aggregates are
  coverage shares (denominator: permits) and one recorded sum
  (2,032 units over 1,589 demolition permits), which is a total, not
  a rate.

## 10.1.4 Categorical exhaustiveness - PASS

Counter(CLASS) over the full saved extracts (the extracts contain
only in-window rows, so these are also the in-window counts).

Residential construction service (permits_2020.geojson, 31,200 rows),
raw values: NEW BUILDING 8,432; ALTERATION/TENANT FINISH 7,826;
Alteration/Tenant Finish 3,764; New Building 3,203; ADDITION 1,662;
PHASED CONSTRUCTION 1,322; Addition 1,010; REPAIR/REPLACE 1,003;
Repair/Replace 899; Phased Construction 759; NEW NON-BUILDING
STRUCTURE 319; CHANGE OF CONTRACTOR 287; New Non-Building Structure
263; Change of Contractor 217; FOUNDATION ONLY/EXCAVATION 142;
Change of Use Only 26; Foundation Only/Excavation 20; CHANGE OF USE
ONLY 18; MOVE 7; Wreck 6; WRECK 4; (null) 4; 1 - New Building 3;
6 - WRECK 3; 2 - Addition to building 1.
Normalized (upper-case, "N - " prefix stripped): NEW BUILDING 11,638;
ALTERATION/TENANT FINISH 11,590; ADDITION 2,672; PHASED CONSTRUCTION
2,081; REPAIR/REPLACE 1,902; NEW NON-BUILDING STRUCTURE 582; CHANGE
OF CONTRACTOR 504; FOUNDATION ONLY/EXCAVATION 162; CHANGE OF USE ONLY
44; WRECK 13; MOVE 7; (empty) 4; ADDITION TO BUILDING 1.
All NEW BUILDING spelling/prefix variants normalize into the counted
class; the new-building total (11,638 rows, 11,585 active) matches
stats.json and verify.py's REST variant-list count. The 13 WRECK
records in this service (Wreck 6 + WRECK 4 + 6 - WRECK 3, all active
and in-window) are the disclosed undercount bound for demolitions.

Demolition service (demolitions_2020.geojson, 5,152 rows), raw
values: 6 - WRECK 2,142; 6 - Wreck 1,483; 4 - ALTERATION 777;
4 - Alteration 452; 6-Wreck 218; ALTERATION/TENANT FINISH 10;
5 - MOVE 9; 2 - ADDITION TO BUILDING 8; 11 - Change of contractor 8;
11 - CHANGE OF CONTRACTOR 7; 2 - Addition to building 7;
3 - REPAIR / REPLACE 6; 1 - New Building 4; NEW BUILDING 3; 5 - Move
3; (null) 2; 1 - NEW BUILDING 2; 12 - PHASED CONSTRUCTION 2;
REPAIR/REPLACE 2; 3 - Repair / replace 2; Addition 2; NEW
NON-BUILDING STRUCTURE 1; 12 - Phased Construction 1; Alteration/
Tenant Finish 1.
Normalized: WRECK 3,843; ALTERATION 1,229; ADDITION TO BUILDING 15;
CHANGE OF CONTRACTOR 15; MOVE 12; ALTERATION/TENANT FINISH 11; NEW
BUILDING 9; REPAIR / REPLACE 8; PHASED CONSTRUCTION 3; (empty) 2;
REPAIR/REPLACE 2; ADDITION 2; NEW NON-BUILDING STRUCTURE 1.
The WRECK filter captures all three spelling variants ("6 - WRECK",
"6 - Wreck", "6-Wreck" - the no-space variant is the trap this gate
exists for, and the prefix-strip normalization catches it); 3,843
matches stats.json exactly. The excluded classes sum to 1,309,
matching stats.json's demo_service_nonwreck_line_items_excluded, and
no excluded class is a plausible demolition variant.

Variant note: "2 - Addition to building" (1 record, residential
service) normalizes to "ADDITION TO BUILDING", which is not a
CLASS_MAP key after prefix-stripping, so the record lands in "other"
rather than "addition" (this audit replicates analyze.py's behavior
exactly; 5 records total land in "other", including the 4 null-CLASS
rows). The record is not a new-building, phased, or wreck permit, so
no published figure is affected. Recorded here because it is exactly
the failure shape this gate watches for.

Zoning and growth layers: Counter(ZONE_USE_FORM) over zoning.geojson:
999 1,452; MX 887; MS 330; SU 303; MU 280; RH 217; TU 161; RX 66;
CC 43; RO 22; IMX 11; MHC 5. The SU filter matches the alphabetic
code exactly and no SU variant exists. Counter(GROWTH_FUTURE) over
bp_growth_areas.geojson: Community centers and corridors 7,075;
Districts 3,586; Regional centers 1,810; Greenfield residential areas
1,573; High and high-med residential areas in D and UC contexts
1,475; ROW 20; Community Centers and Corridors 2; Low 1 - all
non-null, so analyze.py's "inside any growth polygon" treatment is
consistent across the layer.

## 10.2.1 Join hygiene - PASS (cross-street snapping NOT APPLICABLE)

This brief performs no buffer snapping of points to a linear network,
so the cross-street/perpendicular-corridor failure mode does not
arise. Its joins are point-in-polygon assignment (neighborhoods,
zoning, Blueprint growth areas) and street-address pairing between the
two permit services.

Spatial joins, recomputed with this audit's own point-in-polygon
implementation (analyze.py used geopandas sjoin, predicate "within",
first match kept):

- Neighborhood match: new buildings 11,529 of 11,585 (99.5%); phased
  2,051 of 2,069 (99.1%); demolitions 3,818 of 3,837 (99.5%). The
  unmatched counts (56 new buildings, 19 demolitions) match
  verification.md's statement. Of the 56 unmatched new buildings, 16
  have null geometry and 40 fall outside every neighborhood polygon.
- Zoning match: identical rates (99.5% / 99.1% / 99.5%); SU counts
  reproduce exactly (4,222 new buildings; 2,142 demolitions).
- Growth areas: 2,940 new buildings and 638 demolitions inside,
  reproducing stats.json exactly. Net inside +2,302, net outside
  +5,446, both as printed.
- Every published join count from this audit's independent
  implementation is identical to analyze.py's, so polygon-boundary
  handling is not producing divergent assignments.

Address pairing (the brief's relational join). Both normalizers
recomputed from raw ADDRESS fields:

- Exact-string match: demolitions at a new-building address 36.3%;
  new buildings at a demolition address 14.9%. Both match stats.json.
- Base-address match, analyze.py's normalizer: demolitions 62.5%
  (2,397 of 3,837); new buildings 29.8% (3,447 of 11,585). Both match
  stats.json and the brief's printed counts.
- Base-address match, verify.py's independent normalizer: demolitions
  62.4% (2,396); new buildings 29.7% (3,446). The pairing estimate is
  stable to normalizer choice within 0.1 percentage point.
- Timing: 2,397 matched demolitions; in 96.7% the latest new-building
  permit at the address is on or after the demolition (matches
  stats.json).

Timing-definition sensitivity (transparency note, not a defect): the
published "followed by" count (2,304, median 85 days - both recomputed
exactly by this audit) uses the code's definition: the FIRST
new-building permit at the address falls on or after the demolition
date. Under the looser reading "any later new-building permit at the
address", the count is 2,317 (60.4%), median 84 days. The 13-record
difference is addresses where construction both preceded and followed
the demolition inside the window. The published figure is the
code's definition, computed correctly; the brief's Finding 2 wording
("followed by a new-building permit at the same address", "the first
later construction permit") is consistent with it.

Physical scale: the brief reports structure counts throughout (15,422
gross structures citywide; 78 statistical neighborhoods as the
geographic frame - neighborhoods.geojson contains exactly 78
polygons, Indian Creek included, and 77 record any matched activity).
No GIS polygon or segment count is reported as if it were blocks or
parcels; the growth-area layer's 15,542 polygons are never cited as a
count of anything.

## 10.2.2 Built-in control group - PASS, qualified

Stated plainly: the package contains no purpose-built control group
of the known-expected-rate kind (the way the Nashville STR brief used
owner-occupied permits as a control). What it contains are three
cross-method consistency controls, all re-run by this audit, which
serve the gate's purpose of proving the join and classification logic
is not producing artifacts:

1. Field-vs-spatial neighborhood control: the services' own
   NEIGHBORHOOD field agrees with the spatial join on 100.0% of
   demolition records where both exist (stats.json), and the two
   neighborhoods this audit re-derived by both methods independently
   agree exactly (Sun Valley and Washington Park, below). Systematic
   join artifacts would show up as divergence between the two
   assignments; there is none.
2. Normalizer sensitivity: two independently written address
   normalizers bracket the headline pairing share at 62.4-62.5%
   (10.2.1).
3. Brief #1 reconciliation: the same class map and definitions
   reproduce brief #1's published totals (30,902 active permits,
   11,559 new buildings) from brief #1's own extract under its own
   pipeline rules (verify.py ledger: REPRODUCED), anchoring this
   brief's classification logic to a previously verified result.

### Control check: Sun Valley zero, independently re-verified

The package's flagged QA item was Sun Valley: 78 demolitions, 0
new-building permits, 0 phased permits in-window. Re-derived from the
raw data files by three methods:

1. This audit's own spatial join (point-in-polygon against
   neighborhoods.geojson): demolitions 78, new buildings 0, phased 0.
2. The services' own NEIGHBORHOOD field in the raw extracts (no
   spatial join involved): demolitions 78, new buildings 0, phased 0.
   Stronger: zero active permits of ANY class in the residential
   service carry NEIGHBORHOOD = "Sun Valley", while the demolition
   service carries 89 in-window Sun Valley rows of any class (the 78
   active WRECK records plus non-wreck line items and cancelled rows).
3. The package's data/neighborhood_net.csv row: Sun Valley
   new_building 0, phased 0, demolitions 78, net -78.

CONFIRMED. The zero is real within the brief's stated scope
(residential construction service plus demolition service, issued
2020-01-01 to 2026-10-12). The scope caveat the brief itself carries
stands: construction permitted through the commercial service is out
of scope (verify.py's live count found zero WRECK records there; the
same out-of-scope boundary applied to brief #1).

Washington Park was re-derived the same way as a positive control:
430 new buildings and 276 demolitions under both the spatial join and
the NEIGHBORHOOD field, matching the brief exactly.

## 10.3.1 Repository and documentation sync: imports - FAIL (minor)

Third-party imports actually used across code/*.py (AST scan):
analyze.py - geopandas, pandas; charts.py - geopandas, matplotlib,
pandas; compose_hero.py - PIL (Pillow); download.py - standard library
only; verify.py - geopandas, pandas (plus standard-library dynamic
imports: zoneinfo, csv, datetime).

README.md's Reproduce section states: "(Python environment:
geopandas, pandas, matplotlib.)" Pillow is missing: an environment
built from the README alone cannot run code/compose_hero.py. Every
listed dependency is genuinely used; nothing else is missing. Fix is
one line in README.md. Not applied here - this audit is read-only;
the fix belongs to the QA pass.

## 10.3.2 Repository and documentation sync: numbers - FAIL (minor)

Every number in brief-draft.md was cross-checked against stats.json,
and the decisive figures were recomputed from the raw data by this
audit. All agree except one:

DEFECT: the same-address replacement rate is printed as 60.1% but
computes to 60.0%. The underlying count is exactly right everywhere
(2,304 of 3,837 demolitions, recomputed by this audit; median gap 85
days, also recomputed). 2,304 / 3,837 = 60.05%, which rounds to 60.0%
at one decimal under any standard rounding - the printed 60.1% is a
stale or mis-rounded figure. Occurrences: brief-draft.md (TL;DR,
Finding 2, "Who can act"), README.md, verification.md (layering
admission test), reviewer-notes.md (two mentions), social-drafts.md
(LinkedIn post and X thread). The one-line summary's "60 percent" is
correct. Severity: 0.1 percentage point on one figure; the checkable
count (2,304) and the median (85 days) are correct in every location,
and no other figure depends on the percentage.

Everything else cross-checked and in agreement (audit value =
stats.json value = brief value, unless noted):

- Headline counts: 11,585 new buildings; 3,837 demolitions; net
  +7,748 structures; 33 demolitions per 100 new buildings (33.1);
  31,005 active residential permits; 11,585 of 31,005.
- Demolition definition: 3,843 WRECK rows; 1,309 non-wreck line items
  excluded; 6 cancelled WRECK rows; at most 13 stray WRECK records in
  the residential service (0.3%); zero WRECK in the commercial service
  (verify.py live REST count, REPRODUCED in its ledger).
- UNITS: coverage 55.9% / 41.4%; recorded value "1" in 98.9% / 85.5%
  of numeric records; maximums 12 / 18; demolition recorded total
  2,032 units across 1,589 permits; phased sensitivity 2,069 permits,
  net +9,817.
- Yearly: net +1,366 (2020), +1,646 (2021), +1,259 (2022), +1,345
  (2023), +890 (2024), +851 (2025), +391 (partial 2026); new buildings
  peak 2,343 (2021), 1,309 (2025); demolitions peak 743 (2022), 440
  (2024) and 458 (2025); demolition share of gross activity 22.3% to
  27.1% across 2020-2025 (this audit's recomputation: 22.7, 22.9,
  27.1, 22.3, 24.9, 25.9) and 33.3% in partial 2026 (389 demolitions,
  780 new buildings).
- Pairing: 62% base-address share (2,397 of 3,837); strict
  exact-string floor 36.3%; 29.8% of new buildings at a demolished
  address (3,447 of 11,585); 96.7% before-or-same statistic in
  stats.json.
- Neighborhoods: 78 statistical neighborhoods, 77 with any activity
  (Indian Creek none - it is present as a polygon and absent from the
  activity table), 11 net-negative. The five with gross >= 30 (Sun
  Valley 78/0/-78; Civic Center 32/0/-32; Globeville 41 demolitions,
  26 new, -15; Capitol Hill 24/10/-14; Hampden South 19/11/-8) and the
  six small-count negatives (CBD -15 on 15; Union Station -14 on 14;
  North Capitol Hill -12 on 20; Southmoor Park -2 on 6; Auraria -1 on
  1; Kennedy -1 on 1) all match data/neighborhood_net.csv and this
  audit's spatial recount. Top gainers: Central Park +1,063 (1,075
  new, 12 demolished), Gateway - Green Valley Ranch +843, DIA +733,
  West Colfax +622 (784 new, 162 demolished). Churn group: Washington
  Park 430 new / 276 demolished / net +154 (recomputed by two
  methods), Hilltop 141/107/+34 on 248 gross, Belcaro 150/105/+45 on
  255 gross; demolition share of activity 39.1% / 43.1% / 41.2%
  against the brief's "39-43 percent" and 24.9% citywide.
- Growth geography: demolitions outside growth areas 83.4% (3,199 of
  3,837); inside 16.6% (638); net inside +2,302, net outside +5,446;
  net outside share 70.3%. The 74.6% gross figure attributed to brief
  #1 also equals this package's own recomputed gross outside share
  (8,645 of 11,585).
- Zoning: 56.1% of matched demolition sites in SU zoning (2,142 of
  3,818); 36.6% of matched new-building sites (4,222 of 11,529).
- Caveat figures: 0.5% of records unmatched to a neighborhood or
  zoning polygon (99.5% match rates); demolitions understated by at
  most 13 records (0.3%).
- Hero and README headline figures agree with stats.json, apart from
  the README's repetition of the 60.1% figure noted above. The growth
  chart's rounded title figures (83% of demolitions, 75% of new
  buildings outside the growth areas) round correctly from 83.4% and
  74.6%.

## Audit bottom line

The package's data pipeline is sound: every count, join, and rate in
stats.json was reproduced exactly by an independent implementation,
the Sun Valley zero is confirmed three ways, and the pairing estimate
is stable across two normalizers. Two minor documentation defects
block a clean pass under section 10.3: the replacement rate printed
as 60.1% instead of 60.0% (in the brief, README, verification,
reviewer notes, and social drafts), and Pillow missing from the
README dependency list. Both are one-line fixes for the QA pass; no
finding, count, or conclusion in the brief changes.
