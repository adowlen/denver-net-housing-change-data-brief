"""Net housing change in Denver: building permits layered with demolitions.

Follow-up to denver-housing-permits-data-brief (2026-10-11). Uses brief #1's
definitions exactly (same CLASS_MAP, cancelled = CANCEL not null, neighborhood
from the same spatial join, Blueprint growth areas from the same layer) so the
two briefs are comparable, and nets the demolition side from the city's
dedicated demolition permit service (DEV_DEMOLITIONPERMIT_P).

Window: permits ISSUED 2020-01-01 through 2026-10-12 (Denver dates). Both
services were pulled 2026-10-14; 2026-10-12 is the latest issue date present
in either extract. 2026 is a partial year.

Measures are STRUCTURES (permit counts), not dwelling units: the UNITS field
is blank on 44% of new-building permits and 59% of demolition permits and is
not a reliable unit count where present (see brief + verification.md).
"""
import json
import os
import re
from collections import Counter

import geopandas as gpd
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(HERE, "..")
DATA = os.path.join(PKG, "data")
PROJ = "EPSG:26913"  # NAD83 / Colorado Central, as brief #1

# Brief #1's class map, copied verbatim so classes mean the same thing.
CLASS_MAP = {
    "NEW BUILDING": "new_building",
    "1 - NEW BUILDING": "new_building",
    "ADDITION": "addition",
    "2 - ADDITION TO BUILDING": "addition",
    "ALTERATION/TENANT FINISH": "alteration",
    "REPAIR/REPLACE": "alteration",
    "PHASED CONSTRUCTION": "phased",
    "FOUNDATION ONLY/EXCAVATION": "site_prep",
    "FOUNDATION ONLY/ EXCAVATION": "site_prep",
    "NEW NON-BUILDING STRUCTURE": "non_building",
    "CHANGE OF CONTRACTOR": "admin",
    "MOVE": "admin",
    "WRECK": "admin",
    "6 - WRECK": "admin",
    "SPECIAL EVENT": "admin",
    "CHANGE OF USE ONLY": "change_of_use",
}

WINDOW_START = pd.Timestamp("2020-01-01")
WINDOW_END = pd.Timestamp("2026-10-12")


def cls_norm(raw):
    """Upper-case, strip the leading 'N - ' class numbering used in some years."""
    s = str(raw).upper().strip()
    return re.sub(r"^\d+\s*-\s*", "", s)


def base_address(addr):
    """Reduce an Accela address string to number + direction + street + type.

    '3314 N FRANKLIN 1/2' -> '3314 N FRANKLIN'; '1515 WYNKOOP ST MECH' ->
    '1515 WYNKOOP ST'. Used only for the same-address pairing analysis;
    match rates under exact and base matching are both reported.
    """
    if not isinstance(addr, str):
        return None
    s = re.sub(r"[^A-Z0-9 ]", " ", addr.upper())
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\s+(ADU|DADU)$", "", s)
    m = re.match(
        r"^(\d+)\s+((?:N|S|E|W|NE|NW|SE|SW)\s+)?(.+?)\s+"
        r"(ST|AVE|AV|BLVD|DR|CT|PL|LN|WAY|RD|CIR|PKWY|HWY|SQ|TER|TRL|ALY|ROW)\b",
        s,
    )
    if m:
        return f"{m.group(1)} {(m.group(2) or '').strip()} {m.group(3)} {m.group(4)}".replace("  ", " ").strip()
    return s


def prep(df):
    df = df.copy()
    df["date"] = (
        pd.to_datetime(df["DATE_ISSUED"], unit="ms", utc=True)
        .dt.tz_convert("America/Denver")
        .dt.tz_localize(None)
        .dt.normalize()
    )
    df = df[(df["date"] >= WINDOW_START) & (df["date"] <= WINDOW_END)].copy()
    df["active"] = df["CANCEL"].isna()
    df["cls"] = df["CLASS"].map(cls_norm).map(
        lambda s: CLASS_MAP.get(s, "other") if isinstance(s, str) else "other"
    )
    return df


