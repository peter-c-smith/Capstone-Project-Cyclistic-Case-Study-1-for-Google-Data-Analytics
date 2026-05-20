"""
generate_notebook.py
--------------------
Generates cyclistic_analysis.ipynb — the pandas analysis Jupyter notebook
for the Cyclistic portfolio capstone.

Run once to produce the notebook:
    python generate_notebook.py

Then open the notebook in Jupyter:
    jupyter notebook cyclistic_analysis.ipynb

The notebook mirrors the 12 analysis scripts but adds:
  - Narrative markdown commentary
  - matplotlib charts (inline + saved as PNGs to ../../Visuals/Python/)
  - A casual rider segmentation section (Script 13 insight from Polars module)
  - A key findings summary at the end

Charts are saved as high-resolution PNGs alongside inline display so they
can be embedded in the final portfolio README and presentations.
"""

import nbformat as nbf
from pathlib import Path

OUTPUT_NB   = Path(__file__).parent / "cyclistic_analysis.ipynb"
nb = nbf.v4.new_notebook()
nb.metadata["kernelspec"] = {
    "display_name": "Python 3",
    "language": "python",
    "name": "python3"
}
cells = []

# ---------------------------------------------------------------------------
# Helper shortcuts
# ---------------------------------------------------------------------------
md   = nbf.v4.new_markdown_cell
code = nbf.v4.new_code_cell

# ===========================================================================
# TITLE & INTRODUCTION
# ===========================================================================
cells.append(md("""# Cyclistic Bike-Share Analysis — pandas Module

**Google Data Analytics Certificate Capstone**
Tool: Python 3.13 · pandas 2.3 · matplotlib · NumPy
Dataset: 5,620,544 rides · Apr 2025 – Mar 2026 · Divvy (Chicago)

---

## Objective

Cyclistic wants to convert casual riders into annual members.
This notebook explores **who rides, how, when, and where** — and quantifies
the revenue opportunity if even a fraction of casual riders convert.

All metrics in this notebook are cross-validated against SQL Server, DuckDB, and R
to confirm consistency across tools.

---

## Contents

1. Setup — load data
2. Who rides? — member vs casual split
3. How long and how far? — duration & distance
4. When do they ride? — hourly distribution
5. Weekend vs weekday
6. Seasonal patterns
7. Bike type mix
8. Where do they start? — top stations
9. The conversion opportunity — revenue proxy
10. Fleet utilization — peak concurrent rides
11. Casual rider segmentation — who to target
12. Key findings summary
"""))

# ===========================================================================
# SETUP
# ===========================================================================
cells.append(md("""---
## 1. Setup

Load all 12 monthly CSV files into a single DataFrame using the shared `utils.py` loader.
This is the same load used by all 12 analysis scripts — one function, consistent results.
"""))

cells.append(code("""\
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path

from utils import load_trips

# Chart output folder — relative to this notebook
VISUALS_DIR = Path.cwd().parent.parent / "Visuals" / "Python"

# Matplotlib defaults — clean, professional style
plt.rcParams.update({
    "figure.dpi":        150,
    "figure.facecolor":  "white",
    "axes.facecolor":    "#f8f9fa",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.grid":         True,
    "axes.axisbelow":    True,
    "grid.color":        "white",
    "grid.linewidth":    1.2,
    "font.family":       "sans-serif",
    "axes.titlesize":    13,
    "axes.labelsize":    11,
})

MEMBER_COLOR = "#2196F3"   # blue  — members
CASUAL_COLOR = "#FF9800"   # amber — casuals

def save_fig(name: str) -> None:
    \"\"\"Save current figure to Visuals/Python/ as a high-res PNG.\"\"\"
    VISUALS_DIR.mkdir(parents=True, exist_ok=True)
    path = VISUALS_DIR / f"{name}.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    print(f"  Saved → {path.relative_to(path.parents[3])}")

print("Loading 5.6M rides...")
trips = load_trips()
print(f"Loaded: {len(trips):,} rows × {len(trips.columns)} columns")
"""))

# ===========================================================================
# SECTION 2: WHO RIDES
# ===========================================================================
cells.append(md("""---
## 2. Who Rides? — Member vs Casual Split

The most fundamental question: what proportion of rides come from annual members
vs casual (pay-per-ride) users?

Members account for **64.1%** of all rides. Casuals at **35.9%** represent a
large addressable conversion pool — over 2 million rides from people already
engaged with the product but paying the higher per-ride rate.
"""))

cells.append(code("""\
counts = trips["member_casual"].value_counts()
total  = len(trips)

print("=" * 45)
print("  Ride Counts by Rider Type")
print("=" * 45)
for rtype, n in counts.items():
    print(f"  {rtype:<10}  {n:>10,}  ({n/total*100:.1f}%)")
print(f"  {'Total':<10}  {total:>10,}")

# --- Chart ---
fig, ax = plt.subplots(figsize=(5, 5))
colors = [MEMBER_COLOR, CASUAL_COLOR]
wedges, texts, autotexts = ax.pie(
    counts.values,
    labels=counts.index.str.capitalize(),
    autopct="%1.1f%%",
    colors=colors,
    startangle=90,
    pctdistance=0.75,
    wedgeprops={"linewidth": 2, "edgecolor": "white"}
)
for at in autotexts:
    at.set_fontsize(13)
    at.set_fontweight("bold")
    at.set_color("white")
ax.set_title("Ride Share by Rider Type\\n(Apr 2025 – Mar 2026)", pad=15)
plt.tight_layout()
save_fig("01_rider_split")
plt.show()
"""))

