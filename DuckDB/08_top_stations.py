"""
08_top_stations.py
------------------
Which stations are most popular, and do casual and member riders
concentrate at different locations?

Key findings:
  - Zero overlap between member and casual top 10 station lists
  - Member top stations: transit hubs near Union Station, Canal St, Kinzie St
  - Casual top stations: lakefront/tourist destinations — Navy Pier,
    Millennium Park, Shedd Aquarium
  - Shedd Aquarium is the starkest example: 81.8% casual (the most
    casual-skewed station in the top 10 by a wide margin)

DuckDB notes:
  - LIMIT replaces SQL Server's TOP n — same result, standard SQL syntax
    LIMIT 10  vs  SELECT TOP 10
  - WHERE filters for non-null, non-empty station names — same logic as
    SQL Server's IS NOT NULL AND <> '' pattern
  - Two queries share one StationCounts CTE definition — written twice
    here (once per query) since DuckDB doesn't support cross-query CTEs.
    Could be refactored into a VIEW or temp table — shown as-is to match
    the SQL Server query structure.

Validates against SQL Server queries 12_top_stations.sql and
12b_top_stations_member.sql
"""

import duckdb
from pathlib import Path

CSV_PATH = str(Path(__file__).parent.parent / "Data" / "DATAfile_Consolidated" / "*.csv")

con = duckdb.connect()

# ── Part 1: Top 10 stations by member starts ─────────────────────────────────
member_top = con.execute(f"""
    WITH StationCounts AS (
        SELECT
            start_station_name,
            COUNT(*) FILTER (WHERE member_casual = 'member') AS member_starts,
            COUNT(*) FILTER (WHERE member_casual = 'casual') AS casual_starts,
            COUNT(*)                                          AS total_starts
        FROM read_csv_auto('{CSV_PATH}')
        WHERE start_station_name IS NOT NULL
          AND start_station_name <> ''
        GROUP BY start_station_name
    )
    SELECT
        start_station_name,
        member_starts,
        casual_starts,
        total_starts,
        ROUND(100.0 * member_starts / total_starts, 1) AS member_pct
    FROM StationCounts
    ORDER BY member_starts DESC
    LIMIT 10
""").fetchall()

# ── Part 2: Top 10 stations by casual starts ─────────────────────────────────
casual_top = con.execute(f"""
    WITH StationCounts AS (
        SELECT
            start_station_name,
            COUNT(*) FILTER (WHERE member_casual = 'member') AS member_starts,
            COUNT(*) FILTER (WHERE member_casual = 'casual') AS casual_starts,
            COUNT(*)                                          AS total_starts
        FROM read_csv_auto('{CSV_PATH}')
        WHERE start_station_name IS NOT NULL
          AND start_station_name <> ''
        GROUP BY start_station_name
    )
    SELECT
        start_station_name,
        casual_starts,
        member_starts,
        total_starts,
        ROUND(100.0 * casual_starts / total_starts, 1) AS casual_pct
    FROM StationCounts
    ORDER BY casual_starts DESC
    LIMIT 10
""").fetchall()

# ── Output ────────────────────────────────────────────────────────────────────
print("=" * 68)
print("  Top 10 Stations by Member Starts")
print("=" * 68)
print(f"  {'Station':<38} {'Member':>7} {'Casual':>7} {'Total':>7} {'Mem%':>6}")
print(f"  {'-'*66}")
for row in member_top:
    station, member, casual, total, pct = row
    print(f"  {station:<38} {member:>7,} {casual:>7,} {total:>7,} {pct:>5.1f}%")

print()
print("=" * 68)
print("  Top 10 Stations by Casual Starts")
print("=" * 68)
print(f"  {'Station':<38} {'Casual':>7} {'Member':>7} {'Total':>7} {'Cas%':>6}")
print(f"  {'-'*66}")
for row in casual_top:
    station, casual, member, total, pct = row
    print(f"  {station:<38} {casual:>7,} {member:>7,} {total:>7,} {pct:>5.1f}%")

print("=" * 68)
print("  Zero overlap between the two top 10 lists.")
print("  Members: transit hubs (commuting)")
print("  Casuals: lakefront/tourist destinations (leisure)")
print("=" * 68)
