"""
01_hello_pandas.py
------------------
Sanity check script — reads all 12 monthly CSVs into a single pandas DataFrame
and confirms the row count matches SQL Server (5,620,544), DuckDB, and R.

This is the pandas equivalent of DuckDB's read_csv_auto('*.csv') — but where
DuckDB queries files directly without loading them, pandas loads everything into
memory. On 5.6M rows that's manageable (~1.5 GB RAM), but it's worth knowing
the difference.

Introduces: pd.read_csv(), pd.concat(), DataFrame.info(), value_counts()
"""

import pandas as pd
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths — resolved relative to this script's location so the script works
# from any terminal directory.
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).parent
CSV_DIR = SCRIPT_DIR.parent.parent / "Data" / "DATAfile_Consolidated"

csv_files = sorted(CSV_DIR.glob("*.csv"))
print(f"CSV files found: {len(csv_files)}")

# ---------------------------------------------------------------------------
# Load all 12 CSVs into a single DataFrame.
#
# pd.read_csv() reads one file; pd.concat() stacks the list of DataFrames
# into one. ignore_index=True resets the row index so it runs 0 to N-1
# instead of repeating 0..n for each file.
# ---------------------------------------------------------------------------

trips = pd.concat(
    [pd.read_csv(f) for f in csv_files],
    ignore_index=True
)

# ---------------------------------------------------------------------------
# Sanity checks
# ---------------------------------------------------------------------------

print("\n" + "=" * 50)
print("  pandas — Hello, Cyclistic!")
print("=" * 50)
print(f"  Total rows:     {len(trips):,}")
print(f"  Total columns:  {trips.shape[1]}")
print(f"  Expected rows:  5,620,544")
print(f"  Match:          {'✓' if len(trips) == 5_620_544 else '✗ MISMATCH'}")
print("=" * 50)

# Member / casual split
split = trips["member_casual"].value_counts()
total = len(trips)
print("\n--- Member / Casual Split ---")
for label, count in split.items():
    print(f"  {label:<8}  {count:>9,}  ({count/total*100:.1f}%)")

# Date range — parse the started_at column for min/max
trips["started_at"] = pd.to_datetime(trips["started_at"])
print(f"\n--- Date Range ---")
print(f"  Earliest ride:  {trips['started_at'].min()}")
print(f"  Latest ride:    {trips['started_at'].max()}")

# Column types — the pandas equivalent of R's glimpse()
print("\n--- DataFrame Info ---")
trips.info(memory_usage="deep")