# ===========================================================================
# SECTION 3: DURATION & DISTANCE
# ===========================================================================
cells.append(md("""---
## 3. How Long and How Far? — Duration & Distance

Casual riders take rides that are **1.82× longer** in duration than members,
but travel only **1.03× farther** in distance. This tells a clear story:

- **Members** ride efficiently — short, purposeful, point-to-point (commuting).
- **Casuals** ride leisurely — longer time in the saddle but not going much farther
  (touring, exploring, recreational loops).

The duration gap is the stronger signal. It reflects fundamentally different
intent between the two groups.

> **Note on round trips:** Rides where start and end station are the same produce
> a Haversine distance of ~0 miles. Casuals have a 1.63× higher round-trip rate,
> which partially suppresses their average distance — the 1.03× distance ratio
> slightly understates casual riders' actual travel.
"""))

cells.append(code("""\
# Duration
trips["duration_min"] = (
    (trips["ended_at"] - trips["started_at"]).dt.total_seconds() / 60
)
trips.loc[trips["duration_min"] <= 0, "duration_min"] = None

# Distance (Haversine)
lat1 = np.radians(trips["start_lat"])
lat2 = np.radians(trips["end_lat"])
dlat = lat2 - lat1
dlng = np.radians(trips["end_lng"] - trips["start_lng"])
a    = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlng/2)**2
trips["distance_mi"] = 3958.8 * 2 * np.arcsin(np.sqrt(a))
trips.loc[trips["distance_mi"] <= 0, "distance_mi"] = None

avgs = trips.groupby("member_casual")[["duration_min", "distance_mi"]].mean()
dur_ratio  = avgs.loc["casual", "duration_min"]  / avgs.loc["member", "duration_min"]
dist_ratio = avgs.loc["casual", "distance_mi"]   / avgs.loc["member", "distance_mi"]

print("=" * 50)
print("  Avg Duration & Distance by Rider Type")
print("=" * 50)
print(f"  {'Rider':<10} {'Avg Duration':>14} {'Avg Distance':>14}")
print(f"  {'-'*48}")
for rtype in ["member", "casual"]:
    d = avgs.loc[rtype, "duration_min"]
    m = avgs.loc[rtype, "distance_mi"]
    print(f"  {rtype:<10} {d:>12.2f} min {m:>12.2f} mi")
print(f"  {'Casual/Member ratio':<10}  {dur_ratio:>10.2f}x      {dist_ratio:>10.2f}x")

# --- Chart ---
fig, axes = plt.subplots(1, 2, figsize=(9, 4.5))
metrics   = ["duration_min", "distance_mi"]
titles    = ["Average Ride Duration (min)", "Average Ride Distance (mi)"]

for ax, metric, title in zip(axes, metrics, titles):
    vals   = [avgs.loc["member", metric], avgs.loc["casual", metric]]
    colors = [MEMBER_COLOR, CASUAL_COLOR]
    bars   = ax.bar(["Member", "Casual"], vals, color=colors, width=0.5,
                    edgecolor="white", linewidth=1.5)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02 * max(vals),
                f"{v:.1f}", ha="center", va="bottom", fontweight="bold", fontsize=11)
    ax.set_title(title)
    ax.set_ylabel("")
    ax.tick_params(axis="x", labelsize=11)

fig.suptitle("Casuals Ride Longer, Members Ride Purposefully", fontsize=12,
             fontweight="bold", y=1.02)
plt.tight_layout()
save_fig("02_duration_distance")
plt.show()
"""))

# ===========================================================================
# SECTION 4: HOURLY DISTRIBUTION
# ===========================================================================
cells.append(md("""---
## 4. When Do They Ride? — Hourly Distribution

The hourly chart is the single most revealing visualization in this analysis.

**Members** show two sharp peaks:
- **08:00** — morning commute
- **17:00** — evening commute

**Casuals** show one broad peak:
- Midday / early afternoon (11:00–15:00) — leisure riding

This is the clearest possible confirmation that members and casuals have
fundamentally different use cases. Members use the bikes as transportation.
Casuals use them for recreation. A conversion campaign needs to speak to
the commuter value proposition — not just "save money on rides."
"""))

