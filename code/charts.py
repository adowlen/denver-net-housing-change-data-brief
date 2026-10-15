"""Charts for the Denver net housing change brief - Machine Readable brand palette.

Every figure is drawn from stats.json / data/neighborhood_net.csv (produced by
analyze.py) and carries its scope and source on the graphic. Text uses plain
hyphens only. Data charts only; the hero is a generated illustration.
"""
import json
import os

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd

CHARCOAL = "#101417"
PANEL = "#171D21"
AMBER = "#F5A800"
TEAL = "#19B8A6"
PAPER = "#F2EFE9"
TEXT_DIM = "#9AA5AB"
GRID = "#2C343A"

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(HERE, "..")
OUT = os.path.join(PKG, "charts")
DATA = os.path.join(PKG, "data")
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    "figure.facecolor": CHARCOAL,
    "axes.facecolor": CHARCOAL,
    "axes.edgecolor": GRID,
    "axes.labelcolor": PAPER,
    "text.color": PAPER,
    "xtick.color": TEXT_DIM,
    "ytick.color": TEXT_DIM,
    "grid.color": GRID,
    "grid.alpha": 0.5,
    "font.size": 11,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.titlecolor": PAPER,
})

s = json.load(open(os.path.join(PKG, "stats.json")))
t = pd.read_csv(os.path.join(DATA, "neighborhood_net.csv"))
SRC = "Source: City and County of Denver open data (residential construction + demolition permits), issued 2020-01-01 to 2026-10-12."


def footnote(fig, text=SRC):
    fig.text(0.012, 0.012, text, fontsize=8.5, color=TEXT_DIM, va="bottom")


def save(fig, name, rect_bottom=0.05):
    fig.tight_layout(rect=[0, rect_bottom, 1, 1])
    fig.savefig(os.path.join(OUT, name), dpi=150, facecolor=CHARCOAL)
    plt.close(fig)
    print("saved", name)


# 1. Choropleth: net change by neighborhood
nbhd = gpd.read_file(os.path.join(DATA, "neighborhoods.geojson"))
m = nbhd.merge(t, left_on="NBHD_NAME", right_on="neighborhood", how="left")
fig, ax = plt.subplots(figsize=(10.5, 9.5))
cmap = mcolors.LinearSegmentedColormap.from_list("net", [AMBER, "#3A3F35", TEAL])
norm = mcolors.TwoSlopeNorm(vmin=-80, vcenter=0, vmax=1100)
m.plot(column="net", ax=ax, cmap=cmap, norm=norm, edgecolor="#0B0E10", linewidth=0.4,
       legend=True, legend_kwds={"label": "Net structures (new-building permits minus demolition permits)"},
       missing_kwds={"color": "#23282C", "label": "No recorded activity"})
ax.set_title("Net housing change by Denver neighborhood, 2020-2026\n(new residential buildings permitted minus structures demolished)")
ax.set_axis_off()
footnote(fig)
save(fig, "net_change_map.png", rect_bottom=0.03)

# 2. Top gainers / largest net losses
top = t.head(10).iloc[::-1]
bot = t.tail(10)
fig, axes = plt.subplots(1, 2, figsize=(13.5, 6))
axes[0].barh(top["neighborhood"], top["net"], color=TEAL)
axes[0].set_title("Largest net gains (structures)")
for i, r in enumerate(top.itertuples()):
    axes[0].text(r.net + 22, i, f"+{r.net:,}  ({r.new_building:,} new, {r.demolitions:,} demolished)",
                 va="center", fontsize=9, color=PAPER)
axes[0].set_xlim(0, 1500)
axes[0].tick_params(labelsize=9)
bot_r = bot.iloc[::-1]
axes[1].barh(bot_r["neighborhood"], bot_r["net"], color=AMBER)
axes[1].set_title("Largest net losses (structures)")
for i, r in enumerate(bot_r.itertuples()):
    axes[1].text(r.net - 3, i, f"{r.net:,}  ({r.new_building:,} new, {r.demolitions:,} demolished)",
                 va="center", fontsize=9, color=PAPER, ha="right")
axes[1].set_xlim(-215, 5)
axes[1].tick_params(labelsize=9)
fig.suptitle("Net change leaders and laggards, 2020-2026", fontsize=14, fontweight="bold", color=PAPER)
footnote(fig)
save(fig, "net_gainers_losers.png", rect_bottom=0.06)

