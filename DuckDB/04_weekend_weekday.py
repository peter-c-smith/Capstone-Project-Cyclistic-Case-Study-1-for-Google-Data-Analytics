"""
04_weekend_weekday.py
---------------------
Do casual riders concentrate their usage on weekends more than members?

Key finding: Casual riders are 1.61x more likely to ride on weekends —
strong evidence of leisure use vs. member commuting patterns.

DuckDB notes:
  - DAYOFWEEK() returns 0=Sunday, 1=Monday ... 6=Saturday.
    SQL Server's DATEPART(WEEKDAY, ...) uses 1=Sunday, 7=Saturday.
    Same logic, different numbering — weekend is still Sun + Sat.
  - FILTER (WHERE ...) again replaces nested CASE WHEN / NULLIF patterns,
    making the conditional aggregations much easier to read.
  - No CAST needed around ROUND() — DuckDB returns clean numerics.

Validates against SQL Server query 07_weekend_weekday.sql
  Expected: ~24% member weekend | ~38% casual weekend | ratio 1.61
"""

import duckdb
from pathlib import Path

CSV_PATH = str(Path(__file__).parent.parent / "Data" / "DATAfile_Consolidated" / "*.csv")

con = duckdb.connect()

result = con.execute(f"""
    WITH WeekendFlags AS (
        SELECT
            member_casual,
            -- DAYOFWEEK: 0=Sunday, 6=Saturday
            DAYOFWEEK(started_at) IN (0, 6) AS is_weekend
        FROM read_csv_auto('{CSV_PATH}')
    )
    SELECT
        -- Overall split
        COUNT(*) FILTER (WHERE is_weekend)              AS weekend_rides,
        COUNT(*) FILTER (WHERE NOT is_weekend)          AS weekday_rides,
        ROUND(100.0 * COUNT(*) FILTER (WHERE is_weekend) / COUNT(*), 1) AS weekend_pct,

        -- Member weekend %
        ROUND(100.0 *
            COUNT(*) FILTER (WHERE member_casual = 'member' AND is_weekend) /
            COUNT(*) FILTER (WHERE member_casual = 'member')
        , 1) AS member_weekend_pct,

        -- Casual weekend %
        ROUND(100.0 *
            COUNT(*) FILTER (WHERE member_casual = 'casual' AND is_weekend) /
            COUNT(*) FILTER (WHERE member_casual = 'casual')
        , 1) AS casual_weekend_pct,

        -- Weekend skew ratio
        ROUND(
            (100.0 * COUNT(*) FILTER (WHERE member_casual = 'casual' AND is_weekend) /
                     COUNT(*) FILTER (WHERE member_casual = 'casual'))
            /
            (100.0 * COUNT(*) FILTER (WHERE member_casual = 'member' AND is_weekend) /
                     COUNT(*) FILTER (WHERE member_casual = 'member'))
        , 2) AS weekend_skew_ratio

    FROM WeekendFlags
""").fetchone()

(weekend_rides, weekday_rides, weekend_pct,
 member_weekend_pct, casual_weekend_pct, skew_ratio) = result

print("=" * 50)
print("  Weekend vs Weekday Riding Patterns")
print("=" * 50)
print(f"  Weekend rides:   {weekend_rides:,}  ({weekend_pct}%)")
print(f"  Weekday rides:   {weekday_rides:,}  ({100 - weekend_pct:.1f}%)")
print(f"")
print(f"  {'':30s} {'Pct Weekend':>11}")
print(f"  {'-'*42}")
print(f"  {'Members':30s} {member_weekend_pct:>10.1f}%")
print(f"  {'Casual riders':30s} {casual_weekend_pct:>10.1f}%")
print(f"  {'-'*42}")
print(f"  Weekend skew ratio (casual/member): {skew_ratio:.2f}x")
print("=" * 50)
print("  Casual riders are {:.2f}x more likely to ride on".format(skew_ratio))
print("  weekends — consistent with leisure, not commuting.")
print("=" * 50)