cells.append(code("""\
trips["hour"] = trips["started_at"].dt.hour

hourly = (
    trips.groupby(["hour", "member_casual"])
    .size()
    .unstack(fill_value=0)
    .rename(columns={"member": "member", "casual": "casual"})
)
hourly["member_pct"] = hourly["member"] / hourly["member"].sum() * 100
hourly["casual_pct"] = hourly["casual"] / hourly["casual"].sum() * 100

# --- Chart ---
fig, ax = plt.subplots(figsize=(11, 5))
hours = hourly.index

ax.plot(hours, hourly["member_pct"], color=MEMBER_COLOR, linewidth=2.5,
        marker="o", markersize=4, label="Member")
ax.plot(hours, hourly["casual_pct"], color=CASUAL_COLOR, linewidth=2.5,
        marker="o", markersize=4, label="Casual")

# Annotate commute peaks
for peak_h, label, color in [(8, "8 AM\\ncommute", MEMBER_COLOR),
                              (17, "5 PM\\ncommute", MEMBER_COLOR)]:
    val = hourly.loc[peak_h, "member_pct"]
    ax.annotate(label, xy=(peak_h, val),
                xytext=(peak_h + 0.4, val + 0.4),
                fontsize=9, color=color, fontweight="bold")

ax.set_xlabel("Hour of Day")
ax.set_ylabel("% of Each Group's Total Rides")
ax.set_title("Hourly Ride Distribution — Members Commute, Casuals Leisure Ride",
             fontweight="bold")
ax.set_xticks(range(0, 24))
ax.set_xticklabels([f"{h:02d}:00" for h in range(24)], rotation=45, fontsize=8)
ax.legend(fontsize=11)
plt.tight_layout()
save_fig("03_hourly_distribution")
plt.show()
"""))

# ===========================================================================
# SECTION 5: WEEKEND VS WEEKDAY
# ===========================================================================
cells.append(md("""---
## 5. Weekend vs Weekday

Casuals ride **1.61× more on weekends** relative to their weekday volume, while
members are more consistent across the week (weekends are leisure for them too,
but they don't shift nearly as dramatically).

This reinforces the leisure-vs-commute split from the hourly chart. Casuals are
weekend recreational riders. Members integrate cycling into their daily routine.
"""))

cells.append(code("""\
trips["is_weekend"] = trips["started_at"].dt.dayofweek >= 5

wk = (
    trips.groupby(["member_casual", "is_weekend"])
    .size()
    .unstack()
    .rename(columns={False: "weekday", True: "weekend"})
)
wk["weekend_pct"] = wk["weekend"] / (wk["weekend"] + wk["weekday"]) * 100

ratios = {}
for rtype in ["member", "casual"]:
    wkend = wk.loc[rtype, "weekend"]
    wkday = wk.loc[rtype, "weekday"]
    ratios[rtype] = (wkend / wkday)

print("=" * 50)
print("  Weekend vs Weekday Rides")
print("=" * 50)
for rtype in ["member", "casual"]:
    r = wk.loc[rtype]
    print(f"  {rtype:<10}  weekday: {r['weekday']:>9,}   weekend: {r['weekend']:>9,}"
          f"   ratio: {ratios[rtype]:.2f}x")
print(f"\\n  Casual weekend/weekday ratio: {ratios['casual']:.2f}x")
print(f"  Member weekend/weekday ratio: {ratios['member']:.2f}x")

# --- Chart ---
fig, ax = plt.subplots(figsize=(7, 4.5))
x = np.arange(2)
w = 0.32
wkd_vals = [wk.loc["member","weekday"]/1000, wk.loc["casual","weekday"]/1000]
wke_vals = [wk.loc["member","weekend"]/1000, wk.loc["casual","weekend"]/1000]

b1 = ax.bar(x - w/2, wkd_vals, width=w, label="Weekday",
            color=[MEMBER_COLOR, CASUAL_COLOR], alpha=0.6, edgecolor="white")
b2 = ax.bar(x + w/2, wke_vals, width=w, label="Weekend",
            color=[MEMBER_COLOR, CASUAL_COLOR], edgecolor="white")

ax.set_xticks(x)
ax.set_xticklabels(["Member", "Casual"], fontsize=12)
ax.set_ylabel("Rides (thousands)")
ax.set_title("Weekend vs Weekday Ride Volume", fontweight="bold")
ax.legend(["Weekday", "Weekend"], fontsize=10)
plt.tight_layout()
save_fig("04_weekend_weekday")
plt.show()
"""))

# ===========================================================================
# SECTION 6: SEASONAL
# ===========================================================================
cells.append(md("""---
## 6. Seasonal Patterns

Casual ridership is highly seasonal — **42.7% of rides in summer are casual**,
dropping to just **19.6% in winter**. Member ridership is far more consistent
across seasons, confirming that members have committed to cycling as a year-round
transportation mode.

Implication: a conversion campaign timed for **late spring / early summer** —
when casual ridership is peaking and people are already engaged — will reach
the largest addressable audience at the moment they're most likely to consider
annual membership.
"""))

cells.append(code("""\
trips["month_int"] = trips["started_at"].dt.month
season_map = {12:"Winter",1:"Winter",2:"Winter",
              3:"Spring",4:"Spring",5:"Spring",
              6:"Summer",7:"Summer",8:"Summer",
              9:"Fall",10:"Fall",11:"Fall"}
trips["season"] = trips["month_int"].map(season_map)

season_order = ["Spring", "Summer", "Fall", "Winter"]
seasonal = (
    trips.groupby(["season", "member_casual"])
    .size()
    .unstack(fill_value=0)
)
seasonal["casual_pct"] = (
    seasonal["casual"] / (seasonal["casual"] + seasonal["member"]) * 100
)
seasonal = seasonal.reindex(season_order)

# --- Chart ---
fig, ax = plt.subplots(figsize=(8, 4.5))
x = np.arange(len(season_order))
w = 0.35

member_vals = [seasonal.loc[s, "member"]/1000 for s in season_order]
casual_vals = [seasonal.loc[s, "casual"]/1000 for s in season_order]

ax.bar(x - w/2, member_vals, width=w, label="Member",
       color=MEMBER_COLOR, edgecolor="white")
ax.bar(x + w/2, casual_vals, width=w, label="Casual",
       color=CASUAL_COLOR, edgecolor="white")

for i, s in enumerate(season_order):
    pct = seasonal.loc[s, "casual_pct"]
    ax.text(i + w/2, casual_vals[i] + 5, f"{pct:.0f}% casual",
            ha="center", va="bottom", fontsize=8, color=CASUAL_COLOR,
            fontweight="bold")

ax.set_xticks(x)
ax.set_xticklabels(season_order, fontsize=11)
ax.set_ylabel("Rides (thousands)")
ax.set_title("Seasonal Ride Volume — Casuals Peak Sharply in Summer",
             fontweight="bold")
ax.legend(fontsize=10)
plt.tight_layout()
save_fig("05_seasonal")
plt.show()
"""))

