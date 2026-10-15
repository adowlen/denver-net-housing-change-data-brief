"""Independent verification pass for the net housing change brief.

Written separately from analyze.py on purpose:
- counts come from plain JSON parsing of the saved geojson extracts (no
  geopandas), plus live REST returnCountOnly queries against the services;
- neighborhood cross-check uses the services' own NEIGHBORHOOD field instead
  of analyze.py's spatial join;
- spatial splits are recomputed with a polygon-side sjoin ('contains');
- address pairing is recomputed with a different normalizer;
- brief #1 reconciliation recomputes brief #1's numbers from ITS saved
  extract with ITS class map.
Outputs verification_results.json and prints the ledger.
"""
import json
import os
import re
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(HERE, "..")
DATA = os.path.join(PKG, "data")
BASE = "https://services1.arcgis.com/zdB7qR0BtYrg0Xpl/arcgis/rest/services"
LEDGER = []


def rec(name, expected, got, note=""):
    ok = expected == got
    LEDGER.append({"figure": name, "expected": expected, "recomputed": got,
                   "status": "REPRODUCED" if ok else "DISCREPANCY", "note": note})


def load_props(path):
    fc = json.load(open(path))
    return [f["properties"] for f in fc["features"]]


def denver_date(ms):
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).astimezone(
        __import__("zoneinfo").ZoneInfo("America/Denver")).date()


def norm_cls(s):
    if not isinstance(s, str):
        return ""
    # class labels appear as 'WRECK', '6 - WRECK' and '6-Wreck' across years
    return re.sub(r"^\d+\s*-\s*", "", s.strip().upper())


def rest_count(service, where):
    q = urllib.parse.urlencode({"where": where, "returnCountOnly": "true", "f": "json"})
    with urllib.request.urlopen(f"{BASE}/{service}/query?{q}", timeout=120) as r:
        return json.load(r)["count"]


