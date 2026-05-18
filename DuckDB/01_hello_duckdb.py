"""
01_hello_duckdb.py
------------------
Sanity check script — confirms DuckDB can read all 12 monthly CSVs at once
using a glob pattern. No database, no loading, no staging tables. Just files.

This is the core DuckDB value proposition: query raw CSVs directly with SQL.
"""

import duckdb
from pathlib import Path

# Build the CSV path relative to this script's location, so it works
# regardless of which directory the terminal is in when you run the script.
SCRIPT_DIR = Path(__file__).parent
CSV_PATH = str(SCRIPT_DIR.parent / "Data" / "DATAfile_Consolidated" / "*.csv")

# Connect to an in-memory DuckDB instance (nothing is saved to disk)
con = duckdb.connect()

# Query all 12 CSVs as if they were a single table
result = con.execute(f"""
    SELECT
        COUNT(*)                                            AS total_rides,
        COUNT(CASE WHEN member_casual = 'member'  THEN 1 END) AS member_rides,
        COUNT(CASE WHEN member_casual = 'casual'  THEN 1 END) AS casual_rides,
        COUNT(DISTINCT rideable_type)                       AS bike_types,
        MIN(started_at)                                     AS earliest_ride,
        MAX(started_at)                                     AS latest_ride
    FROM read_csv_auto('{CSV_PATH}')
""").fetchone()

total, members, casuals, bike_types, earliest, latest = result

print("=" * 50)
print("  DuckDB — Hello, Cyclistic!")
print("=" * 50)
print(f"  Total rides:    {total:,}")
print(f"  Member rides:   {members:,}")
print(f"  Casual rides:   {casuals:,}")
print(f"  Bike types:     {bike_types}")
print(f"  Date range:     {earliest}  →  {latest}")
print("=" * 50)
print("  All 12 CSVs read directly. No database required.")
print("=" * 50)
