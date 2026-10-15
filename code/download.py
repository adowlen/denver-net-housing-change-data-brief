"""Download Denver permits + demolition permits for the net-housing-change brief.

Follow-up to brief #1 (denver-housing-permits-data-brief, 2026-10-11).
Same source org (City and County of Denver, ArcGIS Hub zdB7qR0BtYrg0Xpl),
same issue-date window discipline: DATE_ISSUED >= 2020-01-01, pulled fresh
2026-10-14 so both datasets share one snapshot date.

Sources:
- ODC_DEV_RESIDENTIALCONSTPERMIT_P/316  residential construction permits (RESCON)
- ODC_DEV_DEMOLITIONPERMIT_P/318         demolition permits (DEMO)
Boundary/plan layers (neighborhoods, Blueprint growth areas, zoning) are
reused from brief #1's saved extracts in the same workspace data folder
(boundaries and plan geography are stable; see sources.md).
"""
import json
import os
import time
import urllib.parse
import urllib.request

BASE = "https://services1.arcgis.com/zdB7qR0BtYrg0Xpl/arcgis/rest/services"
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")


def fetch_paged(url, where, out_fields, page_size=2000):
    feats = []
    offset = 0
    while True:
        q = {
            "where": where,
            "outFields": out_fields,
            "returnGeometry": "true",
            "outSR": "4326",
            "f": "geojson",
            "resultOffset": offset,
            "resultRecordCount": page_size,
        }
        req_url = url + "/query?" + urllib.parse.urlencode(q)
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req_url, timeout=180) as r:
                    page = json.load(r)
                break
            except Exception:
                if attempt == 3:
                    raise
                time.sleep(2 * (attempt + 1))
        batch = page.get("features", [])
        feats.extend(batch)
        print(f"  offset {offset}: +{len(batch)} (total {len(feats)})", flush=True)
        if len(batch) < page_size:
            break
        offset += page_size
    return {"type": "FeatureCollection", "features": feats}


def save(name, fc):
    path = os.path.join(DATA, f"{name}.geojson")
    with open(path, "w") as f:
        json.dump(fc, f)
    print(f"saved {path}: {len(fc['features'])} features")


def main():
    os.makedirs(DATA, exist_ok=True)
    print("residential construction permits 2020+ ...")
    fc = fetch_paged(
        f"{BASE}/ODC_DEV_RESIDENTIALCONSTPERMIT_P/FeatureServer/316",
        "DATE_ISSUED >= TIMESTAMP '2020-01-01 00:00:00'",
        "OBJECTID,DATE_ISSUED,PERMIT_NUM,ADDRESS,CLASS,UNITS,VALUATION,PERMIT_FEE,"
        "FINAL_DATE,CANCEL,DATE_RECEIVED,NEIGHBORHOOD,STAT_CODE_1,STAT_CODE_2,STAT_CODE_3",
    )
    save("permits_2020", fc)

    print("demolition permits 2020+ ...")
    fc = fetch_paged(
        f"{BASE}/ODC_DEV_DEMOLITIONPERMIT_P/FeatureServer/318",
        "DATE_ISSUED >= TIMESTAMP '2020-01-01 00:00:00'",
        "OBJECTID,DATE_ISSUED,PERMIT_NUM,ADDRESS,LOCATION,CLASS,UNITS,VALUATION,PERMIT_FEE,"
        "FINAL_DATE,CANCEL,DATE_RECEIVED,NEIGHBORHOOD,STAT_CODE_1,STAT_CODE_2,STAT_CODE_3",
    )
    save("demolitions_2020", fc)


if __name__ == "__main__":
    main()
