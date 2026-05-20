"""
00_run_all.py
-------------
Runs all pandas analysis scripts in sequence and reports pass/fail
for each based on whether key expected values are present in the output.

Expected outputs are derived from the SQL Server cross-validation
(cross_validation.md) — the authoritative reference for this dataset.

Usage:
    python 00_run_all.py
"""

import os
import subprocess
import sys
import time
from pathlib import Path

PYTHON   = sys.executable
SCRIPT_DIR = Path(__file__).parent

SCRIPTS = [
    "01_hello_pandas.py",
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
]

# Key strings expected in each script's output — a lightweight sanity check.
# If these strings are present, the script ran and produced the right result.
EXPECTED = {
    "01_hello_pandas.py":           ["5,620,544", "Match:          ✓"],
    "02_core_ride_counts.py":       ["64.1%", "35.9%", "Matches SQL Server"],
    "03_avg_duration_distance.py":  ["1.82x", "1.03x"],
    "04_weekend_weekday.py":        ["1.61x"],
    "05_round_trips.py":            ["1.63x", "BLANK() = BLANK()"],
    "06_seasonal_breakdown.py":     ["42.7%", "19.6%"],
    "07_bike_type_mix.py":          ["Null finding"],
    "08_top_stations.py":           ["Kingsbury St & Kinzie St",
                                     "DuSable Lake Shore Dr & Monroe St",
                                     "Overlap between top 10 lists: 0"],
    "09_hourly_distribution.py":    ["08:00", "17:00", "commute pattern"],
    "10_missing_station_data.py":   ["100.0%", "onboard GPS hardware"],
    "11_revenue_proxy.py":          ["2,015,499", "119.88"],
    "12_peak_concurrent_rides.py":  ["Peak simultaneous rides", "fleet size"],
}

print("=" * 60)
print("  Cyclistic — pandas Module: Run All Scripts")
print("=" * 60)

results = []
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

    # Check expected strings
    checks  = EXPECTED.get(script, [])
    passed  = all(s in output for s in checks)
    status  = "✓ PASS" if passed and result.returncode == 0 else "✗ FAIL"

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
print("=" * 60)
print("  Summary")
print("=" * 60)
for script, status, elapsed in results:
    print(f"  {status}  {script:<35} {elapsed:>6.1f}s")
print(f"  {'-'*58}")
passed_count = sum(1 for _, s, _ in results if "PASS" in s)
print(f"  {passed_count}/{len(results)} scripts passed   "
      f"Total time: {t_total:.1f}s")
print("=" * 60)
