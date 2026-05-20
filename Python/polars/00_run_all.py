"""
00_run_all.py
-------------
Runs all Polars analysis scripts in sequence and reports pass/fail
for each based on whether key expected values are present in the output.

Also records total elapsed time per script for comparison against the
pandas module (00_run_all.py in Python/pandas/).

Usage:
    python 00_run_all.py
"""

import os
import subprocess
import sys
import time
from pathlib import Path

PYTHON     = sys.executable
SCRIPT_DIR = Path(__file__).parent

SCRIPTS = [
    "01_hello_polars.py",
    "02_core_ride_counts.py",
    "03_avg_duration_distance.py",
    "04_weekend_weekday.py",
    "05_round_trips.py",
    "06_seasonal_breakdown.py",
    "07_bike_type_mix.py",
    "08_top_stations.py",
    "09_hourly_distribution.py",
    "10_missing_station_data.py",
    "11_revenue_proxy.py",
    "12_peak_concurrent_rides.py",
    "13_commuter_casual_segmentation.py",
]

EXPECTED = {
    "01_hello_polars.py":                   ["5,620,544", "✓"],
    "02_core_ride_counts.py":               ["64.1%", "35.9%", "Matches SQL Server"],
    "03_avg_duration_distance.py":          ["1.82x", "1.03x"],
    "04_weekend_weekday.py":                ["1.61x"],
    "05_round_trips.py":                    ["1.63x", "fill_null"],
    "06_seasonal_breakdown.py":             ["42.7%", "19.6%"],
    "07_bike_type_mix.py":                  ["Null finding"],
    "08_top_stations.py":                   ["Kingsbury St & Kinzie St",
                                             "DuSable Lake Shore Dr & Monroe St",
                                             "Overlap between top 10 lists: 0"],
    "09_hourly_distribution.py":            ["08:00", "17:00", "commute pattern"],
    "10_missing_station_data.py":           ["100.0%", "onboard GPS hardware"],
    "11_revenue_proxy.py":                  ["2,015,499", "119.88"],
    "12_peak_concurrent_rides.py":          ["Peak simultaneous rides", "fleet size"],
    "13_commuter_casual_segmentation.py":   ["Commuter-pattern casuals",
                                             "Targeted vs Broad"],
}

print("=" * 62)
print("  Cyclistic — Polars Module: Run All Scripts")
print("=" * 62)

results       = []
t_total_start = time.perf_counter()

for script in SCRIPTS:
    path = SCRIPT_DIR / script
    print(f"\n  Running {script}...")
    t0 = time.perf_counter()

    child_env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    result = subprocess.run(
        [PYTHON, str(path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=child_env
    )

    elapsed = time.perf_counter() - t0
    output  = result.stdout + result.stderr

    checks = EXPECTED.get(script, [])
    passed = all(s in output for s in checks)
    status = "✓ PASS" if passed and result.returncode == 0 else "✗ FAIL"

    print(f"  {status}  ({elapsed:.1f}s)")
    if result.returncode != 0 or not passed:
        print(f"  --- stdout ---")
        print(result.stdout[-500:] if result.stdout else "  (no output)")
        if result.stderr:
            print(f"  --- stderr ---")
            print(result.stderr[-300:])

    results.append((script, status, elapsed))

t_total = time.perf_counter() - t_total_start

print()
print("=" * 62)
print("  Summary")
print("=" * 62)
for script, status, elapsed in results:
    print(f"  {status}  {script:<40} {elapsed:>6.1f}s")
print(f"  {'-'*60}")
passed_count = sum(1 for _, s, _ in results if "PASS" in s)
print(f"  {passed_count}/{len(results)} scripts passed   "
      f"Total time: {t_total:.1f}s")
print()
print("  pandas total time (reference): ~333s")
print(f"  Polars total time:              {t_total:.0f}s")
print(f"  Speedup: ~{333/t_total:.2f}x" if t_total > 0 else "")
print("=" * 62)