def main():
    stats = json.load(open(os.path.join(PKG, "stats.json")))
    perm = load_props(os.path.join(DATA, "permits_2020.geojson"))
    demo = load_props(os.path.join(DATA, "demolitions_2020.geojson"))

    # ---- raw counts from saved extracts (plain JSON path) ----
    rec("permits rows in extract", stats["permits_pulled_in_window"], len(perm))
    rec("demo service rows in extract", stats["demo_service_rows_in_window"], len(demo))

    perm_active = [p for p in perm if p["CANCEL"] is None]
    rec("permits active (not cancelled)", stats["permits_active"], len(perm_active))
    rec("permits cancelled", stats["permits_cancelled"], len(perm) - len(perm_active))

    nb = [p for p in perm_active if norm_cls(p["CLASS"]) == "NEW BUILDING"]
    rec("new-building permits, active", stats["new_building_active"], len(nb))
    phased = [p for p in perm_active if norm_cls(p["CLASS"]) == "PHASED CONSTRUCTION"]
    rec("phased permits, active", stats["phased_active"], len(phased))

    wreck = [d for d in demo if norm_cls(d["CLASS"]) == "WRECK"]
    rec("demolition-service WRECK rows", stats["demo_wreck_rows"], len(wreck))
    wreck_active = [d for d in wreck if d["CANCEL"] is None]
    rec("demolitions, active", stats["demolitions_active"], len(wreck_active))
    rec("non-wreck line items excluded", stats["demo_service_nonwreck_line_items_excluded"],
        len(demo) - len(wreck))

    rec("net structures", stats["net_structures"], len(nb) - len(wreck_active))
    rec("net incl. phased", stats["net_with_phased"], len(nb) + len(phased) - len(wreck_active))
    rec("gross activity", stats["gross_activity"], len(nb) + len(wreck_active))

    # ---- live REST counts (independent of the saved extracts) ----
    w = "DATE_ISSUED >= TIMESTAMP '2020-01-01 00:00:00'"
    rec("REST: permits in window", len(perm),
        rest_count("ODC_DEV_RESIDENTIALCONSTPERMIT_P/FeatureServer/316", w))
    rec("REST: demo rows in window", len(demo),
        rest_count("ODC_DEV_DEMOLITIONPERMIT_P/FeatureServer/318", w))
    wreck_variants = ("CLASS IN ('WRECK','Wreck','6 - WRECK','6 - Wreck','6-Wreck')")
    rec("REST: demo WRECK rows", len(wreck),
        rest_count("ODC_DEV_DEMOLITIONPERMIT_P/FeatureServer/318", f"{w} AND {wreck_variants}"))
    nb_variants = ("CLASS IN ('NEW BUILDING','New Building','1 - NEW BUILDING','1 - New Building')")
    rec("REST: new-building rows (incl. cancelled)", len([p for p in perm if norm_cls(p['CLASS']) == 'NEW BUILDING']),
        rest_count("ODC_DEV_RESIDENTIALCONSTPERMIT_P/FeatureServer/316", f"{w} AND {nb_variants}"))
    rec("REST: commercial-service WRECK rows", 0,
        rest_count("ODC_DEV_COMMERCIALCONSTPERMIT_P/FeatureServer/317", f"{w} AND UPPER(CLASS) LIKE '%WRECK%'"))

    # ---- window discipline ----
    dates = [denver_date(p["DATE_ISSUED"]) for p in perm] + [denver_date(d["DATE_ISSUED"]) for d in demo]
    rec("earliest issue date (Denver)", "2020-01-01", str(min(dates)))
    rec("latest issue date (Denver)", "2026-10-12", str(max(dates)))

    # ---- by-year recompute ----
    def by_year(rows):
        c = Counter(denver_date(r["DATE_ISSUED"]).year for r in rows)
        return {str(y): c[y] for y in range(2020, 2027)}
    nby, dby = by_year(nb), by_year(wreck_active)
    for y in range(2020, 2027):
        rec(f"new buildings {y}", stats["by_year"][str(y)]["new_building"], nby[str(y)])
        rec(f"demolitions {y}", stats["by_year"][str(y)]["demolitions"], dby[str(y)])
        rec(f"net {y}", stats["by_year"][str(y)]["net"], nby[str(y)] - dby[str(y)])

    # ---- UNITS coverage recompute ----
    def units(rows):
        vals = []
        for r in rows:
            try:
                vals.append(float(r["UNITS"]))
            except (TypeError, ValueError):
                pass
        return len(vals), int(sum(vals))
    n_cnt, n_sum = units(nb)
    d_cnt, d_sum = units(wreck_active)
    rec("NB units numeric coverage", stats["units_new_building"]["units_numeric"], n_cnt)
    rec("NB units reported sum", stats["units_new_building"]["units_reported_sum"], n_sum)
    rec("demo units numeric coverage", stats["units_demolitions"]["units_numeric"], d_cnt)
    rec("demo units reported sum", stats["units_demolitions"]["units_reported_sum"], d_sum)

    # ---- neighborhood cross-check via the services' NEIGHBORHOOD field ----
    table = {r["neighborhood"]: r for r in
             __import__("csv").DictReader(open(os.path.join(DATA, "neighborhood_net.csv")))}
    nb_field = Counter(p["NEIGHBORHOOD"] for p in nb if p["NEIGHBORHOOD"])
    demo_field = Counter(d["NEIGHBORHOOD"] for d in wreck_active if d["NEIGHBORHOOD"])
    top_names = ["Central Park", "Gateway - Green Valley Ranch", "DIA", "West Colfax",
                 "Berkeley", "Sunnyside", "Washington Park", "Sun Valley", "Civic Center", "Globeville"]
    for name in top_names:
        rec(f"NB in {name} (field-based)", int(table[name]["new_building"]), nb_field.get(name, 0),
            note="spatial join vs NEIGHBORHOOD field; small gaps expected from join misses")
        rec(f"demos in {name} (field-based)", int(table[name]["demolitions"]), demo_field.get(name, 0),
            note="spatial join vs NEIGHBORHOOD field")

    # ---- spatial splits recomputed with polygon-side sjoin ----
    import geopandas as gpd
    import pandas as pd
    for fname, rows, key_in, key_pct in [
        ("permits_2020.geojson", None, None, None)]:
        pass
    perm_g = gpd.read_file(os.path.join(DATA, "permits_2020.geojson"))
    demo_g = gpd.read_file(os.path.join(DATA, "demolitions_2020.geojson"))
    for df in (perm_g, demo_g):
        df["date"] = pd.to_datetime(df["DATE_ISSUED"], unit="ms", utc=True).dt.tz_convert("America/Denver").dt.tz_localize(None).dt.normalize()
        df["cls"] = df["CLASS"].map(norm_cls)
    perm_g = perm_g[(perm_g["date"] >= "2020-01-01") & (perm_g["date"] <= "2026-10-12") & perm_g["CANCEL"].isna()]
    demo_g = demo_g[(demo_g["date"] >= "2020-01-01") & (demo_g["date"] <= "2026-10-12") & demo_g["CANCEL"].isna() & (demo_g["cls"] == "WRECK")]
    nb_g = perm_g[perm_g["cls"] == "NEW BUILDING"]
    bp = gpd.read_file(os.path.join(DATA, "bp_growth_areas.geojson"))
    zoning = gpd.read_file(os.path.join(DATA, "zoning.geojson"))

    def inside_count(points, polys):
        j = gpd.sjoin(polys[["geometry"]], points[["geometry"]], how="inner", predicate="contains")
        return j.index_right.nunique() if len(j) else 0

    rec("new buildings inside growth areas", stats["new_building_in_growth"], inside_count(nb_g, bp))
    rec("demolitions inside growth areas", stats["demolitions_in_growth"], inside_count(demo_g, bp))
    su = zoning[zoning["ZONE_USE_FORM"] == "SU"]
    rec("new buildings in SU zoning", stats["new_building_in_su_zoning"], inside_count(nb_g, su))
    rec("demolitions in SU zoning", stats["demolitions_in_su_zoning"], inside_count(demo_g, su))

    # ---- address pairing, different normalizer ----
    def base2(addr):
        if not addr:
            return None
        s = " ".join(str(addr).upper().replace(",", " ").split())
        toks = s.split()
        types = {"ST", "AVE", "AV", "BLVD", "DR", "CT", "PL", "LN", "WAY", "RD", "CIR", "PKWY", "HWY", "SQ", "TER", "TRL", "ALY", "ROW"}
        for i, tk in enumerate(toks):
            if tk in types and i >= 1:
                return " ".join(toks[: i + 1])
        return s

    nb_addr = {base2(p["ADDRESS"]) for p in nb} - {None}
    demo_addr = {base2(d["ADDRESS"]) for d in wreck_active} - {None}
    d_share = sum(1 for d in wreck_active if base2(d["ADDRESS"]) in nb_addr) / len(wreck_active)
    rec("pairing: demo share at NB address (pct, rounded)",
        stats["pairing_addr_base_demo_share_pct"], round(100 * d_share, 1))

    # ---- brief #1 reconciliation from brief #1's own extract ----
    # Brief #1's pipeline dropped features with null/empty geometry BEFORE
    # counting; replicate that here, and also report the un-dropped counts.
    b1_fc = json.load(open("/home/hatch/workspace/denver-housing-permits/data/permits_2020.geojson"))
    b1_all = [f["properties"] for f in b1_fc["features"]]
    b1_geo = [f["properties"] for f in b1_fc["features"] if f.get("geometry")]
    LEDGER.append({"figure": "brief #1 extract: rows without geometry", "expected": None,
                   "recomputed": len(b1_all) - len(b1_geo), "status": "INFO", "note": ""})
    b1_active = [p for p in b1_geo if p["CANCEL"] is None]
    rec("brief #1 active permits (its extract, geometry-dropped as in brief #1)", 30902, len(b1_active))
    b1_nb = [p for p in b1_active if norm_cls(p["CLASS"]) == "NEW BUILDING"]
    rec("brief #1 new buildings (its extract, geometry-dropped as in brief #1)", 11559, len(b1_nb))
    fresh_le_oct11 = [p for p in nb if denver_date(p["DATE_ISSUED"]) <= __import__("datetime").date(2026, 10, 11)]
    LEDGER.append({"figure": "fresh-pull NB issued on/before 2026-10-11", "expected": 11559,
                   "recomputed": len(fresh_le_oct11),
                   "status": "RECONCILIATION" if len(fresh_le_oct11) >= 11559 else "DISCREPANCY",
                   "note": "delta vs brief #1 = permits issued Oct 12 in the later pull plus any Accela backfills/revisions"})

    out = {"ledger": LEDGER}
    with open(os.path.join(PKG, "verification_results.json"), "w") as f:
        json.dump(out, f, indent=2)
    n_ok = sum(1 for e in LEDGER if e["status"] == "REPRODUCED")
    print(f"{n_ok}/{len(LEDGER)} REPRODUCED")
    for e in LEDGER:
        if e["status"] != "REPRODUCED":
            print(e)


if __name__ == "__main__":
    main()
