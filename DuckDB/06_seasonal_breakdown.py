"""
06_seasonal_breakdown.py
------------------------
How does ridership vary by season, and do casual riders show stronger
seasonal concentration than members?

Key finding: Casual ridership peaks at 42.7% of summer rides, drops to
19.6% in winter — far more seasonal than members, who ride year-round.

DuckDB notes:
  - MONTH() works identically to SQL Server's MONTH() — no change needed.
  - strftime() formats timestamps as strings. SQL Server used FORMAT().
    strftime('%Y-%m', started_at) is the DuckDB equivalent of
    FORMAT(started_at, 'yyyy-MM').
  - Season ORDER BY uses the same CASE trick as SQL Server — DuckDB
    supports this pattern identically.
  - Two result sets in one script: monthly detail + season rollup.
    Each is its own con.execute() call, same connection.

Season definitions (Northern Hemisphere, matches SQL Server):
  Spring: March, April, May       (months 3, 4, 5)
  Summer: June, July, August      (months 6, 7, 8)
  Fall:   September, October, Nov (months 9, 10, 11)
  Winter: December, January, Feb  (months 12, 1, 2)

Validates against SQL Server query 10_seasonal_breakdown.sql
  Expected summer casual %: ~42.7% | winter casual %: ~19.6%
"""

import duckdb
from pathlib import Path

CSV_PATH = str(Path(__file__).parent.parent / "Data" / "DATAfile_Consolidated" / "*.csv")

con = duckdb.connect()

# ── Part 1: Monthly breakdown ────────────────────────────────────────────────
monthly = con.execute(f"""
    SELECT
        strftime(started_at, '%Y-%m')                   AS ride_month,
        COUNT(*)                                        AS total_rides,
        COUNT(*) FILTER (WHERE member_casual = 'member') AS member_rides,
        COUNT(*) FILTER (WHERE member_casual = 'casual') AS casual_rides,
        ROUND(100.0 *
            COUNT(*) FILTER (WHERE member_casual = 'casual') / COUNT(*), 1) AS casual_pct
    FROM read_csv_auto('{CSV_PATH}')
    GROUP BY ride_month
    ORDER BY ride_month
""").fetchall()

print("=" * 57)
print("  Monthly Breakdown")
print("=" * 57)
print(f"  {'Month':<10} {'Total':>9} {'Member':>9} {'Casual':>9} {'Casual%':>8}")
print(f"  {'-'*55}")
for row in monthly:
    month, total, member, casual, casual_pct = row
    print(f"  {month:<10} {total:>9,} {member:>9,} {casual:>9,} {casual_pct:>7.1f}%")

# ── Part 2: Season rollup ────────────────────────────────────────────────────
seasonal = con.execute(f"""
    WITH SeasonRollup AS (
        SELECT
            CASE
                WHEN MONTH(started_at) IN (3,4,5)   THEN 'Spring'
                WHEN MONTH(started_at) IN (6,7,8)   THEN 'Summer'
                WHEN MONTH(started_at) IN (9,10,11) THEN 'Fall'
                ELSE                                     'Winter'
            END                                         AS season,
            member_casual
        FROM read_csv_auto('{CSV_PATH}')
    )
    SELECT
        season,
        COUNT(*)                                        AS total_rides,
        COUNT(*) FILTER (WHERE member_casual = 'member') AS member_rides,
        COUNT(*) FILTER (WHERE member_casual = 'casual') AS casual_rides,
        ROUND(100.0 *
            COUNT(*) FILTER (WHERE member_casual = 'member') / COUNT(*), 1) AS member_pct,
        ROUND(100.0 *
            COUNT(*) FILTER (WHERE member_casual = 'casual') / COUNT(*), 1) AS casual_pct
    FROM SeasonRollup
    GROUP BY season
    ORDER BY
        CASE season
            WHEN 'Spring' THEN 1
            WHEN 'Summer' THEN 2
            WHEN 'Fall'   THEN 3
            ELSE               4
        END
""").fetchall()

print()
print("=" * 57)
print("  Seasonal Rollup")
print("=" * 57)
print(f"  {'Season':<10} {'Total':>9} {'Member':>9} {'Casual':>9} {'Casual%':>8}")
print(f"  {'-'*55}")
for row in seasonal:
    season, total, member, casual, member_pct, casual_pct = row
    print(f"  {season:<10} {total:>9,} {member:>9,} {casual:>9,} {casual_pct:>7.1f}%")
print("=" * 57)