# ===========================================================================
# SECTION 7: BIKE TYPE
# ===========================================================================
cells.append(md("""---
## 7. Bike Type Mix — A Null Finding

Both members and casuals use classic and electric bikes in nearly identical
proportions (~35% classic, ~65% electric). There is no meaningful bike-type
preference difference between the groups.

**This is a null finding — and null findings matter.** A campaign targeting
"e-bike converts" or "classic bike loyalists" would not be supported by the data.
The conversion strategy should focus on *behavior* (commuter vs leisure), not
equipment preference.
"""))

cells.append(code("""\
bike_mix = (
    trips.groupby(["member_casual", "rideable_type"])
    .size()
    .unstack(fill_value=0)
)
bike_mix_pct = bike_mix.div(bike_mix.sum(axis=1), axis=0) * 100

print("=" * 55)
print("  Bike Type Mix (% within each rider group)")
print("=" * 55)
print(bike_mix_pct.round(1).to_string())
print("\\n  Null finding: no meaningful bike-type preference difference.")

# --- Chart ---
fig, ax = plt.subplots(figsize=(7, 4))
bike_types = bike_mix_pct.columns.tolist()
x = np.arange(len(bike_types))
w = 0.35

for i, (rtype, color) in enumerate([("member", MEMBER_COLOR), ("casual", CASUAL_COLOR)]):
    vals = [bike_mix_pct.loc[rtype, bt] for bt in bike_types]
    bars = ax.bar(x + (i-0.5)*w, vals, width=w, label=rtype.capitalize(),
                  color=color, edgecolor="white")
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f"{v:.0f}%", ha="center", va="bottom", fontsize=10, fontweight="bold")

ax.set_xticks(x)
ax.set_xticklabels([bt.replace("_", " ").title() for bt in bike_types], fontsize=11)
ax.set_ylabel("% of group's rides")
ax.set_ylim(0, 85)
ax.set_title("Bike Type Mix — Nearly Identical for Both Groups (Null Finding)",
             fontweight="bold")
ax.legend(fontsize=10)
plt.tight_layout()
save_fig("06_bike_type_mix")
plt.show()
"""))

# ===========================================================================
# SECTION 8: TOP STATIONS
# ===========================================================================
cells.append(md("""---
## 8. Where Do They Start? — Top Stations

The top casual start stations tell the leisure-use story in concrete, geographic terms:

| Station | Casual Starts | Casual % |
|---|---|---|
| Streeter Dr & Grand Ave | 23,659 | 76.4% |
| DuSable Lake Shore Dr & Monroe St | 22,148 | 82.3% |
| **Shedd Aquarium** | **16,957** | **81.8%** |
| Millennium Park | 16,244 | 82.3% |

**Shedd Aquarium is the starkest example:** fewer than 1 in 5 rides there are from
members. Every station in the casual top 10 is a lakefront tourist or leisure
destination — Navy Pier, the Museum Campus, Millennium Park.

By contrast, the member top stations are urban transit hubs — Kingsbury & Kinzie,
Clark & Elm, Wells & Concord. Classic commuter infrastructure.

**Zero overlap** between the two top-10 lists. These are not just different
proportions of the same riders — they are entirely different people going to
entirely different places.
"""))

cells.append(code("""\
def is_missing(col):
    return col.isna() | (col.str.strip() == "")

valid = trips[~is_missing(trips["start_station_name"])].copy()

station_counts = (
    valid.groupby(["start_station_name", "member_casual"])
    .size()
    .unstack(fill_value=0)
    .reset_index()
)
station_counts.columns.name = None
station_counts["total"] = station_counts.get("member", 0) + station_counts.get("casual", 0)
station_counts["casual_pct"] = station_counts["casual"] / station_counts["total"] * 100

top10_casual = station_counts.nlargest(10, "casual")[
    ["start_station_name", "casual", "member", "casual_pct"]
].reset_index(drop=True)

top10_member = station_counts.nlargest(10, "member")[
    ["start_station_name", "member", "casual", "casual_pct"]
].reset_index(drop=True)

print("Top 10 Casual Start Stations")
print("-" * 65)
for _, r in top10_casual.iterrows():
    print(f"  {r['start_station_name'][:40]:<40}  "
          f"casual: {int(r['casual']):>6,}  ({r['casual_pct']:.1f}% casual)")

print("\\nTop 10 Member Start Stations")
print("-" * 65)
for _, r in top10_member.iterrows():
    print(f"  {r['start_station_name'][:40]:<40}  "
          f"member: {int(r['member']):>6,}  ({100-r['casual_pct']:.1f}% member)")

overlap = set(top10_casual["start_station_name"]) & set(top10_member["start_station_name"])
print(f"\\nOverlap between top 10 lists: {len(overlap)}")

# --- Chart: Casual top 10 stations ---
fig, ax = plt.subplots(figsize=(9, 5.5))
names  = [n[:35] + "…" if len(n) > 35 else n
          for n in top10_casual["start_station_name"]][::-1]
values = top10_casual["casual"].tolist()[::-1]
bars   = ax.barh(names, values, color=CASUAL_COLOR, edgecolor="white")
for bar, v in zip(bars, values):
    ax.text(bar.get_width() + 100, bar.get_y() + bar.get_height()/2,
            f"{v:,}", va="center", fontsize=9)
ax.set_xlabel("Casual Ride Starts")
ax.set_title("Top 10 Start Stations — Casual Riders\\nAll Lakefront Leisure Destinations",
             fontweight="bold")
ax.set_xlim(0, max(values) * 1.15)
plt.tight_layout()
save_fig("07_top_casual_stations")
plt.show()
"""))

