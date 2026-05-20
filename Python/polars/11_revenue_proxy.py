"""
11_revenue_proxy.py
-------------------
What is the estimated revenue difference between casual and member
pricing, and what is the potential upside of converting casual riders
to members?

Expected output (matching SQL Server, DuckDB, R, and pandas):
  Casual ride count: 2,015,499
  Annual membership price: $119.88

Polars notes:
  - Duration computed same as script 03 using .dt.total_seconds().
  - Conditional revenue uses pl.when().then().otherwise() inline —
    replaces the pandas apply(lambda row: ...) pattern.
    Polars evaluates this as a vectorized expression, not row by row,
    so it is significantly faster than pandas .apply().
  - This is one of the clearest performance wins for Polars over pandas:
    pandas .apply() is Python-loop speed; Polars expressions are Rust speed.
"""

import polars as pl
from utils import load_trips

trips = load_trips()

UNLOCK_FEE    = 1.00
PER_MIN_RATE  = 0.18
MEMBER_ANNUAL = 9.99 * 12   # $119.88

# Duration
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

# Revenue per group — vectorized expressions (no .apply())
detail = (
    trips
    .group_by(["member_casual", "rideable_type"])
    .agg(
        pl.len().alias("total_rides"),
        pl.col("duration_min").mean().alias("avg_duration"),
        pl.col("duration_min").sum().alias("total_minutes"),
    )
    .with_columns(
        pl.when(pl.col("member_casual") == "casual")
        .then(pl.col("total_rides") * UNLOCK_FEE + pl.col("total_minutes") * PER_MIN_RATE)
        .when(pl.col("rideable_type") == "electric_bike")
        .then(pl.col("total_minutes") * PER_MIN_RATE)
        .otherwise(None)
        .alias("est_revenue")
    )
    .sort(["member_casual", "rideable_type"])
)

print("=" * 65)
print("  Revenue Proxy — Detail by Rider & Bike Type")
print("=" * 65)
print(f"  {'Rider':<10} {'Bike Type':<16} {'Rides':>9} {'Avg Min':>8} {'Est Revenue':>16}")
print(f"  {'-'*63}")
for row in detail.iter_rows(named=True):
    rev = row["est_revenue"]
    rev_str = f"${rev:>14,.2f}" if rev is not None else "  (subscription)"
    print(f"  {row['member_casual']:<10} {row['rideable_type']:<16} "
          f"{row['total_rides']:>9,} {row['avg_duration']:>8.2f} {rev_str:>16}")

# Summary totals
casual_rows  = trips.filter(pl.col("member_casual") == "casual")
member_rows  = trips.filter(pl.col("member_casual") == "member")
ebike_rows   = trips.filter(
    (pl.col("member_casual") == "member") & (pl.col("rideable_type") == "electric_bike")
)

total_casual_rev  = (
    casual_rows.height * UNLOCK_FEE +
    casual_rows["duration_min"].sum() * PER_MIN_RATE
)
member_ebike_rev  = ebike_rows["duration_min"].sum() * PER_MIN_RATE
casual_ride_count = casual_rows.height

print()
print("=" * 65)
print("  Revenue Summary")
print("=" * 65)
print(f"  Est. casual pay-per-ride revenue:  ${total_casual_rev:>14,.2f}")
print(f"  Est. member e-bike overage:        ${member_ebike_rev:>14,.2f}")
print(f"  Member rides (subscription):        {member_rows.height:>14,}")
print(f"  Casual rides (conversion targets):  {casual_ride_count:>14,}")

print()
print("=" * 65)
print("  Conversion Sensitivity — Annual Membership Revenue Upside")
print(f"  ({casual_ride_count:,} casual riders × conversion rate × ${MEMBER_ANNUAL:.2f}/yr)")
print("=" * 65)
print(f"  {'Conversion Rate':>16} {'New Members':>13} {'Annual Revenue Upside':>24}")
print(f"  {'-'*58}")
for rate in [0.05, 0.10, 0.15, 0.20, 0.25]:
    new_members = int(casual_ride_count * rate)
    upside      = new_members * MEMBER_ANNUAL
    print(f"  {rate*100:>14.0f}%  {new_members:>13,}  ${upside:>23,.2f}")
print(f"  {'-'*58}")
print(f"  {'100% (theoretical)':>16}  {casual_ride_count:>13,}  "
      f"${casual_ride_count * MEMBER_ANNUAL:>23,.2f}")
print("=" * 65)
print(f"  2,015,499 check: {'✓' if casual_ride_count == 2_015_499 else '✗'}")
print(f"  119.88 check:    {'✓' if abs(MEMBER_ANNUAL - 119.88) < 0.01 else '✗'}")
print("=" * 65)
