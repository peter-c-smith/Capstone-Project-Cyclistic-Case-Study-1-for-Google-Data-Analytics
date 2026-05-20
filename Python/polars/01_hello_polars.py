"""
01_hello_polars.py
------------------
Sanity check: load all 12 CSV files and confirm row/column counts match
the SQL Server cross-validation reference (5,620,544 rows, 13 columns).

Also times the load so we can compare directly against the pandas equivalent
(01_hello_pandas.py). The load time difference is the clearest single-number
summary of the pandas vs Polars performance story.

pandas baseline (AMD Ryzen 5 7520U, Samsung SSD, 16GB RAM, Windows 11):
  ~23-24 seconds to load 5,620,544 rows across 12 CSV files.

Key Polars difference shown here:
  scan_csv() + collect() vs pandas read_csv() — Polars uses a lazy query
  plan executed by its Rust engine. For a full-column load like this, the
  speedup comes from faster CSV parsing, not lazy column pruning.
"""

import time
import polars as pl
from utils import load_trips

EXPECTED_ROWS = 5_620_544
EXPECTED_COLS = 13

print("=" * 55)
print("  Polars — Hello, Cyclistic!")
print("=" * 55)

t0    = time.perf_counter()
trips = load_trips()
elapsed = time.perf_counter() - t0

rows, cols = trips.shape

print(f"  Total rows:     {rows:>10,}")
print(f"  Total columns:  {cols:>10}")
print(f"  Load time:      {elapsed:>9.2f}s")
print()
print(f"  Expected rows:  {EXPECTED_ROWS:>10,}")
print(f"  Match:          {'✓' if rows == EXPECTED_ROWS else '✗ MISMATCH'}")
print()
print(f"  Schema:")
for name, dtype in trips.schema.items():
    print(f"    {name:<25} {dtype}")
print("=" * 55)