# ===========================================================================
# SECTION 9: REVENUE PROXY
# ===========================================================================
cells.append(md("""---
## 9. The Conversion Opportunity — Revenue Proxy

### Pricing assumptions (Divvy ~2025)
- **Annual member:** \$119.88/year — unlimited classic rides + e-bike at \$0.18/min
- **Casual single-ride:** \$1.00 unlock + \$0.18/min

### The key question
If even a fraction of the 2,015,499 casual riders converted to annual membership,
what is the revenue upside?

The table below presents a range of scenarios. Rather than projecting a single number,
we show the full sensitivity — the marketing team picks the row they believe is
achievable with their campaign budget.

> **Important:** These are illustrative estimates using publicly available pricing.
> Actual Cyclistic pricing may differ. The purpose is to frame the magnitude of the
> opportunity, not to produce auditable financial figures.

"""))

cells.append(code("""\
UNLOCK_FEE     = 1.00
PER_MIN_RATE   = 0.18
MEMBER_ANNUAL  = 9.99 * 12   # $119.88

casual_mask = trips["member_casual"] == "casual"
member_mask = trips["member_casual"] == "member"
ebike_mask  = trips["rideable_type"] == "electric_bike"

total_casual_rev = (
    casual_mask.sum() * UNLOCK_FEE +
    trips.loc[casual_mask, "duration_min"].sum() * PER_MIN_RATE
)
member_ebike_rev = (
    trips.loc[member_mask & ebike_mask, "duration_min"].sum() * PER_MIN_RATE
)
casual_ride_count = casual_mask.sum()

print(f"Est. casual pay-per-ride revenue:  ${total_casual_rev:>14,.2f}")
print(f"Est. member e-bike overage:        ${member_ebike_rev:>14,.2f}")
print(f"Casual rides (conversion targets):  {casual_ride_count:>14,}")
print()
print("Conversion Sensitivity — Annual Membership Revenue Upside")
print(f"({casual_ride_count:,} casual riders × rate × ${MEMBER_ANNUAL:.2f}/yr)")
print("-" * 58)
rates      = [0.05, 0.10, 0.15, 0.20, 0.25]
new_mems   = [int(casual_ride_count * r) for r in rates]
upsides    = [n * MEMBER_ANNUAL for n in new_mems]

for r, n, u in zip(rates, new_mems, upsides):
    print(f"  {r*100:.0f}%  →  {n:>9,} new members  →  ${u:>12,.0f}/yr")

# --- Chart ---
fig, ax = plt.subplots(figsize=(8, 4.5))
bar_colors = plt.cm.Blues(np.linspace(0.4, 0.85, len(rates)))
bars = ax.bar([f"{r*100:.0f}%" for r in rates],
              [u/1e6 for u in upsides],
              color=bar_colors, edgecolor="white")
for bar, u, n in zip(bars, upsides, new_mems):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f"${u/1e6:.1f}M\\n({n:,} members)",
            ha="center", va="bottom", fontsize=8.5, fontweight="bold")
ax.set_xlabel("Conversion Rate")
ax.set_ylabel("Annual Revenue Upside ($M)")
ax.set_title("Revenue Upside by Conversion Rate\\n"
             f"({casual_ride_count:,} casual riders × ${MEMBER_ANNUAL:.2f}/yr)",
             fontweight="bold")
ax.set_ylim(0, max(upsides)/1e6 * 1.3)
plt.tight_layout()
save_fig("08_revenue_sensitivity")
plt.show()
"""))

# ===========================================================================
# SECTION 10: PEAK CONCURRENT
# ===========================================================================
cells.append(md("""---
## 10. Fleet Utilization — Peak Concurrent Rides

### Method: Sweep Line Algorithm

Each ride generates two events: a **+1** at the start time and a **−1** at the end time.
Sorting all events by timestamp and taking a running cumulative sum gives the number
of bikes in use at every moment in the dataset.

The **maximum** of that cumulative sum is the minimum fleet size Cyclistic needs
to serve peak demand.

### Key results
- **Peak concurrent rides: 1,199** — Sunday, October 12, 2025 at 12:24 PM
- This sets a floor on required fleet size
- Converting casuals to members changes their *pricing model*, not their behavior —
  peak fleet demand stays stable at conversion. If members ride more frequently
  over time (zero marginal cost), fleet demand could grow — but that is a
  secondary, longer-term effect.

### Why Python for this?
This analysis would be verbose in pure SQL (requiring a self-join or recursive CTE)
and slow in R without additional packages. Python's vectorized `pd.concat` +
`sort_values` + `cumsum` handles 11.2M events (2 per ride) cleanly and efficiently.
"""))

