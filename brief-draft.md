# Denver's net housing ledger: 11,585 new buildings, 3,837 demolitions

Machine Readable - 2026-10-15

**One-line summary:** Between January 2020 and October 2026, Denver issued permits for 11,585 new residential buildings and 3,837 demolitions, a net of 7,748 structures; 60 percent of the demolitions were followed by a new-building permit at the same address.

## TL;DR

- Citywide, Denver permitted 11,585 new residential buildings and 3,837 demolitions from 2020-01-01 to 2026-10-12: a net of +7,748 structures, or 33 demolitions for every 100 new buildings.
- Most demolition is teardown-and-replace: 60.0 percent of demolitions were followed by a new-building permit at the same street address within the window, a median of 85 days later.
- 11 of Denver's 78 statistical neighborhoods recorded more demolitions than new buildings. Sun Valley recorded 78 demolitions and no new-building permits at all.
- Netting demolitions does not change the geography from our first brief: 70.3 percent of net growth is outside Blueprint Denver's designated growth areas, and demolitions themselves are even more concentrated outside those areas (83.4 percent).
- 56.1 percent of demolitions are in single-unit zoning, versus 36.6 percent of new buildings.

Every figure is in structures (permits), not dwelling units. The permit data cannot support a unit count - see "What we used" - and this brief does not pretend otherwise.

## What we used

Denver publishes residential construction permits and demolition permits as two separate open datasets, both extracted daily from the Accela permitting system. This brief reads them together over the same window: permits issued 2020-01-01 through 2026-10-12, the latest issue date in either file. Definitions replicate our October 11 brief on residential construction permits exactly, so the two briefs can be read side by side: cancelled permits are excluded on both sides, and "new buildings" are permits of class New Building in the residential service (11,585 of 31,005 active residential permits).

Demolitions are the WRECK-class records inside the city's demolition permit service: 3,837 active permits. The same service carries 1,309 non-demolition line items filed under demolition applications (trade and alteration rows), which are excluded. A coverage check found zero WRECK records in the commercial construction service, and at most 13 stray WRECK records in the residential service, so 3,837 understates demolitions by at most 0.3 percent.

Structures, not units: both datasets carry a UNITS field, but it is recorded on only 55.9 percent of new-building permits and 41.4 percent of demolition permits, and where recorded it is "1" in 98.9 percent and 85.5 percent of records respectively, with maximums of 12 and 18. Large multifamily projects are permitted under a separate Phased Construction class. The field behaves as a structure count, not a dwelling-unit count, so every figure here counts structures. Where the city did record units on demolition permits, the recorded total removed is 2,032 units across 1,589 permits. A separate sensitivity figure adds Phased Construction permits (2,069) to the new-building side: the net becomes +9,817 structures. Neither version counts units inside buildings, and a demolished house replaced by a permitted duplex raises unit counts in ways this data cannot see.

Neighborhoods are the city's statistical neighborhood boundaries, assigned by spatial join (99.5 percent of records matched), the same method as the first brief. Growth areas are Blueprint Denver's own future-places geography.

## Finding 1: The city adds more than it removes every year, and the margin has narrowed

Denver's net was positive in every year of the window: +1,366 structures in 2020, +1,646 in 2021, +1,259 in 2022, +1,345 in 2023, +890 in 2024, +851 in 2025, and +391 in the partial year through October 12, 2026. New-building permits peaked in 2021 (2,343) and fell to 1,309 in 2025. Demolitions peaked in 2022 (743) and ran at 440-458 per year in 2024-2025. Demolitions were 22.3-27.1 percent of gross add-and-remove activity in 2020-2025, and 33.3 percent in the partial 2026 figures (389 demolitions against 780 new buildings through October 12).

## Finding 2: Most demolitions are followed by construction at the same address

Matched on street address, 62 percent of demolitions (2,397 of 3,837) sit at an address that also has a new-building permit in the window; a strict exact-string address match gives a floor of 36.3 percent. Of all demolitions, 60.0 percent (2,304) are followed by a new-building permit at the same address, with a median gap of 85 days between the demolition permit and the first later construction permit. Read the other way, 29.8 percent of new buildings (3,447 of 11,585) stand at an address where a structure was demolished in the same window. These shares are floors: a demolition in late 2026 whose replacement is permitted in 2027 counts as unmatched here, as does a new building whose demolition was permitted in 2019.

## Finding 3: Eleven neighborhoods demolished more than they built

Of 78 statistical neighborhoods, 77 recorded any permit activity (Indian Creek recorded none) and 11 recorded more demolitions than new buildings. Five of the 11 have gross activity of 30 or more permits:

- Sun Valley: 78 demolitions, 0 new-building permits, net -78. It also recorded no phased-construction permits in the window.
- Civic Center: 32 demolitions, 0 new buildings, net -32.
- Globeville: 41 demolitions, 26 new buildings, net -15.
- Capitol Hill: 24 demolitions, 10 new buildings, net -14.
- Hampden South: 19 demolitions, 11 new buildings, net -8.

