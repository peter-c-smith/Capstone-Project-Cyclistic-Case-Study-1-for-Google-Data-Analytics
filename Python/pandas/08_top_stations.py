"""
08_top_stations.py
------------------
Which stations are most popular, and do casual and member riders
concentrate at different locations?

Key findings:
  - Zero overlap between member and casual top 10 station lists
  - Member top stations: transit hubs near Union Station, Canal St, Kinzie St
  - Casual top stations: lakefront/tourist destinations — Navy Pier,
    Millennium Park, Shedd Aquarium
  - Shedd Aquarium is the starkest example: 81.8% casual (the most
    casual-skewed station in the top 10 by a wide margin)

pandas notes:
  - Filter out null/empty station names with dropna() + boolean mask before
    grouping — same logic as SQL's WHERE station IS NOT NULL AND station <> ''.
  - groupby().agg() computes member and casual counts in one pass using
    named aggregations — cleaner than running two separate groupbys.
  - nlargest(10) replaces SQL's ORDER BY ... LIMIT 10 / SELECT TOP 10.

Expected output (matching SQL Server, DuckDB, and R):
  Member #1:  Kingsbury St & Kinzie St
  Casual #1:  DuSable Lake Shore Dr & Monroe St
  Shedd Aquarium: ~81.8% casual
  Zero overlap between the two top 10 lists
"""

import pandas as pd
from utils import load_trips

trips = load_trips()

# ---------------------------------------------------------------------------
# Filter to rides with a known start station
#
# dropna() removes NaN rows; the boolean mask removes empty strings.
# Both are needed: CSVs can have either representation for missing data.
# ---------------------------------------------------------------------------

has_station = trips[
    trips["start_station_name"].notna() &
    (trips["start_station_name"].str.strip() != "")
].copy()

# ---------------------------------------------------------------------------
# Station-level counts — one groupby for both rider types
# ---------------------------------------------------------------------------

station_counts = (
    has_station.groupby(["start_station_name", "member_casual"])
    .size()
    .unstack(fill_value=0)
)
station_counts.columns.name = None
station_counts["total"] = station_counts.sum(axis=1)

# Ensure both columns exist even if one type has zero rides at a station
for col in ["member", "casual"]:
    if col not in station_counts.columns:
        station_counts[col] = 0

station_counts["member_pct"] = station_counts["member"] / station_counts["total"] * 100
station_counts["casual_pct"] = station_counts["casual"] / station_counts["total"] * 100

# ---------------------------------------------------------------------------
# Top 10 by member starts / top 10 by casual starts
# ---------------------------------------------------------------------------

member_top = station_counts.nlargest(10, "member")
casual_top = station_counts.nlargest(10, "casual")

print("=" * 68)
print("  Top 10 Stations by Member Starts")
print("=" * 68)
print(f"  {'Station':<38} {'Member':>7} {'Casual':>7} {'Total':>7} {'Mem%':>6}")
print(f"  {'-'*66}")
for station, row in member_top.iterrows():
    print(f"  {station:<38} {int(row['member']):>7,} {int(row['casual']):>7,} "
          f"{int(row['total']):>7,} {row['member_pct']:>5.1f}%")

print()
print("=" * 68)
print("  Top 10 Stations by Casual Starts")
print("=" * 68)
print(f"  {'Station':<38} {'Casual':>7} {'Member':>7} {'Total':>7} {'Cas%':>6}")
print(f"  {'-'*66}")
for station, row in casual_top.iterrows():
    print(f"  {station:<38} {int(row['casual']):>7,} {int(row['member']):>7,} "
          f"{int(row['total']):>7,} {row['casual_pct']:>5.1f}%")

print("=" * 68)

# ---------------------------------------------------------------------------
# Verify zero overlap between the two top 10 lists
# ---------------------------------------------------------------------------

member_set = set(member_top.index)
casual_set = set(casual_top.index)
overlap    = member_set & casual_set

print(f"  Overlap between top 10 lists: {len(overlap)} stations")
print("  Members: transit hubs (commuting)")
print("  Casuals: lakefront/tourist destinations (leisure)")
print("=" * 68)
