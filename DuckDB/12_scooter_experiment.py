"""
12_scooter_experiment.py
------------------------
Does electric_scooter ever appear as a bike type in Divvy data?

Our 12-month dataset (Apr 2025–Mar 2026) contains only classic_bike and
electric_bike. The ETL was intentionally designed to handle other types
in future loads — but do they actually exist in other years?

This script downloads a sample of older Divvy CSV files directly from the
public S3 bucket and queries them with DuckDB — no database, no SQL Server,
no permanent import. This is the core DuckDB use case: ad-hoc exploration
of external data you've never loaded before.

Months sampled: One month per quarter from 2022 and 2023.
If electric_scooter appears anywhere, we'll find it in this sample.

DuckDB notes:
  - read_csv_auto() works on a list of file paths, not just a glob
  - This script shows DuckDB being used for genuine discovery work,
    not just replicating SQL Server queries
  - The temp files are downloaded, queried, and deleted — DuckDB never
    needs them loaded into a database

Data source: https://divvy-tripdata.s3.amazonaws.com/
License: Divvy trip data is made available under the Open Government License.
"""

import duckdb
import urllib.request
import zipfile
import tempfile
import os
from pathlib import Path

# ── Months to sample ──────────────────────────────────────────────────────────
# One month per quarter, 2022 and 2023 — broad enough to catch scooters
# if they appeared in any season
SAMPLE_MONTHS = [
    "202201", "202204", "202207", "202210",  # 2022: Jan, Apr, Jul, Oct
    "202301", "202304", "202307", "202310",  # 2023: Jan, Apr, Jul, Oct
]

BASE_URL = "https://divvy-tripdata.s3.amazonaws.com"

def download_and_extract(month_str, dest_folder):
    """Download a Divvy ZIP for the given YYYYMM and extract the CSV."""
    zip_name = f"{month_str}-divvy-tripdata.zip"
    url = f"{BASE_URL}/{zip_name}"
    zip_path = os.path.join(dest_folder, zip_name)

    print(f"  Downloading {zip_name}...", end=" ", flush=True)
    try:
        urllib.request.urlretrieve(url, zip_path)
        with zipfile.ZipFile(zip_path, 'r') as z:
            # Exclude macOS resource fork files (__MACOSX/._filename)
            # that get bundled into ZIPs created on Macs
            csv_files = [
                f for f in z.namelist()
                if f.endswith('.csv')
                and not f.startswith('__MACOSX')
                and not os.path.basename(f).startswith('._')
            ]
            z.extractall(dest_folder, members=csv_files)
        os.remove(zip_path)  # delete ZIP, keep CSV
        print("done")
        return [os.path.join(dest_folder, f) for f in csv_files]
    except Exception as e:
        print(f"failed ({e})")
        return []

# ── Main ──────────────────────────────────────────────────────────────────────
con = duckdb.connect()
all_csv_paths = []

# Use a temp directory — files are deleted when we're done
with tempfile.TemporaryDirectory() as tmp:
    print("=" * 60)
    print("  Scooter Experiment — Downloading sample Divvy files")
    print("=" * 60)

    for month in SAMPLE_MONTHS:
        paths = download_and_extract(month, tmp)
        all_csv_paths.extend(paths)

    if not all_csv_paths:
        print("  No files downloaded successfully. Check internet connection.")
    else:
        print(f"\n  {len(all_csv_paths)} CSV files downloaded. Querying with DuckDB...")

        # ── Bike types by year ────────────────────────────────────────────────
        # Pass list of paths directly to read_csv_auto
        path_list = ", ".join(f"'{p}'" for p in all_csv_paths)

        bike_types = con.execute(f"""
            SELECT
                YEAR(started_at)        AS ride_year,
                rideable_type,
                COUNT(*)                AS rides,
                ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY YEAR(started_at)), 1)
                                        AS pct_of_year
            FROM read_csv_auto([{path_list}])
            GROUP BY ride_year, rideable_type
            ORDER BY ride_year, rides DESC
        """).fetchall()

        print()
        print("=" * 55)
        print("  Bike Types Found in Sample (2022–2023)")
        print("=" * 55)
        print(f"  {'Year':>6} {'Bike Type':<20} {'Rides':>10} {'% of Year':>10}")
        print(f"  {'-'*53}")

        current_year = None
        for row in bike_types:
            year, bike, rides, pct = row
            if year != current_year:
                if current_year is not None:
                    print()
                current_year = year
            print(f"  {year:>6} {bike:<20} {rides:>10,} {pct:>9.1f}%")

        # ── Did scooter appear? ───────────────────────────────────────────────
        scooter_found = any(row[1] == 'electric_scooter' for row in bike_types)
        all_types = sorted(set(row[1] for row in bike_types))

        print()
        print("=" * 55)
        print("  Summary")
        print("=" * 55)
        print(f"  Unique bike types found: {', '.join(all_types)}")
        if scooter_found:
            print("  electric_scooter: YES — appears in this sample.")
            print("  The ETL's allowance for other types was warranted.")
        else:
            print("  electric_scooter: NOT FOUND in this sample.")
            print("  Scooters may exist outside this date range, or")
            print("  may have been retired / not yet deployed in 2022–23.")
        print("=" * 55)
        print("  All temp files deleted. Nothing was loaded into a database.")
        print("=" * 55)
