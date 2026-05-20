"""
10_missing_station_data.py
--------------------------
How prevalent is missing station data, and what does it reveal about
how electric bikes track location differently from classic bikes?

Expected output (matching SQL Server, DuckDB, R, and pandas):
  classic_bike: ~0% missing station data
  electric_bike: ~32% missing station data
  100% of missing-station e-bike rides still have GPS coordinates

Key inference: E-bikes have onboard GPS hardware. Missing station names
are NOT a data quality gap — coordinates are present and fully usable.

Polars notes:
  - is_null() | (str.strip_chars() == "") replicates pandas is_missing().
  - cast(pl.Int32) converts boolean True/False to 1/0 for summation.
  - Conditional aggregation uses pl.col().filter() — cleaner than pandas
    lambda inside .agg().
"""

import polars as pl
from utils import load_trips

trips = load_trips()

# Missing station flags
trips = trips.with_columns(
    (
        pl.col("start_station_name").is_null() |
        (pl.col("start_station_name").str.strip_chars() == "")
    ).alias("missing_start"),
    (
        pl.col("end_station_name").is_null() |
        (pl.col("end_station_name").str.strip_chars() == "")
    ).alias("missing_end"),
)
trips = trips.with_columns(
    (pl.col("missing_start") & pl.col("missing_end")).alias("missing_both")
)

total = trips.height

print("=" * 55)
print("  Part 1: Overall Missing Station Data")
print("=" * 55)
for label, col in [("Missing start station", "missing_start"),
                   ("Missing end station",   "missing_end"),
                   ("Missing both",          "missing_both")]:
    n   = trips[col].sum()
    pct = n / total * 100
    print(f"  {label}: {n:>9,}  ({pct:.1f}%)")

# Part 2: by rider and bike type
by_type = (
    trips
    .group_by(["member_casual", "rideable_type"])
    .agg(
        pl.len().alias("total_rides"),
        pl.col("missing_start").sum().alias("missing_start"),
    )
    .with_columns(
        (pl.col("missing_start") / pl.col("total_rides") * 100)
        .alias("missing_pct")
    )
    .sort(["member_casual", "rideable_type"])
)

print()
print("=" * 55)
print("  Part 2: Missing Start Station by Rider & Bike Type")
print("=" * 55)
print(f"  {'Rider':<10} {'Bike Type':<16} {'Total':>9} {'Missing':>9} {'Miss%':>7}")
print(f"  {'-'*53}")
for row in by_type.iter_rows(named=True):
    print(f"  {row['member_casual']:<10} {row['rideable_type']:<16} "
          f"{row['total_rides']:>9,} {row['missing_start']:>9,} "
          f"{row['missing_pct']:>6.1f}%")

# Part 3: GPS check
missing_ebike = trips.filter(
    pl.col("missing_start") & (pl.col("rideable_type") == "electric_bike")
)
has_gps = missing_ebike.filter(
    pl.col("start_lat").is_not_null() & pl.col("start_lng").is_not_null()
)
gps_pct = has_gps.height / missing_ebike.height * 100 if missing_ebike.height > 0 else 0

print()
print("=" * 55)
print("  Part 3: Missing Station — But GPS Coordinates Present?")
print("=" * 55)
print(f"  E-bike rides missing station name:  {missing_ebike.height:>9,}")
print(f"  Of those, has GPS coordinates:      {has_gps.height:>9,}")
print(f"  GPS coverage:                       {gps_pct:>8.1f}%")
print()
print(f"  100% GPS check: {'✓' if abs(gps_pct - 100.0) < 0.1 else '✗'}")
print()
print("  Inference: E-bikes have onboard GPS hardware.")
print("  Missing station names are NOT a data quality gap.")
print("  onboard GPS hardware confirmed by data structure.")
print("=" * 55)
