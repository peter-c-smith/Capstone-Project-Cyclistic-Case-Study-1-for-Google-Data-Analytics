"""
04_weekend_weekday.py
---------------------
Do members and casual riders show different weekend vs weekday patterns?

Expected output (matching SQL Server, DuckDB, R, and pandas):
  Casual weekend/weekday ratio: ~1.61x

Polars notes:
  - .dt.weekday() returns 1=Monday through 7=Sunday (ISO 8601).
    This differs from pandas (.dt.dayofweek: 0=Mon, 6=Sun) and
    DuckDB (DAYOFWEEK: 0=Sun, 6=Sat). Always check the reference day.
  - Weekend in Polars: weekday >= 6 (Saturday=6, Sunday=7).
  - pl.when().then().otherwise() creates conditional columns inline.
"""

import polars as pl
from utils import load_trips

trips = load_trips()

# Polars .dt.weekday(): 1=Mon, 2=Tue, ..., 6=Sat, 7=Sun
trips = trips.with_columns(
    pl.when(pl.col("started_at").dt.weekday() >= 6)
    .then(pl.lit("weekend"))
    .otherwise(pl.lit("weekday"))
    .alias("day_type")
)

wk = (
    trips
    .group_by(["member_casual", "day_type"])
    .agg(pl.len().alias("rides"))
    .sort(["member_casual", "day_type"])
)

print("=" * 55)
print("  Weekend vs Weekday Rides by Rider Type")
print("=" * 55)
print(f"  {'Rider':<10} {'Day Type':<10} {'Rides':>10}")
print(f"  {'-'*35}")
for row in wk.iter_rows(named=True):
    print(f"  {row['member_casual']:<10} {row['day_type']:<10} {row['rides']:>10,}")

# Ratio
def get_rides(rider, day):
    return wk.filter(
        (pl.col("member_casual") == rider) & (pl.col("day_type") == day)
    )["rides"][0]

for rider in ["member", "casual"]:
    wkend = get_rides(rider, "weekend")
    wkday = get_rides(rider, "weekday")
    ratio = wkend / wkday
    print(f"\n  {rider.capitalize()} weekend/weekday ratio: {ratio:.2f}x")

casual_ratio = get_rides("casual", "weekend") / get_rides("casual", "weekday")
print(f"\n  Casual 1.61x check: {'✓' if abs(casual_ratio - 1.61) < 0.02 else '✗'}")
print("=" * 55)