def spatial_assign(df_p, polys, name_col, out_col):
    j = gpd.sjoin(df_p, polys[[name_col, "geometry"]], how="left", predicate="within")
    j = j[~j.index.duplicated(keep="first")]
    out = pd.Series(index=df_p.index, dtype=object)
    out.loc[j.index] = j[name_col].values
    return out


def main():
    stats = {"window": {"start": "2020-01-01", "end": "2026-10-12", "pulled": "2026-10-14"}}

    perm = prep(gpd.read_file(os.path.join(DATA, "permits_2020.geojson")))
    demo_raw = gpd.read_file(os.path.join(DATA, "demolitions_2020.geojson"))
    demo_all = prep(demo_raw)
    stats["permits_pulled_in_window"] = int(len(perm))
    stats["permits_active"] = int(perm["active"].sum())
    stats["permits_cancelled"] = int((~perm["active"]).sum())
    stats["demo_service_rows_in_window"] = int(len(demo_all))

    # Demolitions = WRECK class rows of the DEMO-type service. The service also
    # carries non-wreck line items of DEMO applications (trade/alteration rows);
    # those are not demolitions and are excluded and counted here.
    demo = demo_all[demo_all["CLASS"].map(cls_norm) == "WRECK"].copy()
    stats["demo_wreck_rows"] = int(len(demo))
    stats["demo_service_nonwreck_line_items_excluded"] = int(len(demo_all) - len(demo))
    stats["demo_cancelled"] = int((~demo["active"]).sum())
    demo = demo[demo["active"]].copy()
    stats["demolitions_active"] = int(len(demo))

    act = perm[perm["active"]].copy()
    nb = act[act["cls"] == "new_building"].copy()
    phased = act[act["cls"] == "phased"].copy()
    stats["new_building_active"] = int(len(nb))
    stats["phased_active"] = int(len(phased))
    stats["net_structures"] = int(len(nb) - len(demo))
    stats["gross_activity"] = int(len(nb) + len(demo))
    stats["churn_citywide_pct"] = round(100 * len(demo) / (len(nb) + len(demo)), 1)
    stats["demos_per_100_new"] = round(100 * len(demo) / len(nb), 1)
    stats["net_with_phased"] = int(len(nb) + len(phased) - len(demo))

    # Reconciliation with brief #1 (pulled 2026-10-11, window 2020-01-01 onward)
    stats["brief1_active_permits"] = 30902
    stats["brief1_new_building"] = 11559

    # ---- UNITS coverage (the units-vs-permits trap), reported not used ----
    def units_stats(df):
        raw = df["UNITS"]
        num = pd.to_numeric(raw, errors="coerce")
        return {
            "rows": int(len(df)),
            "units_field_nonnull": int(raw.notna().sum()),
            "units_numeric": int(num.notna().sum()),
            "units_coverage_pct": round(100 * num.notna().mean(), 1) if len(df) else None,
            "units_reported_sum": int(num.sum()),
            "units_gt1": int((num > 1).sum()),
            "units_eq1": int((num == 1).sum()),
            "units_max": float(num.max()) if num.notna().any() else None,
        }

    stats["units_new_building"] = units_stats(nb)
    stats["units_demolitions"] = units_stats(demo)

    # ---- spatial joins (same layers + method as brief #1) ----
    nbhd = gpd.read_file(os.path.join(DATA, "neighborhoods.geojson")).to_crs(PROJ)
    bp = gpd.read_file(os.path.join(DATA, "bp_growth_areas.geojson")).to_crs(PROJ)
    zoning = gpd.read_file(os.path.join(DATA, "zoning.geojson")).to_crs(PROJ)

    for label, df in [("nb", nb), ("phased", phased), ("demo", demo)]:
        df_p = df.to_crs(PROJ)
        df["nbhd_spatial"] = spatial_assign(df_p, nbhd, "NBHD_NAME", "nbhd")
        j = gpd.sjoin(df_p, bp[["GROWTH_FUTURE", "geometry"]], how="left", predicate="within")
        j = j[~j.index.duplicated(keep="first")]
        df["in_growth_area"] = False
        m = j["GROWTH_FUTURE"].notna()
        df.loc[j.index[m], "in_growth_area"] = True
        df["zone_use_form"] = spatial_assign(df_p, zoning, "ZONE_USE_FORM", "zuf")
        df["zone_district"] = spatial_assign(df_p, zoning, "ZONE_DISTRICT", "zd")
        stats[f"{label}_neighborhood_match_pct"] = round(100 * df["nbhd_spatial"].notna().mean(), 1)
        stats[f"{label}_zoning_match_pct"] = round(100 * df["zone_district"].notna().mean(), 1)

    # NEIGHBORHOOD field vs spatial join agreement, demolitions
    both = demo["nbhd_spatial"].notna() & demo["NEIGHBORHOOD"].notna()
    stats["demo_nbhd_field_vs_spatial_agreement_pct"] = round(
        100 * (demo.loc[both, "nbhd_spatial"] == demo.loc[both, "NEIGHBORHOOD"]).mean(), 1
    )
    stats["demo_nbhd_field_missing"] = int(demo["NEIGHBORHOOD"].isna().sum())

    # ---- growth-plan geography ----
    for label, df in [("new_building", nb), ("demolitions", demo)]:
        inn = int(df["in_growth_area"].sum())
        stats[f"{label}_in_growth"] = inn
        stats[f"{label}_outside_growth"] = int(len(df) - inn)
        stats[f"{label}_in_growth_pct"] = round(100 * inn / len(df), 1)
    stats["net_in_growth"] = int(nb["in_growth_area"].sum() - demo["in_growth_area"].sum())
    stats["net_outside_growth"] = int(
        (len(nb) - nb["in_growth_area"].sum()) - (len(demo) - demo["in_growth_area"].sum())
    )

    # ---- zoning of sites ----
    for label, df in [("new_building", nb), ("demolitions", demo)]:
        su = df["zone_use_form"] == "SU"
        stats[f"{label}_in_su_zoning"] = int(su.sum())
        stats[f"{label}_in_su_zoning_pct_of_matched"] = round(
            100 * su.sum() / df["zone_use_form"].notna().sum(), 1
        )

    # ---- yearly series (2026 partial, through Oct 12) ----
    yrs = {}
    for y in range(2020, 2027):
        n_y = int((nb["date"].dt.year == y).sum())
        d_y = int((demo["date"].dt.year == y).sum())
        yrs[str(y)] = {"new_building": n_y, "demolitions": d_y, "net": n_y - d_y}
    stats["by_year"] = yrs
    pd.DataFrame(yrs).T.to_csv(os.path.join(DATA, "yearly_net.csv"))

    # ---- neighborhood aggregates ----
    def agg(df, col):
        return df.groupby("nbhd_spatial").size().rename(col)

    table = pd.concat(
        [agg(nb, "new_building"), agg(phased, "phased"), agg(demo, "demolitions")], axis=1
    ).fillna(0)
    table = table.reset_index().rename(columns={"nbhd_spatial": "neighborhood"})
    for c in ["new_building", "phased", "demolitions"]:
        table[c] = table[c].astype(int)
    table["net"] = table["new_building"] - table["demolitions"]
    table["gross"] = table["new_building"] + table["demolitions"]
    table["churn_pct"] = (100 * table["demolitions"] / table["gross"]).round(1)
    table["small_counts_flag"] = table["gross"] < 30
    table = table.sort_values("net", ascending=False)
    table.to_csv(os.path.join(DATA, "neighborhood_net.csv"), index=False)

    big = table[~table["small_counts_flag"]]
    stats["neighborhoods_with_activity"] = int((table["gross"] > 0).sum())
    stats["neighborhoods_negative_net"] = int((table["net"] < 0).sum())
    stats["neighborhoods_negative_net_list"] = table.loc[table["net"] < 0, "neighborhood"].tolist()
    stats["top10_net_gainers"] = [
        {"neighborhood": r.neighborhood, "net": int(r.net), "new_building": int(r.new_building),
         "demolitions": int(r.demolitions)}
        for r in table.head(10).itertuples()
    ]
    stats["bottom10_net"] = [
        {"neighborhood": r.neighborhood, "net": int(r.net), "new_building": int(r.new_building),
         "demolitions": int(r.demolitions), "gross": int(r.gross)}
        for r in table.tail(10).itertuples()
    ]
    churn_sorted = big.sort_values("churn_pct", ascending=False)
    stats["top10_churn_gross30plus"] = [
        {"neighborhood": r.neighborhood, "churn_pct": float(r.churn_pct), "gross": int(r.gross),
         "new_building": int(r.new_building), "demolitions": int(r.demolitions), "net": int(r.net)}
        for r in churn_sorted.head(10).itertuples()
    ]
    stats["neighborhoods_majority_demolition"] = [
        {"neighborhood": r.neighborhood, "churn_pct": float(r.churn_pct), "gross": int(r.gross), "net": int(r.net)}
        for r in big[churn_sorted["churn_pct"] >= 50].itertuples()
    ] if False else [
        {"neighborhood": r.neighborhood, "churn_pct": float(r.churn_pct), "gross": int(r.gross), "net": int(r.net)}
        for r in big[big["churn_pct"] >= 50].itertuples()
    ]

    # ---- same-address pairing (teardown -> rebuild on the same address) ----
    nb_b = nb.copy(); demo_b = demo.copy()
    nb_b["addr_exact"] = nb_b["ADDRESS"].fillna("").str.upper().str.strip()
    demo_b["addr_exact"] = demo_b["ADDRESS"].fillna("").str.upper().str.strip()
    nb_b["addr_base"] = nb_b["ADDRESS"].map(base_address)
    demo_b["addr_base"] = demo_b["ADDRESS"].map(base_address)

    for key in ["addr_exact", "addr_base"]:
        nb_addrs = set(nb_b[key].dropna()) - {""}
        demo_addrs = set(demo_b[key].dropna()) - {""}
        stats[f"pairing_{key}_demo_share_pct"] = round(
            100 * demo_b[key].isin(nb_addrs).mean(), 1
        )
        stats[f"pairing_{key}_nb_share_pct"] = round(
            100 * nb_b[key].isin(demo_addrs).mean(), 1
        )

    # timing on base-address matches
    nb_by_addr = nb_b.dropna(subset=["addr_base"]).groupby("addr_base")["date"].agg(["min", "max"])
    demo_b["nb_min"] = demo_b["addr_base"].map(nb_by_addr["min"])
    demo_b["nb_max"] = demo_b["addr_base"].map(nb_by_addr["max"])
    matched = demo_b[demo_b["nb_min"].notna()].copy()
    stats["pairing_demos_with_nb_same_address"] = int(len(matched))
    stats["pairing_demo_before_or_same_nb_pct"] = round(
        100 * (matched["nb_max"] >= matched["date"]).mean(), 1
    )
    after = matched[matched["nb_min"] >= matched["date"]]
    lags = (after["nb_min"] - after["date"]).dt.days
    stats["pairing_median_days_demo_to_first_later_nb"] = (
        int(lags.median()) if len(lags) else None
    )
    stats["pairing_demo_with_later_nb_count"] = int(len(after))

    # demolition valuations + permit counts by class for context
    stats["demo_valuation_median"] = float(demo["VALUATION"].median())
    stats["class_style_by_year_note"] = dict(
        Counter(
            (demo_raw["DATE_ISSUED"].notna()).astype(int)  # placeholder, filled in verification
        )
    )
    stats.pop("class_style_by_year_note")

    with open(os.path.join(PKG, "stats.json"), "w") as f:
        json.dump(stats, f, indent=2, default=str)
    print(json.dumps(stats, indent=2, default=str))

    # enriched extracts for the record
    keep = ["PERMIT_NUM", "ADDRESS", "NEIGHBORHOOD", "nbhd_spatial", "date", "CLASS",
            "UNITS", "VALUATION", "in_growth_area", "zone_use_form", "zone_district"]
    for label, df in [("new_building", nb), ("demolitions", demo)]:
        out = df[keep].copy()
        out["date"] = out["date"].dt.strftime("%Y-%m-%d")
        out.to_csv(os.path.join(DATA, f"{label}_enriched.csv"), index=False)
        print("wrote", label, len(out))


if __name__ == "__main__":
    main()