# 3. Yearly: new buildings vs demolitions, net line
yrs = pd.DataFrame(s["by_year"]).T
years = [int(y) for y in yrs.index]
x = range(len(years))
fig, ax = plt.subplots(figsize=(11, 5.5))
w = 0.38
ax.bar([i - w / 2 for i in x], yrs["new_building"], width=w, color=TEAL, label="New-building permits")
ax.bar([i + w / 2 for i in x], yrs["demolitions"], width=w, color=AMBER, label="Demolition permits")
ax.plot(x, yrs["net"], color=PAPER, marker="o", lw=2, label="Net structures")
for i, r in enumerate(yrs.itertuples()):
    ax.text(i, r.net + 90, f"+{r.net:,}", ha="center", fontsize=9.5, color=PAPER)
ax.set_xticks(list(x))
ax.set_xticklabels([f"{y}" + (" (partial,\nto Oct 12)" if y == 2026 else "") for y in years], fontsize=9.5)
ax.set_ylabel("permits issued")
ax.set_title("Denver adds more than it removes every year - but the margin narrowed after 2021")
ax.legend(fontsize=9.5, frameon=False)
ax.grid(axis="y")
footnote(fig)
save(fig, "yearly_net.png")

# 4. Churn scatter: gross activity vs demolition share
big = t[t["gross"] >= 30].copy()
fig, ax = plt.subplots(figsize=(11, 6.5))
colors = [TEAL if n >= 0 else AMBER for n in big["net"]]
ax.scatter(big["gross"], big["churn_pct"], s=big["gross"] * 1.1, c=colors, alpha=0.8, edgecolor="none")
ax.axhline(s["churn_citywide_pct"], color=PAPER, ls="--", lw=1)
ax.text(big["gross"].max() * 0.99, s["churn_citywide_pct"] + 1.2,
        f"citywide: {s['churn_citywide_pct']}% of activity is demolition", ha="right", fontsize=9.5, color=PAPER)
OFFSETS = {"Civic Center": (-4, -16), "Sun Valley": (10, 4)}
for name in ["Sun Valley", "Civic Center", "Capitol Hill", "Globeville", "Hilltop", "Belcaro",
             "Washington Park", "Berkeley", "Central Park", "Elyria Swansea"]:
    r = big[big["neighborhood"] == name]
    if len(r):
        r = r.iloc[0]
        ax.annotate(name, (r["gross"], r["churn_pct"]), fontsize=9, color=PAPER,
                    xytext=OFFSETS.get(name, (6, 5)), textcoords="offset points")
ax.set_xlabel("Gross permit activity (new buildings + demolitions), 2020-2026")
ax.set_ylabel("Demolitions as % of gross activity")
ax.set_title("Churn: where demolition is a large share of all permit activity\n(neighborhoods with 30+ gross permits; teal = net gain, amber = net loss)")
ax.grid()
footnote(fig)
save(fig, "churn_scatter.png")

# 5. Growth-plan geography: inside vs outside Blueprint Denver growth areas
cats = ["New buildings", "Demolitions", "Net change"]
inside = [s["new_building_in_growth"], s["demolitions_in_growth"], s["net_in_growth"]]
outside = [s["new_building_outside_growth"], s["demolitions_outside_growth"], s["net_outside_growth"]]
fig, ax = plt.subplots(figsize=(11, 5.5))
y = range(len(cats))
ax.barh([i + 0.2 for i in y], inside, height=0.38, color=TEAL, label="Inside Blueprint Denver growth areas")
ax.barh([i - 0.2 for i in y], outside, height=0.38, color=AMBER, label="Outside growth areas")
for i, (a, b) in enumerate(zip(inside, outside)):
    ax.text(a + 130, i + 0.2, f"{a:,}", va="center", fontsize=10, color=PAPER)
    ax.text(b + 130, i - 0.2, f"{b:,}", va="center", fontsize=10, color=PAPER)
ax.set_yticks(list(y))
ax.set_yticklabels(cats)
ax.invert_yaxis()
ax.set_xlim(0, 10200)
ax.set_title("Netting demolitions does not move growth into the plan areas:\n83% of demolitions and 75% of new buildings are outside them")
ax.legend(fontsize=9.5, frameon=False, loc="lower right")
ax.grid(axis="x")
footnote(fig)
save(fig, "growth_geography.png")
print("charts done")
