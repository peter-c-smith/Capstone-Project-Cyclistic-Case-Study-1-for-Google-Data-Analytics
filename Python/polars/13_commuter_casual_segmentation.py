"""
13_commuter_casual_segmentation.py
-----------------------------------
Which casual riders exhibit commuter-like behavior, and what is the
revenue upside of targeting only this high-conversion-probability segment?

Background:
  The standard conversion argument treats all 2,015,499 casual riders as
  equally likely to convert to annual membership. But the data shows two
  very different casual rider profiles:

  1. Leisure/tourist casuals — riding from lakefront destinations on weekend
     afternoons. May not live in Chicago. Low conversion probability.

  2. Commuter-pattern casuals — riding during weekday peak hours (7-9 AM,
     4-6 PM) from stations that also appear in the member top-10. Already
     using the bike as transportation. High conversion probability.

  A targeted campaign aimed at commuter-pattern casuals would have a higher
  conversion rate per marketing dollar spent than a broad casual campaign.

Method:
  "Commuter-pattern casual" = casual ride that meets ALL of:
    - Weekday (Monday–Friday)
    - Peak hour (7:00–9:00 AM or 16:00–18:00 PM)
    - Start station in the member top-10 list

  This is a conservative definition — it undercounts true commuter casuals
  (some commuters use non-top-10 stations) but gives a defensible floor.

Polars notes:
  - is_in() tests list membership — equivalent to SQL IN() or pandas .isin().
  - Multiple filter conditions chain with & (and) | (or).
  - This script demonstrates Polars' strength for multi-condition filtering:
    all conditions are evaluated as a single vectorized expression.

This script is unique to the Python module (Polars implementation).
The insight originated during the pandas module discussion.
"""

import polars as pl
from utils import load_trips

trips = load_trips()

UNLOCK_FEE    = 1.00
PER_MIN_RATE  = 0.18
MEMBER_ANNUAL = 9.99 * 12  # $119.88

# ---------------------------------------------------------------------------
# Step 1: Identify member top-10 start stations
# ---------------------------------------------------------------------------
valid = trips.filter(
    pl.col("start_station_name").is_not_null() &
    (pl.col("start_station_name").str.strip_chars() != "")
)

member_stations = (
    valid.filter(pl.col("member_casual") == "member")
    .group_by("start_station_name")
    .agg(pl.len().alias("member_rides"))
    .top_k(10, by="member_rides")
)
top10_member_stations = member_stations["start_station_name"].to_list()

# ---------------------------------------------------------------------------
# Step 2: Tag rides with hour and day type
# ---------------------------------------------------------------------------
trips = trips.with_columns(
    pl.col("started_at").dt.hour().alias("hour"),
    pl.col("started_at").dt.weekday().alias("dow"),  # 1=Mon...7=Sun
)

trips = trips.with_columns(
    # Peak hour: 7-9 AM or 4-6 PM
    (
        pl.col("hour").is_in([7, 8, 16, 17])
    ).alias("is_peak_hour"),
    # Weekday: Mon-Fri (dow 1-5 in Polars)
    (pl.col("dow") <= 5).alias("is_weekday"),
    # Member station
    pl.col("start_station_name").is_in(top10_member_stations)
    .alias("is_member_station"),
)

# ---------------------------------------------------------------------------
# Step 3: Define commuter-pattern casuals
# ---------------------------------------------------------------------------
casual_rides = trips.filter(pl.col("member_casual") == "casual")

commuter_casual = casual_rides.filter(
    pl.col("is_peak_hour") &
    pl.col("is_weekday") &
    pl.col("is_member_station")
)

leisure_casual = casual_rides.filter(
    ~(pl.col("is_peak_hour") & pl.col("is_weekday") & pl.col("is_member_station"))
)

total_casual      = casual_rides.height
total_commuter    = commuter_casual.height
total_leisure     = leisure_casual.height
commuter_pct      = total_commuter / total_casual * 100

print("=" * 68)
print("  Casual Rider Segmentation — Commuter vs Leisure Profile")
print("=" * 68)
print(f"  Total casual rides:            {total_casual:>10,}")
print(f"  Commuter-pattern casuals:      {total_commuter:>10,}  ({commuter_pct:.1f}%)")
print(f"  Leisure/tourist casuals:       {total_leisure:>10,}  ({100-commuter_pct:.1f}%)")
print()
print("  Commuter-pattern definition:")
print("    ✓ Weekday ride (Mon–Fri)")
print("    ✓ Peak hour (7–9 AM or 4–6 PM)")
print("    ✓ Start station in member top-10")
print()
print("  Member top-10 stations used as filter:")
for i, s in enumerate(top10_member_stations, 1):
    print(f"    {i:2}. {s}")

# ---------------------------------------------------------------------------
# Step 4: Targeted vs broad conversion revenue comparison
# ---------------------------------------------------------------------------
print()
print("=" * 68)
print("  Revenue Upside — Targeted vs Broad Campaign")
print(f"  Annual membership: ${MEMBER_ANNUAL:.2f}/yr")
print("=" * 68)
print(f"  {'Strategy':<35} {'10% rate':>12} {'20% rate':>12} {'25% rate':>12}")
print(f"  {'-'*66}")

for label, pool in [
    ("Broad (all casuals)",       total_casual),
    ("Targeted (commuter casuals)", total_commuter),
]:
    row_vals = []
    for rate in [0.10, 0.20, 0.25]:
        upside = int(pool * rate) * MEMBER_ANNUAL
        row_vals.append(f"${upside/1e6:>8.1f}M")
    print(f"  {label:<35} {'  '.join(row_vals)}")

print()
print("  Insight: A targeted campaign with a higher conversion rate")
print("  on a smaller pool can outperform a broad campaign with a")
print("  lower conversion rate — and costs less to run.")
print()
print("  Caveat: This is a conservative floor estimate. Many commuter-")
print("  pattern casuals start from non-top-10 member stations.")
print("  The true commuter casual pool is likely larger.")
print("=" * 68)