cells.append(code("""\
import time

print("Building sweep line events (11.2M rows)...")
t0     = time.perf_counter()
starts = pd.DataFrame({"ts": trips["started_at"], "event":  1})
ends   = pd.DataFrame({"ts": trips["ended_at"],   "event": -1})
events = (
    pd.concat([starts, ends], ignore_index=True)
    .sort_values("ts")
    .reset_index(drop=True)
)
events["concurrent"] = events["event"].cumsum()
elapsed = time.perf_counter() - t0
print(f"Done in {elapsed:.2f}s — {len(events):,} events processed")

peak_idx        = events["concurrent"].idxmax()
peak_concurrent = events.loc[peak_idx, "concurrent"]
peak_ts         = events.loc[peak_idx, "ts"]
print(f"\\nPeak simultaneous rides: {peak_concurrent:,}")
print(f"At:                      {peak_ts}")

# Peak by hour
events["hour"] = events["ts"].dt.hour
peak_by_hour   = events.groupby("hour")["concurrent"].max()

# Peak by day of week
events["dow"]     = events["ts"].dt.dayofweek
day_names         = {0:"Mon",1:"Tue",2:"Wed",3:"Thu",4:"Fri",5:"Sat",6:"Sun"}
events["day_name"] = events["dow"].map(day_names)
peak_by_dow       = events.groupby("dow")["concurrent"].max()

# --- Charts ---
fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

# Hour chart
ax = axes[0]
ax.bar(peak_by_hour.index, peak_by_hour.values, color=MEMBER_COLOR,
       edgecolor="white", alpha=0.85)
ax.set_xticks(range(0, 24, 2))
ax.set_xticklabels([f"{h:02d}:00" for h in range(0, 24, 2)], rotation=45, fontsize=8)
ax.set_xlabel("Hour of Day")
ax.set_ylabel("Peak Concurrent Rides")
ax.set_title("Peak Concurrent Rides by Hour", fontweight="bold")

# Day of week chart
ax = axes[1]
dow_order  = [0,1,2,3,4,5,6]
dow_labels = [day_names[d] for d in dow_order]
dow_vals   = [peak_by_dow[d] for d in dow_order]
colors     = [CASUAL_COLOR if d >= 5 else MEMBER_COLOR for d in dow_order]
ax.bar(dow_labels, dow_vals, color=colors, edgecolor="white", alpha=0.85)
ax.set_xlabel("Day of Week")
ax.set_ylabel("Peak Concurrent Rides")
ax.set_title("Peak Concurrent Rides by Day\\n(blue=weekday, amber=weekend)",
             fontweight="bold")

fig.suptitle(f"Fleet Utilization — Peak of {peak_concurrent:,} simultaneous rides",
             fontsize=12, fontweight="bold", y=1.02)
plt.tight_layout()
save_fig("09_peak_concurrent")
plt.show()
"""))

# ===========================================================================
# SECTION 11: CASUAL RIDER SEGMENTATION
# ===========================================================================
cells.append(md("""---
## 11. Casual Rider Segmentation — Who to Target

Not all casual riders are equal conversion opportunities. The data reveals
two very different casual rider profiles:

| Profile | Description | Conversion probability |
|---|---|---|
| **Commuter-pattern casuals** | Weekday rides, peak hours (7–9 AM or 4–6 PM) | **High** — already using bikes as transportation |
| **Leisure/tourist casuals** | Weekend afternoons, lakefront destinations | **Low** — visiting Chicago or riding for fun |

### Definition: "Commuter-pattern casual"

A casual ride meeting **both** behavioral conditions:
- **Weekday** (Monday–Friday)
- **Peak hour** (7:00–9:00 AM or 16:00–18:00 PM)

If you're riding at 8 AM on a Tuesday, you're almost certainly commuting — not touring Chicago.
The behavioral signal alone identifies the segment. As corroboration, we separately measure what
fraction of commuter-pattern casuals start at member top-10 stations (transit hubs rather than
lakefront destinations). That overlap confirms they're using member corridors.

### Why this matters for revenue

A targeted campaign aimed at commuter-pattern casuals can achieve a **higher conversion rate
per marketing dollar** than a broad casual campaign, because these riders already have a direct
financial incentive: they are paying per-minute for something they could get for a flat annual fee.
The chart below shows this using a 2× conversion rate assumption for the targeted segment.
"""))

