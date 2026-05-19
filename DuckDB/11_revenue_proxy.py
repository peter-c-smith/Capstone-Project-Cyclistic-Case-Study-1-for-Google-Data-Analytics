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
  This slightly overstates casual revenue (some use day passes)
  but is conservative for the conversion argument.

DuckDB notes:
  - epoch() used again for duration, consistent with 03_avg_duration_distance.py
  - CASE WHEN inside aggregates works identically to SQL Server
  - No new syntax — this script is about the business framing, not DuckDB features
  - Inline subquery in FROM clause works the same as SQL Server

Validates against SQL Server query 14_revenue_proxy.sql
"""

import duckdb
from pathlib import Path

CSV_PATH = str(Path(__file__).parent.parent / "Data" / "DATAfile_Consolidated" / "*.csv")

# Pricing constants — defined once so they're easy to update
UNLOCK_FEE       = 1.00   # casual single-ride unlock
PER_MIN_RATE     = 0.18   # per-minute rate (casual classic, casual electric, member e-bike)
MEMBER_MONTHLY   = 9.99   # member monthly subscription
MEMBER_ANNUAL    = MEMBER_MONTHLY * 12  # $119.88

con = duckdb.connect()

# ── Part 1: Detail by rider type and bike type ───────────────────────────────
detail = con.execute(f"""
    WITH RideMetrics AS (
        SELECT
            member_casual,
            rideable_type,
            COUNT(*)                                                    AS total_rides,
            AVG(CASE WHEN epoch(ended_at - started_at) / 60.0 > 0
                     THEN epoch(ended_at - started_at) / 60.0 END)     AS avg_duration_min,
            SUM(CASE WHEN epoch(ended_at - started_at) / 60.0 > 0
                     THEN epoch(ended_at - started_at) / 60.0 END)     AS total_minutes
        FROM read_csv_auto('{CSV_PATH}')
        GROUP BY member_casual, rideable_type
    )
    SELECT
        member_casual,
        rideable_type,
        total_rides,
        ROUND(avg_duration_min, 2)                                      AS avg_duration_min,
        CASE WHEN member_casual = 'casual'
             THEN ROUND(total_rides * {UNLOCK_FEE} + total_minutes * {PER_MIN_RATE}, 2)
             ELSE NULL END                                              AS est_casual_revenue,
        CASE WHEN member_casual = 'member' AND rideable_type = 'electric_bike'
             THEN ROUND(total_minutes * {PER_MIN_RATE}, 2)
             ELSE NULL END                                              AS est_member_ebike_overage
    FROM RideMetrics
    ORDER BY member_casual, rideable_type
""").fetchall()

# ── Part 2: Summary totals ────────────────────────────────────────────────────
summary = con.execute(f"""
    WITH base AS (
        SELECT
            member_casual,
            rideable_type,
            COUNT(*)                                                    AS total_rides,
            SUM(CASE WHEN epoch(ended_at - started_at) / 60.0 > 0
                     THEN epoch(ended_at - started_at) / 60.0 END)     AS total_minutes
        FROM read_csv_auto('{CSV_PATH}')
        GROUP BY member_casual, rideable_type
    )
    SELECT
        SUM(CASE WHEN member_casual = 'casual'
                 THEN total_rides * {UNLOCK_FEE} + total_minutes * {PER_MIN_RATE}
                 ELSE 0 END)                                            AS total_casual_revenue,
        SUM(CASE WHEN member_casual = 'member' AND rideable_type = 'electric_bike'
                 THEN total_minutes * {PER_MIN_RATE}
                 ELSE 0 END)                                            AS member_ebike_overage,
        SUM(CASE WHEN member_casual = 'member'
                 THEN total_rides ELSE 0 END)                           AS member_ride_count,
        SUM(CASE WHEN member_casual = 'casual'
                 THEN total_rides ELSE 0 END)                           AS casual_ride_count
    FROM base
""").fetchone()

total_casual_rev, member_ebike_overage, member_rides, casual_rides = summary

print("=" * 62)
print("  Revenue Proxy — Detail by Rider & Bike Type")
print("=" * 62)
print(f"  {'Rider':<10} {'Bike Type':<16} {'Rides':>9} {'Avg Min':>8} {'Est Revenue':>13}")
print(f"  {'-'*60}")
for row in detail:
    rider, bike, rides, avg_min, casual_rev, member_overage = row
    rev = casual_rev if casual_rev is not None else member_overage
    rev_str = f"${rev:>12,.2f}" if rev is not None else "  (subscription)"
    print(f"  {rider:<10} {bike:<16} {rides:>9,} {avg_min:>8.2f} {rev_str:>13}")

print()
print("=" * 62)
print("  Revenue Summary")
print("=" * 62)
print(f"  Est. casual pay-per-ride revenue:  ${total_casual_rev:>12,.2f}")
print(f"  Est. member e-bike overage:        ${member_ebike_overage:>12,.2f}")
print(f"  Member rides (subscription):        {member_rides:>12,}")
print(f"  Casual rides (conversion targets):  {casual_rides:>12,}")
print()
print("  Note: Illustrative only. Actual Cyclistic pricing may differ.")
print("  Day pass riders and multi-ride casuals are not separated.")
print("=" * 62)

# ── Conversion sensitivity table ─────────────────────────────────────────────
print()
print("=" * 62)
print("  Conversion Sensitivity — Annual Membership Revenue Upside")
print(f"  ({casual_rides:,} casual riders × conversion rate × ${MEMBER_ANNUAL:.2f}/yr)")
print("=" * 62)
print(f"  {'Conversion Rate':>16} {'New Members':>13} {'Annual Revenue Upside':>22}")
print(f"  {'-'*56}")
for rate in [0.05, 0.10, 0.15, 0.20, 0.25]:
    new_members = int(casual_rides * rate)
    upside = new_members * MEMBER_ANNUAL
    print(f"  {rate*100:>14.0f}%  {new_members:>13,}  ${upside:>21,.2f}")
print(f"  {'-'*56}")
print(f"  {'100% (theoretical)':>16}  {casual_rides:>13,}  ${casual_rides * MEMBER_ANNUAL:>21,.2f}")
print("=" * 62)
print("  Present the range — let the marketing team pick the row")
print("  they believe is achievable with their campaign budget.")
print("=" * 62)
