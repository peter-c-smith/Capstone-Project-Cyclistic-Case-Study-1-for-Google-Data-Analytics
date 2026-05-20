"""
03_avg_duration_distance.py
---------------------------
Average ride duration and distance by member type.

Key finding: Casual riders take ~1.82x longer rides but cover only ~1.03x more
distance — they ride slowly and leisurely, not to get somewhere fast.

pandas notes:
  - Duration: timedelta arithmetic via (ended_at - started_at); .dt.total_seconds()
    extracts the seconds as a float. Negative durations are set to NaN.
  - Distance: Haversine formula vectorised with numpy — no loops needed.
    numpy's broadcast arithmetic applies the formula across all 5.6M rows at once.
  - groupby().agg() produces per-group averages in one pass.

Expected output (matching SQL Server, DuckDB, and R):
    Overall avg duration:  ~16.06 min
    Casual / member duration ratio: 1.82x
    Casual / member distance ratio: 1.03x
"""

import numpy as np
import pandas as pd
from utils import load_trips

trips = load_trips()

# ---------------------------------------------------------------------------
# Duration (minutes)
#
# pandas timedelta subtraction produces a Timedelta Series.
# .dt.total_seconds() converts to float seconds; divide by 60 for minutes.
# Negative durations (data errors) become NaN so they're excluded from AVG.
# ---------------------------------------------------------------------------

trips["duration_min"] = (trips["ended_at"] - trips["started_at"]).dt.total_seconds() / 60
trips.loc[trips["duration_min"] <= 0, "duration_min"] = np.nan

# ---------------------------------------------------------------------------
# Distance (miles) — vectorised Haversine formula
#
# Haversine gives the straight-line ("as the crow flies") distance between
# two GPS points on the Earth's surface. Returns ~0 for round trips where
# start and end coordinates are the same.
# ---------------------------------------------------------------------------

R_EARTH = 3958.8  # Earth radius in miles

lat1 = np.radians(trips["start_lat"])
lat2 = np.radians(trips["end_lat"])
lng1 = np.radians(trips["start_lng"])
lng2 = np.radians(trips["end_lng"])

dlat = lat2 - lat1
dlng = lng2 - lng1

a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlng / 2)**2
trips["distance_mi"] = R_EARTH * 2 * np.arcsin(np.sqrt(a))

# Zero distances (round trips / missing coords) → NaN so they don't pull
# the average down to zero
trips.loc[trips["distance_mi"] <= 0, "distance_mi"] = np.nan

# ---------------------------------------------------------------------------
# Averages by member type
# ---------------------------------------------------------------------------

stats = trips.groupby("member_casual")[["duration_min", "distance_mi"]].mean()
overall_dur  = trips["duration_min"].mean()
overall_dist = trips["distance_mi"].mean()

mem_dur  = stats.loc["member", "duration_min"]
mem_dist = stats.loc["member", "distance_mi"]
cas_dur  = stats.loc["casual", "duration_min"]
cas_dist = stats.loc["casual", "distance_mi"]

dur_ratio  = cas_dur  / mem_dur
dist_ratio = cas_dist / mem_dist

print("=" * 55)
print("  Avg Ride Duration & Distance")
print("=" * 55)
print(f"  {'':25s} {'Member':>8}  {'Casual':>8}  {'All':>8}")
print(f"  {'-'*53}")
print(f"  {'Avg duration (min)':25s} {mem_dur:>8.2f}  {cas_dur:>8.2f}  {overall_dur:>8.2f}")
print(f"  {'Avg distance (mi)':25s} {mem_dist:>8.2f}  {cas_dist:>8.2f}  {overall_dist:>8.2f}")
print(f"  {'-'*53}")
print(f"  Duration ratio (casual/member): {dur_ratio:.2f}x")
print(f"  Distance ratio (casual/member): {dist_ratio:.2f}x")
print("=" * 55)
print("  Casual riders take longer rides but barely go farther —")
print("  they ride slowly for leisure, not to commute.")
print("=" * 55)
