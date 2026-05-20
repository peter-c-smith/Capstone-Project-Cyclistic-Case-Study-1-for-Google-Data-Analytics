"""
02_core_ride_counts.py
----------------------
How many rides did members vs casual riders take, and what percentage
of total rides does each group represent?

Expected output (matching SQL Server, DuckDB, R, and pandas):
  member: 3,605,045  (64.1%)
  casual: 2,015,499  (35.9%)

Polars notes:
  - value_counts() works similarly to pandas but returns a Polars DataFrame.
  - sort() on a DataFrame column replaces pandas .sort_values().
  - Expressions use pl.col() — the core building block of Polars syntax.
  - with_columns() adds new columns using expressions — equivalent to
    pandas df["new_col"] = ... but evaluated lazily and in parallel.
"""

import polars as pl
from utils import load_trips

trips = load_trips()

counts = (
    trips
    .group_by("member_casual")
    .agg(pl.len().alias("rides"))
    .with_columns(
        (pl.col("rides") / pl.col("rides").sum() * 100)
        .alias("pct")
    )
    .sort("member_casual")
)

total = trips.height   # .height = row count in Polars (vs len() in pandas)

print("=" * 50)
print("  Core Ride Counts — Member vs Casual")
print("=" * 50)
for row in counts.iter_rows(named=True):
    print(f"  {row['member_casual']:<10}  {row['rides']:>10,}  ({row['pct']:.1f}%)")
print(f"  {'Total':<10}  {total:>10,}")
print()

member_pct = counts.filter(pl.col("member_casual") == "member")["pct"][0]
casual_pct = counts.filter(pl.col("member_casual") == "casual")["pct"][0]

print(f"  Members: {member_pct:.1f}%  |  Casuals: {casual_pct:.1f}%")
print(f"  Matches SQL Server: {'✓' if abs(member_pct - 64.1) < 0.05 else '✗'}")
print("=" * 50)
