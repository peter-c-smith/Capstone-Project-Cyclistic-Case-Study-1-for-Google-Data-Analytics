"""
03_avg_duration_distance.py
---------------------------
Do casual riders take longer or farther rides than members on average?

Key finding: Casual riders take ~82% longer rides but cover only ~3% more
distance — they ride slowly and leisurely, not to get somewhere fast.

DuckDB notes:
  - No pre-calculated columns here — duration and distance are computed
    inline from raw CSV timestamps and coordinates, unlike SQL Server where
    ride_time_min and ride_distance_mi were pre-built during ETL.
  - epoch(ended_at - started_at) returns elapsed seconds; divide by 60 for minutes.
  - Haversine formula computes straight-line distance in miles from lat/lng.
  - FILTER (WHERE ...) used again for cleaner conditional averages vs CASE WHEN.
  - ROUND() works without CAST — DuckDB returns a clean numeric directly.

Validates against SQL Server query 06_avg_duration_distance.sql
  Expected: ~16.06 min overall | casual ~1.82x longer | casual ~1.03x farther
"""

import duckdb
from pathlib import Path

CSV_PATH = str(Path(__file__).parent.parent / "Data" / "DATAfile_Consolidated" / "*.csv")

con = duckdb.connect()

result = con.execute(f"""
    WITH RideMetrics AS (
        SELECT
            member_casual,

            -- Duration: epoch() extracts total seconds from a timestamp interval
            CASE WHEN epoch(ended_at - started_at) / 60.0 > 0
                 THEN epoch(ended_at - started_at) / 60.0 END AS duration_min,

            -- Distance: haversine formula from start/end coordinates → miles
            -- Gives straight-line distance; zero when start = end (round trips)
            CASE WHEN 3958.8 * 2 * ASIN(SQRT(
                    POWER(SIN(RADIANS(end_lat   - start_lat) / 2), 2) +
                    COS(RADIANS(start_lat)) * COS(RADIANS(end_lat)) *
                    POWER(SIN(RADIANS(end_lng   - start_lng) / 2), 2)
                 )) > 0
                 THEN 3958.8 * 2 * ASIN(SQRT(
                    POWER(SIN(RADIANS(end_lat   - start_lat) / 2), 2) +
                    COS(RADIANS(start_lat)) * COS(RADIANS(end_lat)) *
                    POWER(SIN(RADIANS(end_lng   - start_lng) / 2), 2)
                 )) END AS distance_mi

        FROM read_csv_auto('{CSV_PATH}')
    )
    SELECT
        -- Overall averages
        ROUND(AVG(duration_min), 2)  AS avg_duration_all_min,
        ROUND(AVG(distance_mi),  2)  AS avg_distance_all_mi,

        -- Member averages (FILTER replaces CASE WHEN ... END inside AVG)
        ROUND(AVG(duration_min) FILTER (WHERE member_casual = 'member'), 2) AS avg_duration_member_min,
        ROUND(AVG(distance_mi)  FILTER (WHERE member_casual = 'member'), 2) AS avg_distance_member_mi,

        -- Casual averages
        ROUND(AVG(duration_min) FILTER (WHERE member_casual = 'casual'), 2) AS avg_duration_casual_min,
        ROUND(AVG(distance_mi)  FILTER (WHERE member_casual = 'casual'), 2) AS avg_distance_casual_mi,

        -- Ratios
        ROUND(
            AVG(duration_min) FILTER (WHERE member_casual = 'casual') /
            AVG(duration_min) FILTER (WHERE member_casual = 'member'), 2
        ) AS duration_ratio_casual_to_member,

        ROUND(
            AVG(distance_mi) FILTER (WHERE member_casual = 'casual') /
            AVG(distance_mi) FILTER (WHERE member_casual = 'member'), 2
        ) AS distance_ratio_casual_to_member

    FROM RideMetrics
""").fetchone()

(avg_dur_all, avg_dist_all,
 avg_dur_mem, avg_dist_mem,
 avg_dur_cas, avg_dist_cas,
 dur_ratio, dist_ratio) = result

print("=" * 55)
print("  Avg Ride Duration & Distance")
print("=" * 55)
print(f"  {'':25s} {'Member':>8}  {'Casual':>8}  {'All':>8}")
print(f"  {'-'*53}")
print(f"  {'Avg duration (min)':25s} {avg_dur_mem:>8.2f}  {avg_dur_cas:>8.2f}  {avg_dur_all:>8.2f}")
print(f"  {'Avg distance (mi)':25s} {avg_dist_mem:>8.2f}  {avg_dist_cas:>8.2f}  {avg_dist_all:>8.2f}")
print(f"  {'-'*53}")
print(f"  Duration ratio (casual/member): {dur_ratio:.2f}x")
print(f"  Distance ratio (casual/member): {dist_ratio:.2f}x")
print("=" * 55)
print("  Casual riders take longer rides but barely go farther —")
print("  they ride slowly for leisure, not to commute.")
print("=" * 55)
