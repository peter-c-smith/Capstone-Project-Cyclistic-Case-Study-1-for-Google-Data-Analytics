"""
05_round_trips.py
-----------------
Do casual riders return to their starting station more often than members,
indicating recreational use?

Key finding: Casual riders take round trips at 1.63x the rate of members —
further evidence of leisure riding patterns.

DuckDB notes:
  - DuckDB uses COALESCE() instead of SQL Server's ISNULL().
    Both replace NULL with a fallback value — identical behavior here.
  - NULL semantics matter for this query. In standard SQL (and DuckDB),
    NULL = NULL evaluates to NULL (unknown), not TRUE. So a naive comparison
    of start_station_name = end_station_name would EXCLUDE rides where both
    stations are missing (e.g., e-bikes docked at arbitrary racks).
  - Power BI DAX treats BLANK() = BLANK() as TRUE, so those rides DO count
    as round trips in the report. To match that behavior we use:
      COALESCE(start_station_name, '') = COALESCE(end_station_name, '')
    This converts NULL to empty string first, making NULL = NULL → TRUE.
  - This definition was validated against Power BI in SQL Server module
    (08b_round_trips_diag.sql). DuckDB must use the same COALESCE approach
    to produce matching results.

Validates against SQL Server query 08_round_trips.sql
  Expected: ~11.1% member | ~18.1% casual | ratio 1.63
"""

import duckdb
from pathlib import Path

CSV_PATH = str(Path(__file__).parent.parent / "Data" / "DATAfile_Consolidated" / "*.csv")

con = duckdb.connect()

result = con.execute(f"""
    WITH RoundTripFlags AS (
        SELECT
            member_casual,
            -- COALESCE replaces NULL with '' so that missing-station rides
            -- where both names are NULL correctly evaluate as equal (round trips).
            -- Matches Power BI DAX BLANK() = BLANK() → TRUE behavior.
            COALESCE(start_station_name, '') = COALESCE(end_station_name, '') AS is_round_trip
        FROM read_csv_auto('{CSV_PATH}')
    )
    SELECT
        COUNT(*) FILTER (WHERE is_round_trip)           AS round_trips,

        -- Member
        COUNT(*) FILTER (WHERE member_casual = 'member' AND is_round_trip)
                                                        AS member_round_trips,
        ROUND(100.0 *
            COUNT(*) FILTER (WHERE member_casual = 'member' AND is_round_trip) /
            COUNT(*) FILTER (WHERE member_casual = 'member')
        , 1)                                            AS member_round_trip_pct,

        -- Casual
        COUNT(*) FILTER (WHERE member_casual = 'casual' AND is_round_trip)
                                                        AS casual_round_trips,
        ROUND(100.0 *
            COUNT(*) FILTER (WHERE member_casual = 'casual' AND is_round_trip) /
            COUNT(*) FILTER (WHERE member_casual = 'casual')
        , 1)                                            AS casual_round_trip_pct,

        -- Ratio
        ROUND(
            (100.0 * COUNT(*) FILTER (WHERE member_casual = 'casual' AND is_round_trip) /
                     COUNT(*) FILTER (WHERE member_casual = 'casual'))
            /
            (100.0 * COUNT(*) FILTER (WHERE member_casual = 'member' AND is_round_trip) /
                     COUNT(*) FILTER (WHERE member_casual = 'member'))
        , 2)                                            AS round_trip_ratio

    FROM RoundTripFlags
""").fetchone()

(round_trips, member_rt, member_rt_pct,
 casual_rt, casual_rt_pct, ratio) = result

print("=" * 50)
print("  Round Trip Analysis")
print("=" * 50)
print(f"  Total round trips:  {round_trips:,}")
print(f"")
print(f"  {'':30s} {'Round Trip %':>12}")
print(f"  {'-'*44}")
print(f"  {'Members':30s} {member_rt_pct:>11.1f}%  ({member_rt:,})")
print(f"  {'Casual riders':30s} {casual_rt_pct:>11.1f}%  ({casual_rt:,})")
print(f"  {'-'*44}")
print(f"  Round trip ratio (casual/member): {ratio:.2f}x")
print("=" * 50)
print("  Note: NULL station names treated as equal (COALESCE),")
print("  matching Power BI DAX BLANK() = BLANK() behavior.")
print("  e-bike rides ending at non-station racks count as")
print("  round trips when start and end locations both missing.")
print("=" * 50)
