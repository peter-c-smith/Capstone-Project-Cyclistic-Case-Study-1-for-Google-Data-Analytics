"""
07_bike_type_mix.py
-------------------
Do casual riders and members prefer different bike types?

Key finding (null result): Bike type preference is nearly identical between
members and casuals (~65% electric for both groups). This is NOT a meaningful
behavioral differentiator — worth including because a good analysis reports
what the data doesn't show, not just what it does.

DuckDB notes:
  - CROSS JOIN works identically to SQL Server — broadcasts a single-row
    totals CTE across every row in the main result set.
  - No electric_scooter rows in this 12-month dataset (Apr 2025–Mar 2026).
    ETL was designed to handle other types in future loads; none appeared here.
  - DuckDB experiment (later script): download older Divvy CSVs and query
    them directly to check whether electric_scooter appears in other years.
    This is a showcase of DuckDB's ad-hoc CSV querying strength.

Validates against SQL Server query 11_bike_type_mix.sql
  Expected: ~65% electric for both member and casual groups
"""

import duckdb
from pathlib import Path

CSV_PATH = str(Path(__file__).parent.parent / "Data" / "DATAfile_Consolidated" / "*.csv")

con = duckdb.connect()

rows = con.execute(f"""
    WITH BikeAgg AS (
        SELECT
            rideable_type,
            COUNT(*)                                            AS total_rides,
            COUNT(*) FILTER (WHERE member_casual = 'member')   AS member_rides,
            COUNT(*) FILTER (WHERE member_casual = 'casual')   AS casual_rides
        FROM read_csv_auto('{CSV_PATH}')
        GROUP BY rideable_type
    ),
    GrandTotals AS (
        SELECT
            SUM(total_rides)    AS grand_total,
            SUM(member_rides)   AS total_member,
            SUM(casual_rides)   AS total_casual
        FROM BikeAgg
    )
    SELECT
        b.rideable_type,
        b.total_rides,
        b.member_rides,
        b.casual_rides,
        ROUND(100.0 * b.total_rides  / g.grand_total,  1) AS pct_of_all_rides,
        ROUND(100.0 * b.member_rides / g.total_member, 1) AS member_pct_of_type,
        ROUND(100.0 * b.casual_rides / g.total_casual, 1) AS casual_pct_of_type
    FROM BikeAgg b
    CROSS JOIN GrandTotals g
    ORDER BY b.total_rides DESC
""").fetchall()

print("=" * 65)
print("  Bike Type Mix")
print("=" * 65)
print(f"  {'Bike Type':<20} {'Total':>9} {'Member':>9} {'Casual':>9} {'All%':>6} {'Mem%':>6} {'Cas%':>6}")
print(f"  {'-'*63}")
for row in rows:
    bike, total, member, casual, pct_all, pct_mem, pct_cas = row
    print(f"  {bike:<20} {total:>9,} {member:>9,} {casual:>9,} {pct_all:>5.1f}% {pct_mem:>5.1f}% {pct_cas:>5.1f}%")
print("=" * 65)
print("  Null finding: member and casual riders use electric bikes")
print("  at nearly identical rates — bike type does not distinguish")
print("  the two groups and is not a conversion lever.")
print()
print("  Note: No electric_scooter rows in Apr 2025–Mar 2026 data.")
print("  See 11_scooter_check.py for cross-year CSV experiment.")
print("=" * 65)
