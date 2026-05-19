"""
10_missing_station_data.py
--------------------------
How prevalent is missing station data, and what does it reveal about
how electric bikes track location differently from classic bikes?

Key inference (derived entirely from the data, not assumed from outside
knowledge): Classic bikes have 0% missing station data. Electric bikes
have ~32% missing — but those rides still have start_lat/start_lng and
end_lat/end_lng populated. The only way GPS coordinates can exist without
a station name is if the bike itself is reporting its location. This means
e-bikes almost certainly have onboard GPS and wireless communication
hardware. Classic bikes are "located" only when physically docked; the
station sensor reports occupancy. E-bikes know where they are
independently of any dock.

Portfolio significance: This is a real analytical inference drawn from the
structure of the data, not background knowledge. It demonstrates reasoning
about *how* data was collected, not just what it says. It also confirms
that e-bike rides with missing station names are NOT true data gaps — the
GPS coordinates are fully present and usable for geographic analysis.

DuckDB notes:
  - No new syntax here — this script intentionally uses patterns already
    introduced (FILTER, COALESCE, ROUND) to reinforce them.
  - The GPS presence check uses a compound FILTER condition to count rides
    that are missing station names BUT have coordinates — this is the key
    evidence for the onboard GPS inference.

Validates against SQL Server query 13_missing_station_data.sql
  Expected: classic_bike ~0% missing | electric_bike ~32% missing
"""

import duckdb
from pathlib import Path

CSV_PATH = str(Path(__file__).parent.parent / "Data" / "DATAfile_Consolidated" / "*.csv")

con = duckdb.connect()

# ── Part 1: Overall missing station summary ───────────────────────────────────
overall = con.execute(f"""
    SELECT
        COUNT(*) FILTER (WHERE start_station_name IS NULL OR start_station_name = '')
                                                        AS missing_start,
        ROUND(100.0 *
            COUNT(*) FILTER (WHERE start_station_name IS NULL OR start_station_name = '') /
            COUNT(*), 1)                                AS missing_start_pct,

        COUNT(*) FILTER (WHERE end_station_name IS NULL OR end_station_name = '')
                                                        AS missing_end,
        ROUND(100.0 *
            COUNT(*) FILTER (WHERE end_station_name IS NULL OR end_station_name = '') /
            COUNT(*), 1)                                AS missing_end_pct,

        COUNT(*) FILTER (WHERE (start_station_name IS NULL OR start_station_name = '')
                            AND (end_station_name   IS NULL OR end_station_name   = ''))
                                                        AS missing_both,
        ROUND(100.0 *
            COUNT(*) FILTER (WHERE (start_station_name IS NULL OR start_station_name = '')
                                AND (end_station_name   IS NULL OR end_station_name   = '')) /
            COUNT(*), 1)                                AS missing_both_pct

    FROM read_csv_auto('{CSV_PATH}')
""").fetchone()

missing_start, missing_start_pct, missing_end, missing_end_pct, missing_both, missing_both_pct = overall

# ── Part 2: Missing by rider type and bike type ───────────────────────────────
by_type = con.execute(f"""
    SELECT
        member_casual,
        rideable_type,
        COUNT(*)                                        AS total_rides,
        COUNT(*) FILTER (WHERE start_station_name IS NULL OR start_station_name = '')
                                                        AS missing_start,
        ROUND(100.0 *
            COUNT(*) FILTER (WHERE start_station_name IS NULL OR start_station_name = '') /
            COUNT(*), 1)                                AS missing_start_pct
    FROM read_csv_auto('{CSV_PATH}')
    GROUP BY member_casual, rideable_type
    ORDER BY member_casual, rideable_type
""").fetchall()

# ── Part 3: The GPS inference — missing station BUT coords present ────────────
gps_check = con.execute(f"""
    SELECT
        rideable_type,
        COUNT(*) FILTER (WHERE (start_station_name IS NULL OR start_station_name = '')
                            AND start_lat IS NOT NULL AND start_lng IS NOT NULL)
                                                        AS missing_station_but_has_gps,
        COUNT(*) FILTER (WHERE start_station_name IS NULL OR start_station_name = '')
                                                        AS total_missing_station,
        ROUND(100.0 *
            COUNT(*) FILTER (WHERE (start_station_name IS NULL OR start_station_name = '')
                                AND start_lat IS NOT NULL AND start_lng IS NOT NULL) /
            NULLIF(COUNT(*) FILTER (WHERE start_station_name IS NULL
                                      OR start_station_name = ''), 0)
        , 1)                                            AS pct_missing_station_with_gps
    FROM read_csv_auto('{CSV_PATH}')
    GROUP BY rideable_type
    ORDER BY rideable_type
""").fetchall()

# ── Output ────────────────────────────────────────────────────────────────────
print("=" * 55)
print("  Part 1: Overall Missing Station Data")
print("=" * 55)
print(f"  Missing start station: {missing_start:>9,}  ({missing_start_pct}%)")
print(f"  Missing end station:   {missing_end:>9,}  ({missing_end_pct}%)")
print(f"  Missing both:          {missing_both:>9,}  ({missing_both_pct}%)")

print()
print("=" * 55)
print("  Part 2: Missing Start Station by Rider & Bike Type")
print("=" * 55)
print(f"  {'Rider':<10} {'Bike Type':<16} {'Total':>9} {'Missing':>9} {'Miss%':>7}")
print(f"  {'-'*53}")
for row in by_type:
    rider, bike, total, missing, pct = row
    print(f"  {rider:<10} {bike:<16} {total:>9,} {missing:>9,} {pct:>6.1f}%")

print()
print("=" * 55)
print("  Part 3: Missing Station — But GPS Coordinates Present?")
print("=" * 55)
print(f"  {'Bike Type':<16} {'Missing Stn':>12} {'Has GPS':>10} {'GPS%':>7}")
print(f"  {'-'*48}")
for row in gps_check:
    bike, has_gps, total_missing, gps_pct = row
    pct_str = f"{gps_pct:>6.1f}%" if gps_pct is not None else "   N/A"
    print(f"  {bike:<16} {total_missing:>12,} {has_gps:>10,} {pct_str}")

print()
print("=" * 55)
print("  Inference: E-bikes missing station names still have GPS")
print("  coordinates — the bike itself is reporting its location.")
print("  E-bikes have onboard GPS hardware. Classic bikes are")
print("  located only when docked at a station sensor.")
print("  Missing e-bike station data is NOT a data quality gap —")
print("  coordinates are present and fully usable for geo analysis.")
print("=" * 55)
