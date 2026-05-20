"""
12_peak_concurrent_rides.py
---------------------------
At any given moment, how many bikes were simultaneously in use?
What does peak fleet utilization look like across the day and week?

This analysis is unique to the Python module — not replicated in SQL Server,
DuckDB, or R. It demonstrates Python's strength for event-based time series
analysis that would be verbose or slow in pure SQL.

Business relevance: Peak concurrent usage sets a floor on fleet size. If
Cyclistic experiences a peak of N simultaneous rides, it needs at least N
bikes available at that moment. This is distinct from total ride volume —
it's about capacity planning, not just demand.

Method — "sweep line" algorithm:
  Each ride generates two events: a +1 at started_at and a -1 at ended_at.
  Sorting all events by timestamp and taking a running cumulative sum gives
  the number of bikes in use at every moment in the dataset. The maximum
  of that cumulative sum is the peak concurrent ride count.

  This is O(n log n) — the sort dominates. For 5.6M rides it produces
  11.2M events. pandas handles this efficiently with vectorised concat
  and sort operations.

pandas notes:
  - pd.concat() stacks two DataFrames of events into one.
  - sort_values() + cumsum() implements the sweep line in two lines.
  - groupby() on date/hour components lets us find peak by hour of day
    and day of week for the capacity planning breakdown.

This script is intentionally run-timed so the result can be compared
directly against the Polars equivalent (polars/12_peak_concurrent_rides.py).
"""

import time
import pandas as pd
from utils import load_trips

t_start = time.perf_counter()

trips = load_trips()

# ---------------------------------------------------------------------------
# Sweep line — build +1 / -1 event stream
#
# Create two DataFrames: one row per ride start (+1) and one per ride end (-1).
# Stack them, sort by timestamp, and cumsum gives concurrent rides at each event.
# ---------------------------------------------------------------------------

starts = pd.DataFrame({"ts": trips["started_at"], "event": 1})
ends   = pd.DataFrame({"ts": trips["ended_at"],   "event": -1})

events = (
    pd.concat([starts, ends], ignore_index=True)
    .sort_values("ts")
    .reset_index(drop=True)
)

events["concurrent"] = events["event"].cumsum()

t_sweep = time.perf_counter()

# ---------------------------------------------------------------------------
# Overall peak
# ---------------------------------------------------------------------------

peak_idx        = events["concurrent"].idxmax()
peak_concurrent = events.loc[peak_idx, "concurrent"]
peak_timestamp  = events.loc[peak_idx, "ts"]

# ---------------------------------------------------------------------------
# Peak by hour of day — flatten to hour, find max concurrent within each hour
# ---------------------------------------------------------------------------

events["hour"] = events["ts"].dt.hour

peak_by_hour = (
    events.groupby("hour")["concurrent"]
    .max()
    .reset_index()
    .rename(columns={"concurrent": "peak_concurrent"})
    .sort_values("hour")
)

# ---------------------------------------------------------------------------
# Peak by day of week
# ---------------------------------------------------------------------------

events["dayofweek"] = events["ts"].dt.dayofweek  # 0=Mon, 6=Sun
day_names = {0:"Monday",1:"Tuesday",2:"Wednesday",3:"Thursday",
             4:"Friday",5:"Saturday",6:"Sunday"}
events["day_name"] = events["dayofweek"].map(day_names)

peak_by_dow = (
    events.groupby(["dayofweek", "day_name"])["concurrent"]
    .max()
    .reset_index()
    .rename(columns={"concurrent": "peak_concurrent"})
    .sort_values("dayofweek")
)

t_end = time.perf_counter()

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

print("=" * 58)
print("  Peak Concurrent Rides — Fleet Utilization Analysis")
print("=" * 58)
print(f"  Peak simultaneous rides:  {peak_concurrent:,}")
print(f"  At timestamp:             {peak_timestamp}")
print(f"  (Minimum fleet size needed to serve peak demand)")
print()
print(f"  Sweep line events processed: {len(events):,}")
print(f"  Elapsed time: {t_end - t_start:.2f}s total "
      f"({t_sweep - t_start:.2f}s load, {t_end - t_sweep:.2f}s analysis)")

print()
print("=" * 58)
print("  Peak Concurrent Rides by Hour of Day")
print("=" * 58)
print(f"  {'Hour':>5}  {'Peak Concurrent':>16}  {'Bar'}")
print(f"  {'-'*55}")
max_peak = peak_by_hour["peak_concurrent"].max()
for _, row in peak_by_hour.iterrows():
    bar = "█" * int(row["peak_concurrent"] / max_peak * 30)
    print(f"  {int(row['hour']):02d}:00  {int(row['peak_concurrent']):>16,}  {bar}")

print()
print("=" * 58)
print("  Peak Concurrent Rides by Day of Week")
print("=" * 58)
print(f"  {'Day':<12}  {'Peak Concurrent':>16}  {'Bar'}")
print(f"  {'-'*55}")
max_dow = peak_by_dow["peak_concurrent"].max()
for _, row in peak_by_dow.iterrows():
    bar = "█" * int(row["peak_concurrent"] / max_dow * 30)
    print(f"  {row['day_name']:<12}  {int(row['peak_concurrent']):>16,}  {bar}")

print()
print("=" * 58)
print("  Note: Peak concurrent rides sets a floor on fleet size.")
print("  Converting casual riders to members changes their pricing")
print("  model, not their riding behavior — peak demand stays stable")
print("  at conversion. If members ride more frequently over time")
print("  (zero marginal cost per ride), fleet demand could grow,")
print("  but that is a secondary, longer-term effect.")
print("=" * 58)
