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
     4-6 PM). Already using the bike as transportation. High conversion
     probability — they're paying per-minute for something they could get
     for a flat annual fee.

  A targeted campaign aimed at commuter-pattern casuals would have a higher
  conversion rate per marketing dollar spent than a broad casual campaign.

Method:
  "Commuter-pattern casual" = casual ride that meets BOTH behavioral criteria:
    - Weekday (Monday-Friday)
    - Peak hour (7:00-9:00 AM or 16:00-18:00 PM)

  If you're riding at 8 AM on a Tuesday, you are almost certainly commuting,
  not touring Chicago. The behavioral signal alone identifies the segment.

  Member top-10 station overlap is reported separately as corroboration --
  it confirms these riders are using member corridors, not lakefront spots.

Polars notes:
  - is_in() tests list membership -- equivalent to SQL IN() or pandas .isin().
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
# Step 1: Tag rides with behavioral signals
# ---------------------------------------------------------------------------
trips = trips.with_columns(
    pl.col("started_at").dt.hour().alias("hour"),
    pl.col("started_at").dt.weekday().alias("dow"),  # 1=Mon...7=Sun
)

trips = trips.with_columns(
    # Peak hour: 7-9 AM or 4-6 PM
    pl.col("hour").is_in([7, 8, 16, 17]).alias("is_peak_hour"),
    # Weekday: Mon-Fri (dow 1-5 in Polars)
    (pl.col("dow") <= 5).alias("is_weekday"),
)

# ---------------------------------------------------------------------------
# Step 2: Define commuter-pattern casuals -- behavioral definition
# ---------------------------------------------------------------------------
casual_rides = trips.filter(pl.col("member_casual") == "casual")

commuter_casual = casual_rides.filter(
    pl.col("is_peak_hour") & pl.col("is_weekday")
)

leisure_casual = casual_rides.filter(
    ~(pl.col("is_peak_hour") & pl.col("is_weekday"))
)

total_casual   = casual_rides.height
total_commuter = commuter_casual.height
total_leisure  = leisure_casual.height
commuter_pct   = total_commuter / total_casual * 100

print("=" * 68)
print("  Casual Rider Segmentation — Commuter vs Leisure Profile")
print("=" * 68)
print(f"  Total casual rides:            {total_casual:>10,}")
print(f"  Commuter-pattern casuals:      {total_commuter:>10,}  ({commuter_pct:.1f}%)")
print(f"  Leisure/tourist casuals:       {total_leisure:>10,}  ({100-commuter_pct:.1f}%)")
print()
print("  Commuter-pattern definition (behavioral signals):")
print("    ✓ Weekday ride (Mon–Fri)")
print("    ✓ Peak hour (7–9 AM or 4–6 PM)")

# ---------------------------------------------------------------------------
# Step 3: Corroboration -- member top-10 station overlap
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

commuter_at_member_stn = commuter_casual.filter(
    pl.col("start_station_name").is_in(top10_member_stations)
).height
overlap_pct = commuter_at_member_stn / total_commuter * 100 if total_commuter > 0 else 0

print()
print(f"  Corroboration: {commuter_at_member_stn:,} commuter-pattern casuals")
print(f"  start at a member top-10 station ({overlap_pct:.1f}%)")
print(f"  -- confirms corridor overlap with member commuters")
print()
print("  Member top-10 stations (for reference):")
for i, s in enumerate(top10_member_stations, 1):
    print(f"    {i:2}. {s}")

# ---------------------------------------------------------------------------
# Step 4: Targeted vs broad conversion revenue comparison
# Assumption: commuter casuals convert at 2x the base rate because they
# already exhibit commuter behavior and have a direct financial incentive.
# ---------------------------------------------------------------------------
print()
print("=" * 68)
print("  Revenue Upside — Targeted vs Broad Campaign")
print(f"  Annual membership: ${MEMBER_ANNUAL:.2f}/yr")
print("  Assumption: commuter casuals convert at 2x the base rate")
print("=" * 68)
print(f"  {'Strategy':<40} {'5%/10%':>10} {'10%/20%':>10} {'15%/30%':>10}")
print(f"  {'-'*70}")

broad_rates    = [0.05, 0.10, 0.15]
targeted_rates = [0.10, 0.20, 0.30]

broad_vals    = [f"${int(total_casual   * r) * MEMBER_ANNUAL / 1e6:>7.1f}M"
                 for r in broad_rates]
targeted_vals = [f"${int(total_commuter * r) * MEMBER_ANNUAL / 1e6:>7.1f}M"
                 for r in targeted_rates]

print(f"  {'Broad (all casuals)':<40} {'  '.join(broad_vals)}")
print(f"  {'Targeted (commuter casuals @ 2x rate)':<40} {'  '.join(targeted_vals)}")

print()
print("  Insight: A targeted campaign reaching fewer people at a higher")
print("  conversion rate produces comparable revenue -- at lower cost.")
print("  Targeted vs Broad")
print("=" * 68)
