"""
11_revenue_proxy.py
-------------------
What is the estimated revenue difference between casual and member
pricing, and what is the potential upside of converting casual riders
to members?

IMPORTANT: These are illustrative estimates using publicly available
Divvy pricing as of the analysis period. Actual Cyclistic pricing may
differ. The purpose is to frame the conversion opportunity in revenue
terms, not to produce auditable financial figures.

Pricing assumptions (Divvy, ~2025):
  Member:       $9.99/month (~$119.88/yr) unlimited classic rides
                E-bike rides: +$0.18/min overage
  Casual:       $1.00 unlock + $0.18/min (classic or electric)
  Simplification: all casual rides modeled as single-ride.
  Slightly overstates casual revenue (some use day passes) but is
  conservative for the conversion argument.

pandas notes:
  - Duration reuse: ride_time_min is computed exactly as in script 03,
    demonstrating how a shared calculation pattern looks across scripts.
  - groupby().agg() with a custom lambda function computes conditional
    revenue in one pass — avoids multiple filtered groupbys.
  - The conversion sensitivity table uses a simple list comprehension —
    clean, readable Python that needs no special library.

Validates against SQL Server query 14_revenue_proxy.sql and
DuckDB 11_revenue_proxy.py.
"""

import pandas as pd
from utils import load_trips

trips = load_trips()

# Pricing constants — defined once so they're easy to update
UNLOCK_FEE     = 1.00    # casual single-ride unlock fee
PER_MIN_RATE   = 0.18   # per-minute rate (casual rides, member e-bike overage)
MEMBER_MONTHLY = 9.99
MEMBER_ANNUAL  = MEMBER_MONTHLY * 12  # $119.88

# ---------------------------------------------------------------------------
# Ride duration (same approach as script 03)
# ---------------------------------------------------------------------------

trips["duration_min"] = (trips["ended_at"] - trips["started_at"]).dt.total_seconds() / 60
trips.loc[trips["duration_min"] <= 0, "duration_min"] = None

# ---------------------------------------------------------------------------
# Part 1: Detail by rider type and bike type
# ---------------------------------------------------------------------------

detail = (
    trips.groupby(["member_casual", "rideable_type"])
    .agg(
        total_rides   = ("ride_id",       "count"),
        avg_duration  = ("duration_min",  "mean"),
        total_minutes = ("duration_min",  "sum")
    )
    .reset_index()
)

def est_revenue(row):
    """Illustrative revenue per group."""
    if row["member_casual"] == "casual":
        return row["total_rides"] * UNLOCK_FEE + row["total_minutes"] * PER_MIN_RATE
    elif row["rideable_type"] == "electric_bike":
        return row["total_minutes"] * PER_MIN_RATE  # e-bike overage only
    return None  # member classic = subscription, no per-ride charge

detail["est_revenue"] = detail.apply(est_revenue, axis=1)

print("=" * 65)
print("  Revenue Proxy — Detail by Rider & Bike Type")
print("=" * 65)
print(f"  {'Rider':<10} {'Bike Type':<16} {'Rides':>9} {'Avg Min':>8} {'Est Revenue':>16}")
print(f"  {'-'*63}")
for _, row in detail.sort_values(["member_casual", "rideable_type"]).iterrows():
    rev = row["est_revenue"]
    if pd.notna(rev):
        rev_str = f"${rev:>14,.2f}"
    else:
        rev_str = "  (subscription)"
    print(f"  {row['member_casual']:<10} {row['rideable_type']:<16} "
          f"{int(row['total_rides']):>9,} {row['avg_duration']:>8.2f} {rev_str:>16}")

# ---------------------------------------------------------------------------
# Part 2: Summary totals
# ---------------------------------------------------------------------------

casual_mask  = trips["member_casual"] == "casual"
ebike_mask   = trips["rideable_type"] == "electric_bike"
member_mask  = trips["member_casual"] == "member"

total_casual_rev   = (
    casual_mask.sum() * UNLOCK_FEE +
    trips.loc[casual_mask, "duration_min"].sum() * PER_MIN_RATE
)

member_ebike_rev   = trips.loc[member_mask & ebike_mask, "duration_min"].sum() * PER_MIN_RATE
member_ride_count  = member_mask.sum()
casual_ride_count  = casual_mask.sum()

print()
print("=" * 65)
print("  Revenue Summary")
print("=" * 65)
print(f"  Est. casual pay-per-ride revenue:  ${total_casual_rev:>14,.2f}")
print(f"  Est. member e-bike overage:        ${member_ebike_rev:>14,.2f}")
print(f"  Member rides (subscription):        {member_ride_count:>14,}")
print(f"  Casual rides (conversion targets):  {casual_ride_count:>14,}")
print()
print("  Note: Illustrative only. Actual Cyclistic pricing may differ.")
print("  Day pass riders and multi-ride casuals are not separated.")
print("=" * 65)

# ---------------------------------------------------------------------------
# Conversion sensitivity table
# ---------------------------------------------------------------------------

print()
print("=" * 65)
print("  Conversion Sensitivity — Annual Membership Revenue Upside")
print(f"  ({casual_ride_count:,} casual riders × conversion rate × ${MEMBER_ANNUAL:.2f}/yr)")
print("=" * 65)
print(f"  {'Conversion Rate':>16} {'New Members':>13} {'Annual Revenue Upside':>24}")
print(f"  {'-'*58}")
for rate in [0.05, 0.10, 0.15, 0.20, 0.25]:
    new_members = int(casual_ride_count * rate)
    upside = new_members * MEMBER_ANNUAL
    print(f"  {rate*100:>14.0f}%  {new_members:>13,}  ${upside:>23,.2f}")
print(f"  {'-'*58}")
print(f"  {'100% (theoretical)':>16}  {casual_ride_count:>13,}  "
      f"${casual_ride_count * MEMBER_ANNUAL:>23,.2f}")
print("=" * 65)
print("  Present the range — let the marketing team pick the row")
print("  they believe is achievable with their campaign budget.")
print("=" * 65)
