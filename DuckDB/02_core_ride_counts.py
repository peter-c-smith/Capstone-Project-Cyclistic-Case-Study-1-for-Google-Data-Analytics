"""
02_core_ride_counts.py
----------------------
How are rides distributed between annual members and casual riders?

DuckDB notes:
  - FILTER (WHERE ...) is a cleaner alternative to CASE WHEN for conditional counts
  - ROUND() returns a numeric directly — no need to CAST like SQL Server
  - read_csv_auto() + glob replaces the SQL Server FROM dbo.Trips

Validates against SQL Server query 05_core_ride_counts.sql
  Expected: 5,620,544 total | 3,605,045 member | 2,015,499 casual
"""

import duckdb
from pathlib import Path

CSV_PATH = str(Path(__file__).parent.parent / "Data" / "DATAfile_Consolidated" / "*.csv")

con = duckdb.connect()

result = con.execute(f"""
    SELECT
        COUNT(*)                                                AS total_rides,

        -- FILTER (WHERE ...) is a DuckDB/standard SQL shorthand for CASE WHEN
        COUNT(*) FILTER (WHERE member_casual = 'member')       AS member_rides,
        COUNT(*) FILTER (WHERE member_casual = 'casual')       AS casual_rides,

        -- Percentages — ROUND() works cleanly without CAST in DuckDB
        ROUND(100.0 * COUNT(*) FILTER (WHERE member_casual = 'member') / COUNT(*), 1) AS member_pct,
        ROUND(100.0 * COUNT(*) FILTER (WHERE member_casual = 'casual') / COUNT(*), 1) AS casual_pct

    FROM read_csv_auto('{CSV_PATH}')
""").fetchone()

total, members, casuals, member_pct, casual_pct = result

print("=" * 45)
print("  Core Ride Counts")
print("=" * 45)
print(f"  Total rides:    {total:,}")
print(f"  Member rides:   {members:,}  ({member_pct}%)")
print(f"  Casual rides:   {casuals:,}  ({casual_pct}%)")
print("=" * 45)