The other six net-negative neighborhoods have small gross counts (CBD -15 on 15 permits, Union Station -14 on 14, North Capitol Hill -12 on 20, Southmoor Park -2 on 6, Auraria -1 on 1, Kennedy -1 on 1) and should be read as small numbers, not trends.

The largest net gains are at the city's edges and along West Colfax: Central Park +1,063 (1,075 new, 12 demolished), Gateway - Green Valley Ranch +843, DIA +733, West Colfax +622 (784 new, 162 demolished). A second group of neighborhoods records high gross activity and small net change - the churn group. Washington Park permitted 430 new buildings and 276 demolitions for a net of +154. Hilltop: 141 new, 107 demolished, net +34 on 248 gross permits. Belcaro: 150 new, 105 demolished, net +45 on 255 gross. In these neighborhoods, demolitions are 39-43 percent of all permit activity, against 24.9 percent citywide.

## Finding 4: Netting demolitions leaves the growth-plan geography where the first brief found it

Our October 11 brief reported that 74.6 percent of new residential buildings were permitted outside Blueprint Denver's designated growth areas. Demolitions are more concentrated outside the growth areas than construction is: 83.4 percent of demolitions (3,199 of 3,837) are outside them, against 16.6 percent inside (638). The net position is +2,302 structures inside the growth areas and +5,446 outside them, so 70.3 percent of net growth is outside the designated areas. Subtracting demolitions moves the outside share from 74.6 percent of gross construction to 70.3 percent of net change.

## Finding 5: Demolitions concentrate in single-unit zoning

56.1 percent of demolition sites with a zoning match (2,142 of 3,818) are in single-unit (SU) zone districts. The same figure for new-building sites is 36.6 percent (4,222 of 11,529 matched). Demolitions are, by site share, a single-unit-neighborhood activity to a degree that new construction is not.

## What this might mean

Two readings fit these numbers, and the data separates them only partly.

The first reading is that teardown-and-replace is the dominant form of housing production in Denver's established neighborhoods: most demolitions are followed within months by construction at the same address, demolitions cluster in single-unit zoning, and high-gross neighborhoods like Washington Park, Hilltop and Belcaro convert hundreds of permits into small net gains. Under this reading, gross construction counts overstate how much housing established neighborhoods are adding.

The strongest alternative explanation is about the unit of measurement. A demolished single-unit house replaced by one permitted building can still add homes if that building is a duplex or a small apartment building, and this brief counts structures, not units, because the permit data's unit fields are too incomplete to do otherwise. Under the alternative reading, structure-level churn in single-unit neighborhoods is compatible with unit-level growth that this dataset cannot measure. The pairing and zoning findings hold under either reading; the size of neighborhood housing change does not.

For Sun Valley and Civic Center, the measured fact is clearance without residential construction permits in the window. One reading is that these demolitions are the front end of redevelopment whose construction will be permitted after the window closes or through channels outside the residential permit classes. The alternative reading is removal without replacement on any visible timeline. Permit data through October 2026 cannot distinguish the two; a refresh of this dataset in a later permit period can.

## Who can act

- **Denver Community Planning and Development (permitting and Blueprint Denver monitoring).** The lever: publish net change - new buildings minus demolitions - by neighborhood and by growth area alongside the gross permit totals the city already reports. The linkage this brief used (permit class, address, issue date) is already in the city's own Accela records, so this is a reporting change, not new data collection. The measurable outcome: whether net figures, and the growth-area share of net, appear in the next reporting cycle and permit period.
- **Denver City Council.** The lever: when demolition-related measures are debated (demolition review, deconstruction or replacement requirements), the decision-relevant baselines are the 60.0 percent same-address replacement rate and the 56.1 percent single-unit-zoning share of demolitions, both measured here from the city's data. Any such proposal can be scored against whether those rates move in the following permit periods.
- **Denver Department of Housing Stability.** The lever: the net-negative neighborhood list (11 neighborhoods, 5 with gross activity above 30 permits) is a measurable watch list. The outcome that would show the list mattered: whether Sun Valley and Civic Center record residential construction permits in the next period, closing the gap this brief measured.

## Methods and caveats, short version

- Structures, not units, throughout (see "What we used"). Unit-level net change cannot be computed from this data, and no figure here should be quoted as homes or housing units.
- A permit issued is not a building finished, on either side of the ledger. Cancelled permits are excluded; projects that later stall are not observable.
- This brief covers residential construction permits, the same scope as the October 11 brief. Construction permitted through the commercial service is out of scope, as it was there.
- Address pairing is a floor (window edges, address-format variation) and a street-address match, not a parcel match.
- Demolitions may be understated by at most 13 records (0.3 percent) held in the residential service.
- 0.5 percent of records in each dataset could not be matched to a neighborhood or zoning polygon; neighborhood counts are of matched records.
- Full methods checklist, the layering admission test, and the independent verification ledger are in verification.md and sources.md in this repository. Nothing here is a finding about any individual property owner; demolitions and permits are counted, never named.
