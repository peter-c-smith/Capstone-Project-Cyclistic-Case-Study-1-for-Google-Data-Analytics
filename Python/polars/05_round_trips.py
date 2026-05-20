"""
05_round_trips.py
-----------------
What percentage of rides start and end at the same station (round trips)?
Do casual riders make more round trips than members?

Expected output (matching SQL Server, DuckDB, R, and pandas):
  Casual round trip rate: ~18.1%
  Member round trip rate: ~11.1%
  Ratio: ~1.63x

Polars notes:
  - Null equality: in Polars, null != null by default (same as SQL).
    To replicate DAX BLANK() = BLANK() = TRUE behavior, fill nulls with
    an empty string before comparing — same fix as pandas .fillna("").
  - pl.col().fill_null("") fills null values in a string column.
  - Comparing two expressions: pl.col("a") == pl.col("b") works inline
    inside with_columns() — no need for a separate boolean mask.
"""

import polars as pl
from utils import load_trips

trips = load_trips()

# Fill nulls before comparing — replicates DAX BLANK() = BLANK() = TRUE
trips = trips.with_columns(
    (
        pl.col("start_station_name").fill_null("") ==
        pl.col("end_station_name").fill_null("")
    ).alias("is_round_trip")
)

summary = (
    trips
    .group_by("member_casual")
    .agg(
        pl.len().alias("total_rides"),
        pl.col("is_round_trip").sum().alias("round_trips"),
    )
    .with_columns(
        (pl.col("round_trips") / pl.col("total_rides") * 100)
        .alias("round_trip_pct")
    )
    .sort("member_casual")
)

print("=" * 55)
print("  Round Trip Analysis by Rider Type")
print("=" * 55)
print(f"  {'Rider':<10} {'Total':>10} {'Round Trips':>12} {'RT%':>8}")
print(f"  {'-'*45}")
for row in summary.iter_rows(named=True):
    print(f"  {row['member_casual']:<10} {row['total_rides']:>10,} "
          f"{row['round_trips']:>12,} {row['round_trip_pct']:>7.1f}%")

casual_pct = summary.filter(pl.col("member_casual") == "casual")["round_trip_pct"][0]
member_pct = summary.filter(pl.col("member_casual") == "member")["round_trip_pct"][0]
ratio = casual_pct / member_pct

print(f"\n  Casual/member round trip ratio: {ratio:.2f}x")
print(f"  Ratio 1.63x check:  {'✓' if abs(ratio - 1.63) < 0.02 else '✗'}")
print(f"\n  Note: fill_null('') replicates DAX BLANK() = BLANK() behavior.")
print("=" * 55)
