"""
utils.py
--------
Shared loader for the pandas module. All analysis scripts import load_trips()
from here rather than duplicating the read logic in every file.

Using a utility module is standard practice in real pandas workflows — it keeps
scripts focused on analysis and avoids repeating the boilerplate of reading,
concatenating, and type-casting 12 CSV files.
"""

import pandas as pd
from pathlib import Path

# Resolve the CSV folder relative to this file's location
_SCRIPT_DIR = Path(__file__).parent
_CSV_DIR = _SCRIPT_DIR.parent.parent / "Data" / "DATAfile_Consolidated"

# Explicit dtypes for the string columns — tells pandas not to waste time
# inferring types it already knows. Speeds up read_csv on large files.
_DTYPE_MAP = {
    "ride_id":              "string",
    "rideable_type":        "string",
    "start_station_name":   "string",
    "start_station_id":     "string",
    "end_station_name":     "string",
    "end_station_id":       "string",
    "member_casual":        "string",
}


def load_trips() -> pd.DataFrame:
    """
    Read all 12 monthly Divvy CSV files and return a single concatenated
    DataFrame with typed columns.

    Columns:
        ride_id, rideable_type, started_at, ended_at,
        start/end station name and ID, start/end lat/lng, member_casual

    Row count expected: 5,620,544 (matches SQL Server production table).
    Note: pandas loads all rows into memory (~1.5 GB RAM). This is the key
    difference from DuckDB, which queries the files without loading them.
    """
    csv_files = sorted(_CSV_DIR.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {_CSV_DIR}")

    trips = pd.concat(
        [pd.read_csv(f, dtype=_DTYPE_MAP) for f in csv_files],
        ignore_index=True
    )

    # Parse timestamps once here rather than in every script
    trips["started_at"] = pd.to_datetime(trips["started_at"])
    trips["ended_at"]   = pd.to_datetime(trips["ended_at"])

    return trips
