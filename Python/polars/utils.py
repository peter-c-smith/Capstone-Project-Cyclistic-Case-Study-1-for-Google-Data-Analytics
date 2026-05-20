"""
utils.py
--------
Shared data loader for all Polars analysis scripts.

Key difference from the pandas loader:
  - pandas uses read_csv() — reads all files eagerly into memory immediately.
  - Polars uses scan_csv() — creates a lazy query plan. No data is read until
    .collect() is called. This allows Polars to push down filters and only
    read columns it needs, which can dramatically reduce I/O.

For scripts that use all columns (most of these), the practical difference is
in parsing speed (Polars' Rust engine vs pandas' Python/C engine) rather than
I/O reduction. The timing difference is what we measure.

The returned DataFrame is a fully materialized Polars DataFrame (after .collect()),
identical in content to the pandas equivalent — same rows, same columns, same values.
"""

import polars as pl
from pathlib import Path

# Path to CSV folder — two levels up from this file, then into Data/
_DATA_DIR = (
    Path(__file__).parent.parent.parent
    / "Data"
    / "DATAfile_Consolidated"
)

# Explicit schema — tells Polars the dtype for string columns upfront,
# avoiding the cost of schema inference on every file.
_SCHEMA_OVERRIDES = {
    "ride_id":            pl.String,
    "rideable_type":      pl.String,
    "start_station_name": pl.String,
    "start_station_id":   pl.String,
    "end_station_name":   pl.String,
    "end_station_id":     pl.String,
    "member_casual":      pl.String,
}


def load_trips() -> pl.DataFrame:
    """
    Scan all 12 monthly CSV files and return a single collected DataFrame.

    Uses scan_csv() + collect() — Polars builds a lazy query plan across all
    files, then executes it in one optimized pass using its Rust engine.

    Returns a pl.DataFrame with columns:
        ride_id, rideable_type, started_at, ended_at,
        start_station_name, start_station_id,
        end_station_name, end_station_id,
        start_lat, start_lng, end_lat, end_lng,
        member_casual
    """
    csv_files = sorted(_DATA_DIR.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {_DATA_DIR}")

    trips = (
        pl.scan_csv(
            csv_files,
            schema_overrides=_SCHEMA_OVERRIDES,
            try_parse_dates=True,   # parse started_at / ended_at as Datetime
        )
        .collect()
    )
    return trips