cells.append(code("""\
# Replicate the Polars Script 13 analysis in pandas
# Definition: "commuter-pattern casual" = weekday + peak hour
# The behavioral signal (WHEN they ride) is the primary criterion.
# Station overlap with member corridors is reported separately as corroboration.

# Step 1: Tag rides with timing signals
if "hour" not in trips.columns:
    trips["hour"] = trips["started_at"].dt.hour
if "is_weekend" not in trips.columns:
    trips["is_weekend"] = trips["started_at"].dt.dayofweek >= 5

trips["is_peak_hour"] = trips["hour"].isin([7, 8, 16, 17])
trips["is_weekday"]   = ~trips["is_weekend"]

# Step 2: Segment casual rides — behavioral definition only
casual_rides   = trips[trips["member_casual"] == "casual"].copy()
commuter_mask  = casual_rides["is_peak_hour"] & casual_rides["is_weekday"]

total_casual   = len(casual_rides)
total_commuter = commuter_mask.sum()
total_leisure  = total_casual - total_commuter
commuter_pct   = total_commuter / total_casual * 100

MEMBER_ANNUAL = 9.99 * 12  # $119.88

print("=" * 65)
print("  Casual Rider Segmentation — Commuter vs Leisure Profile")
print("=" * 65)
print(f"  Total casual rides:            {total_casual:>10,}")
print(f"  Commuter-pattern casuals:      {total_commuter:>10,}  ({commuter_pct:.1f}%)")
print(f"  Leisure/tourist casuals:       {total_leisure:>10,}  ({100-commuter_pct:.1f}%)")
print(f"  Definition: weekday + peak hour (7-9 AM or 4-6 PM)")

# Step 3: Corroboration — what % of commuter casuals start at member top-10 stations?
def is_missing(col):
    return col.isna() | (col.str.strip() == "")

valid = trips[~is_missing(trips["start_station_name"])].copy()
member_station_counts = (
    valid[valid["member_casual"] == "member"]
    .groupby("start_station_name")
    .size()
    .nlargest(10)
)
top10_member_stations = set(member_station_counts.index)

commuter_rides = casual_rides[commuter_mask].copy()
commuter_at_member_station = commuter_rides["start_station_name"].isin(top10_member_stations).sum()
print(f"\\n  Corroboration: {commuter_at_member_station:,} of commuter-pattern casuals")
print(f"  start at a member top-10 station")
print(f"  ({commuter_at_member_station / total_commuter * 100:.1f}% of commuter casuals — confirms corridor overlap)")

# Step 4: Revenue comparison
print()
print("  Revenue Upside — Targeted vs Broad Campaign")
print(f"  {'Strategy':<35} {'10% rate':>12} {'20% rate':>12} {'25% rate':>12}")
print(f"  {'-'*66}")
for label, pool in [("Broad (all casuals)", total_casual),
                    ("Targeted (commuter casuals)", total_commuter)]:
    row_vals = [f"${int(pool*r)*MEMBER_ANNUAL/1e6:.1f}M" for r in [0.10, 0.20, 0.25]]
    print(f"  {label:<35} {'  '.join(row_vals)}")
print()
print("  Key: targeted campaign reaches a smaller pool but at higher conversion")
print("  rate — fewer contacts, lower cost, comparable or better return.")

# --- Chart 1: Commuter vs Leisure breakdown (bar, not pie — both visible) ---
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

ax = axes[0]
labels = ["Commuter-pattern\\ncasuals", "Leisure / tourist\\ncasuals"]
values = [total_commuter, total_leisure]
colors = ["#E53935", CASUAL_COLOR]
bars = ax.bar(labels, [v/1000 for v in values], color=colors, edgecolor="white",
              width=0.5)
for bar, v, pct in zip(bars, values, [commuter_pct, 100-commuter_pct]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
            f"{v:,}\\n({pct:.0f}%)", ha="center", va="bottom",
            fontsize=10, fontweight="bold")
ax.set_ylabel("Rides (thousands)")
ax.set_title(f"Casual Rider Profiles\\n({total_casual:,} total casual rides)",
             fontweight="bold")
ax.set_ylim(0, max(values)/1000 * 1.25)

# --- Chart 2: Targeted vs Broad — show conversion rate assumption explicitly ---
ax = axes[1]
# Premise: commuter casuals convert at 2x the rate of average casuals
# because they already behave like members (weekday + peak hour)
broad_rates    = [0.05, 0.10, 0.15, 0.20]
targeted_rates = [0.10, 0.20, 0.30, 0.40]   # 2x conversion rate assumption
broad_rev    = [int(total_casual   * r) * MEMBER_ANNUAL / 1e6 for r in broad_rates]
targeted_rev = [int(total_commuter * r) * MEMBER_ANNUAL / 1e6 for r in targeted_rates]

x = np.arange(len(broad_rates))
w = 0.38
b1 = ax.bar(x - w/2, broad_rev,    width=w, label="Broad @ base rate",
            color=CASUAL_COLOR, alpha=0.7, edgecolor="white")
b2 = ax.bar(x + w/2, targeted_rev, width=w, label="Targeted @ 2× rate",
            color="#E53935", edgecolor="white")

for bar, v in zip(b1, broad_rev):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f"${v:.1f}M", ha="center", va="bottom", fontsize=8.5, fontweight="bold")
for bar, v in zip(b2, targeted_rev):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f"${v:.1f}M", ha="center", va="bottom", fontsize=8.5, fontweight="bold",
            color="#E53935")

ax.set_xticks(x)
ax.set_xticklabels(["5% / 10%", "10% / 20%", "15% / 30%", "20% / 40%"], fontsize=9)
ax.set_xlabel("Conversion Rate (Broad / Targeted)")
ax.set_ylabel("Annual Revenue Upside ($M)")
ax.set_title("Targeted Campaign at 2× Conversion Rate\\nvs Broad Campaign",
             fontweight="bold")
ax.legend(fontsize=9)

fig.suptitle("Commuter-Pattern Casuals: Smaller Pool, Higher Intent,\\n"
             "Better ROI on Marketing Spend", fontsize=12, fontweight="bold", y=1.02)
plt.tight_layout()
save_fig("10_casual_segmentation")
plt.show()
"""))

