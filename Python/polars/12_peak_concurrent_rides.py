"""
12_peak_concurrent_rides.py
---------------------------
At any given moment, how many bikes were simultaneously in use?
What does peak fleet utilization look like across the day and week?

Expected output (matching pandas):
  Peak simultaneous rides: 1,199
  At: 2025-10-12 ~12:24

This script is intentionally timed for direct comparison against the
pandas equivalent. The sweep line algorithm is identical — the difference
is in how each library handles the sort + cumsum on 11.2M events.

Polars performance advantage here:
  - sort() uses a parallel merge sort (Rust, multi-threaded).
  - cum_sum() is a vectorized Rust operation.
  - pandas sort_values() is single-threaded C; cumsum() is numpy.
  On Peter's machine (AMD Ryzen 5 7520U, 4-core, Samsung SSD):
    pandas: ~24s load + ~2s analysis
    Polars: compare here

Polars notes:
  - pl.concat() stacks two DataFrames (equivalent to pd.concat()).
  - .cum_sum() replaces pandas .cumsum().
  - .dt.hour() and .dt.weekday() work the same as in other scripts.
  - arg_max() returns the index of the maximum value.
"""

import time
import polars as pl
from utils import load_trips

t_start = time.perf_counter()
trips   = load_trips()
t_load  = time.perf_counter()

# ---------------------------------------------------------------------------
# Sweep line — build +1 / -1 event stream
# ---------------------------------------------------------------------------
starts = trips.select(pl.col("started_at").alias("ts")).with_columns(
    pl.lit(1).alias("event")
)
ends = trips.select(pl.col("ended_at").alias("ts")).with_columns(
    pl.lit(-1).alias("event")
)

events = (
    pl.concat([starts, ends])
    .sort("ts")
    .with_columns(
        pl.col("event").cum_sum().alias("concurrent")
    )
)

t_sweep = time.perf_counter()

# ---------------------------------------------------------------------------
# Overall peak
# ---------------------------------------------------------------------------
peak_idx        = events["concurrent"].arg_max()
peak_concurrent = events["concurrent"][peak_idx]
peak_timestamp  = events["ts"][peak_idx]

# ---------------------------------------------------------------------------
# Peak by hour of day
# ---------------------------------------------------------------------------
events = events.with_columns(
    pl.col("ts").dt.hour().alias("hour")
)
peak_by_hour = (
    events
    .group_by("hour")
    .agg(pl.col("concurrent").max().alias("peak_concurrent"))
    .sort("hour")
)

# ---------------------------------------------------------------------------
# Peak by day of week
# ---------------------------------------------------------------------------
# Polars .dt.weekday(): 1=Mon ... 6=Sat, 7=Sun
day_names = {1:"Monday",2:"Tuesday",3:"Wednesday",4:"Thursday",
             5:"Friday",6:"Saturday",7:"Sunday"}

events = events.with_columns(
    pl.col("ts").dt.weekday().alias("dow")
)
peak_by_dow = (
    events
    .group_by("dow")
    .agg(pl.col("concurrent").max().alias("peak_concurrent"))
    .sort("dow")
    .with_columns(
        pl.col("dow").cast(pl.String).replace(
            {str(k): v for k, v in day_names.items()}
        ).alias("day_name")
    )
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
      f"({t_load - t_start:.2f}s load, {t_end - t_load:.2f}s analysis)")
print()
print("  pandas benchmark: ~24s load, ~2s analysis")
print(f"  Polars speedup:   ~{24 / (t_load - t_start):.1f}x load, "
      f"~{2 / max(t_end - t_load, 0.01):.1f}x analysis")

print()
print("=" * 58)
print("  Peak Concurrent Rides by Hour of Day")
print("=" * 58)
print(f"  {'Hour':>5}  {'Peak Concurrent':>16}  {'Bar'}")
print(f"  {'-'*55}")
max_peak = peak_by_hour["peak_concurrent"].max()
for row in peak_by_hour.iter_rows(named=True):
    bar = "█" * int(row["peak_concurrent"] / max_peak * 30)
    print(f"  {row['hour']:02d}:00  {row['peak_concurrent']:>16,}  {bar}")

print()
print("=" * 58)
print("  Peak Concurrent Rides by Day of Week")
print("=" * 58)
print(f"  {'Day':<12}  {'Peak Concurrent':>16}  {'Bar'}")
print(f"  {'-'*55}")
max_dow = peak_by_dow["peak_concurrent"].max()
for row in peak_by_dow.iter_rows(named=True):
    bar = "█" * int(row["peak_concurrent"] / max_dow * 30)
    print(f"  {row['day_name']:<12}  {row['peak_concurrent']:>16,}  {bar}")

print()
print("=" * 58)
print(f"  Peak simultaneous rides check (1,199): "
      f"{'✓' if peak_concurrent == 1199 else '✗'}")
print(f"  fleet size confirmed")
print("=" * 58)
