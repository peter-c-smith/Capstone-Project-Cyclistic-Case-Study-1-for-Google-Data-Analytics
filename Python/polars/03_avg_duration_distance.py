"""
03_avg_duration_distance.py
---------------------------
What is the average ride duration and distance for members vs casual riders?

Expected output (matching SQL Server, DuckDB, R, and pandas):
  member:  ~12.4 min,  ~1.44 mi
  casual:  ~22.6 min,  ~1.49 mi
  Duration ratio: ~1.82x
  Distance ratio: ~1.03x

Polars notes:
  - Duration: subtract two Datetime columns → Polars returns a Duration type.
    .dt.total_seconds() converts to integer seconds; divide by 60 for minutes.
  - Haversine: Polars has no built-in distance function, so we use the same
    numpy vectorized formula as pandas — extract columns as numpy arrays,
    compute, then add back as a new column with pl.Series().
  - with_columns() + pl.when().then().otherwise() replaces pandas .loc[] masking
    for conditional null-setting (zeroing out invalid durations/distances).
"""

import polars as pl
import numpy as np
from utils import load_trips

trips = load_trips()

# ---------------------------------------------------------------------------
# Duration
# ---------------------------------------------------------------------------
trips = trips.with_columns(
    ((pl.col("ended_at") - pl.col("started_at")).dt.total_seconds() / 60)
    .alias("duration_min")
)
trips = trips.with_columns(
    pl.when(pl.col("duration_min") <= 0)
    .then(None)
    .otherwise(pl.col("duration_min"))
    .alias("duration_min")
)

# ---------------------------------------------------------------------------
# Haversine distance — via numpy (same formula as pandas script 03)
# ---------------------------------------------------------------------------
R_EARTH = 3958.8
lat1 = np.radians(trips["start_lat"].to_numpy())
lat2 = np.radians(trips["end_lat"].to_numpy())
dlat = lat2 - lat1
dlng = np.radians(
    (trips["end_lng"] - trips["start_lng"]).to_numpy()
)
a    = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlng/2)**2
dist = R_EARTH * 2 * np.arcsin(np.sqrt(a))

trips = trips.with_columns(
    pl.Series("distance_mi", dist)
)
trips = trips.with_columns(
    pl.when(pl.col("distance_mi") <= 0)
    .then(None)
    .otherwise(pl.col("distance_mi"))
    .alias("distance_mi")
)

# ---------------------------------------------------------------------------
# Averages by rider type
# ---------------------------------------------------------------------------
avgs = (
    trips
    .group_by("member_casual")
    .agg(
        pl.col("duration_min").mean().alias("avg_duration"),
        pl.col("distance_mi").mean().alias("avg_distance"),
    )
    .sort("member_casual")
)

member = avgs.filter(pl.col("member_casual") == "member").row(0, named=True)
casual = avgs.filter(pl.col("member_casual") == "casual").row(0, named=True)

dur_ratio  = casual["avg_duration"] / member["avg_duration"]
dist_ratio = casual["avg_distance"] / member["avg_distance"]

print("=" * 55)
print("  Avg Duration & Distance by Rider Type")
print("=" * 55)
print(f"  {'Rider':<10} {'Avg Duration':>14} {'Avg Distance':>14}")
print(f"  {'-'*52}")
for row in avgs.iter_rows(named=True):
    print(f"  {row['member_casual']:<10} {row['avg_duration']:>12.2f} min "
          f"{row['avg_distance']:>12.2f} mi")
print(f"  {'Casual/Member':<10}  {dur_ratio:>11.2f}x    {dist_ratio:>11.2f}x")
print()
print(f"  Duration ratio 1.82x: {'✓' if abs(dur_ratio - 1.82) < 0.02 else '✗'}")
print(f"  Distance ratio 1.03x: {'✓' if abs(dist_ratio - 1.03) < 0.02 else '✗'}")
print("=" * 55)