# ===========================================================================
# KEY FINDINGS SUMMARY
# ===========================================================================
cells.append(md("""---
## 12. Key Findings Summary

| # | Finding | Evidence |
|---|---|---|
| 1 | Members ride to commute; casuals ride for leisure | Dual commute peaks at 8 AM / 5 PM (members only) |
| 2 | Casual rides are 1.82× longer in duration | Consistent across SQL Server, DuckDB, R, pandas |
| 3 | Casual ridership is highly seasonal (42.7% summer → 19.6% winter) | Best time for conversion campaign: late spring |
| 4 | Top casual stations are 100% leisure / tourist destinations | Zero overlap with top member stations |
| 5 | Shedd Aquarium: 81.8% casual — starkest example | Named, concrete finding for presentations |
| 6 | No bike-type preference difference (null finding) | ~65% electric for both groups |
| 7 | E-bikes have onboard GPS — missing station data is NOT a quality gap | 100% of e-bikes without station names still have GPS coordinates |
| 8 | Conversion opportunity: 5%–25% conversion = $12M–$60M annual upside | At $119.88/yr × 2,015,499 casual riders |
| 9 | Peak fleet: 1,199 simultaneous rides (Oct 12, 2025, noon Sunday) | Sweep line algorithm — unique Python analysis |
| 10 | Converting casuals to members changes pricing, not behavior | Peak fleet demand stays stable at conversion |
| 11 | Commuter-pattern casuals are the highest-value conversion target | Weekday + peak hour — higher probability, lower cost |

---

### Recommendation

A targeted campaign aimed at casual riders who already commute (weekday + peak hour)
has the highest conversion probability. These riders are paying per-minute for something
they could get for a flat annual fee — the value proposition is immediate and concrete.

The seasonal timing (late spring), behavioral targeting (commuter-pattern casuals),
and pricing message ($119.88/yr vs pay-per-minute) are the three levers the marketing
team controls.

---
*Analysis by Peter | Cyclistic Capstone | Google Data Analytics Certificate*
*Tools: Power BI · SQL Server/SSIS · DuckDB · R · Python (pandas + Polars)*
"""))

# ===========================================================================
# ASSEMBLE & WRITE
# ===========================================================================
nb.cells = cells
nbf.write(nb, OUTPUT_NB)
print(f"Notebook written to: {OUTPUT_NB}")
print(f"Open with: jupyter notebook cyclistic_analysis.ipynb")
| 9 | Peak fleet: 1,199 simultaneous rides (Oct 12, 2025, noon Sunday) | Sweep line algorithm — unique Python analysis |
| 10 | Converting casuals to members changes pricing, not behavior | Peak fleet demand stays stable at conversion |
| 11 | Commuter-pattern casuals are the highest-value conversion target | Weekday + peak hour + member station — higher probability, lower cost |

---

### Recommendation

A targeted campaign aimed at casual riders who commute (or who ride on routes
overlapping with commuter corridors) has the highest conversion probability.
The seasonal timing (late spring), geographic targeting (lakefront → downtown
corridors), and pricing message ($119.88/yr vs pay-per-minute) are the three
levers the marketing team controls.

---
*Analysis by Peter | Cyclistic Capstone | Google Data Analytics Certificate*
*Tools: Power BI · SQL Server/SSIS · DuckDB · R · Python (pandas + Polars)*
"""))

# ===========================================================================
# ASSEMBLE & WRITE
# ===========================================================================
nb.cells = cells
nbf.write(nb, OUTPUT_NB)
print(f"Notebook written to: {OUTPUT_NB}")
print(f"Open with: jupyter notebook cyclistic_analysis.ipynb")
| 10 | Converting casuals to members changes pricing, not behavior | Peak fleet demand stays stable at conversion |
| 11 | Commuter-pattern casuals are the highest-value conversion target | Weekday + peak hour — higher probability, lower cost |

---

### Recommendation

A targeted campaign aimed at casual riders who already commute (weekday + peak hour)
has the highest conversion probability. These riders are paying per-minute for something
they could get for a flat annual fee.

The seasonal timing (late spring), behavioral targeting (commuter-pattern casuals),
and pricing message (\$119.88/yr vs pay-per-minute) are the three levers the marketing
team controls.

---
*Analysis by Peter | Cyclistic Capstone | Google Data Analytics Certificate*
*Tools: Power BI · SQL Server/SSIS · DuckDB · R · Python (pandas + Polars)*
"""))

# ===========================================================================
# ASSEMBLE & WRITE
# ===========================================================================
nb.cells = cells
nbf.write(nb, OUTPUT_NB)
print(f"Notebook written to: {OUTPUT_NB}")
print(f"Open with: jupyter notebook cyclistic_analysis.ipynb")
upiter notebook cyclistic_analysis.ipynb")
