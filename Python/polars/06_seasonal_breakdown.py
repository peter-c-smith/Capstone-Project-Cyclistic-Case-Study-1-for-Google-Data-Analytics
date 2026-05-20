"""
06_seasonal_breakdown.py
------------------------
How does ride volume and casual rider percentage vary by season?

Expected output (matching SQL Server, DuckDB, R, and pandas):
  Summer casual %: ~42.7%
  Winter casual %: ~19.6%

Polars notes:
  - .dt.month() extracts the month as an integer (1-12).
  - pl.when().then().when().then()...otherwise() chains multiple conditions
    — Polars' equivalent of a SQL CASE WHEN or pandas dict.map().
  - Categorical ordering: Polars doesn't automatically sort strings by a
    custom order, so we sort by a numeric month key after grouping.
"""

import polars as pl
from utils import load_trips

trips = load_trips()

trips = trips.with_columns(
    pl.col("started_at").dt.month().alias("month_int")
)

trips = trips.with_columns(
    pl.when(pl.col("month_int").is_in([12, 1, 2])).then(pl.lit("Winter"))
    .when(pl.col("month_int").is_in([3, 4, 5])).then(pl.lit("Spring"))
    .when(pl.col("month_int").is_in([6, 7, 8])).then(pl.lit("Summer"))
    .otherwise(pl.lit("Fall"))
    .alias("season")
)

# Season sort order
season_order = {"Spring": 1, "Summer": 2, "Fall": 3, "Winter": 4}

seasonal = (
    trips
    .group_by(["season", "member_casual"])
    .agg(pl.len().alias("rides"))
    .pivot(on="member_casual", index="season", values="rides")
    .with_columns(
        (pl.col("casual") + pl.col("member")).alias("total"),
        (pl.col("casual") / (pl.col("casual") + pl.col("member")) * 100)
        .alias("casual_pct"),
    )
    .with_columns(
        pl.col("season").replace(season_order).alias("sort_key")
    )
    .sort("sort_key")
)

print("=" * 60)
print("  Seasonal Ride Breakdown")
print("=" * 60)
print(f"  {'Season':<10} {'Member':>10} {'Casual':>10} {'Total':>10} {'Casual%':>8}")
print(f"  {'-'*55}")
for row in seasonal.iter_rows(named=True):
    print(f"  {row['season']:<10} {row['member']:>10,} {row['casual']:>10,} "
          f"{row['total']:>10,} {row['casual_pct']:>7.1f}%")

summer = seasonal.filter(pl.col("season") == "Summer")["casual_pct"][0]
winter = seasonal.filter(pl.col("season") == "Winter")["casual_pct"][0]

print(f"\n  Summer casual %: {summer:.1f}%  ({'✓' if abs(summer - 42.7) < 0.2 else '✗'})")
print(f"  Winter casual %: {winter:.1f}%  ({'✓' if abs(winter - 19.6) < 0.2 else '✗'})")
print("=" * 60)
