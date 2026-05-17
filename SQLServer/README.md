# SQL Server & SSIS Analysis
## Cyclistic Bike-Share Case Study

This section demonstrates enterprise-level data engineering and SQL analysis using Microsoft SQL Server and SQL Server Integration Services (SSIS).

**Status:** In development — ETL pipeline complete, analytical queries in progress

---

## What's Built

### Database
- **CyclisticCaseStudy** on SQL Server 2022, data files at `D:\SQLDataFiles\`
- Server instance: `PETRISLAP2025\PETRIS2022`

### Schema
Four production tables across two schemas:

| Table | Purpose |
|---|---|
| `stg.Trips` | Staging — raw CSV data, all NVARCHAR, populated by SSIS |
| `stg.Trips_Errors` | Error rows redirected from the staging Data Flow |
| `dbo.Trips` | Production — typed, validated, enriched ride records |
| `dbo.ETL_ErrorLog` | Package-level error log populated by SSIS OnError handler |

Full schema documentation in `schema.md`.

### SSIS Package — LoadTrips
Located in `SSIS/CyclisticETL/LoadTrips.dtsx`. Loads all 12 source CSV files into SQL Server via a staging-to-production pattern.

**Control Flow:**
1. Truncate `stg.Trips`
2. Truncate `dbo.Trips`
3. Foreach Loop — iterates all CSVs in `Data\DATAfile_Consolidated\`
   - Data Flow: Flat File → Derived Column (source_file) → OLE DB Destination (`stg.Trips`)
   - Error rows redirected to `stg.Trips_Errors`
4. Validate staging row count — aborts transform if below 1,000,000 rows
5. Execute SQL — INSERT/SELECT from `stg.Trips` into `dbo.Trips` with type casting, NULL handling, and computed columns

**Computed columns calculated during load:**
- `ride_time_min` — decimal minutes via `DATEDIFF(SECOND)` / 60; NULL for negative durations
- `ride_distance_mi` — Haversine formula in miles; NULL for missing coordinates

**Error handling:**
- OnError event handler logs failures to `dbo.ETL_ErrorLog`
- Data Flow error output redirects bad rows to `stg.Trips_Errors`
- Row count validation prevents transform running on an empty or partial staging load

### Load Results
- **Total rides loaded:** 5,620,544
- **Source files:** 12 monthly CSVs, April 2025 – March 2026
- **Rows excluded from raw source:** 2,736 (missing critical fields)
- **Error rows:** 0

---

## Query Runner

`query_runner.py` connects to SQL Server via `pymssql` and runs `.sql` files from the `queries/` folder, writing results to `query_results/` as timestamped CSVs.

```
pip install pymssql python-dotenv
python query_runner.py                     # runs all queries
python query_runner.py 00_connection_check # runs a specific query
```

Copy `.env.example` to `.env` and set your connection details. `.env` is git-ignored.

---

## Cross-Validation Against Power BI

All T-SQL analytical queries were written to replicate the DAX measures in the Power BI report, then run against SQL Server to verify the figures. This cross-validation process uncovered one noteworthy finding.

### Discovery: DAX BLANK() vs. SQL NULL Semantics (Round Trips)

The initial round trip query — which counted rides where both `start_station_name` and `end_station_name` were non-empty and equal — produced results that didn't match the Power BI report:

| Metric | Power BI | Initial SQL |
|---|---|---|
| Member round trip % | ~11% | 2.0% |
| Casual round trip % | ~18% | 6.0% |
| Ratio (casual / member) | 1.63 | 3.01 |

A diagnostic query (`08b_round_trips_diag.sql`) was written to test three definitions side by side. The finding: **Power BI DAX treats `BLANK() = BLANK()` as TRUE**, meaning rides where *both* station names are missing (common with e-bikes locked at non-station racks) were being counted as round trips. SQL Server's three-valued logic treats `NULL = NULL` as UNKNOWN, not TRUE — so those rows were silently excluded.

Fixing the query to use `ISNULL(start_station_name,'') = ISNULL(end_station_name,'')` — which replicates DAX blank-equality behavior — produced an exact match:

| Metric | Power BI | Corrected SQL |
|---|---|---|
| Member round trip % | ~11% | **11.1%** ✓ |
| Casual round trip % | ~18% | **18.1%** ✓ |
| Ratio (casual / member) | 1.63 | **1.63** ✓ |

This is a meaningful difference in analytical tools, not a data quality issue. It demonstrates the importance of understanding how each tool handles missing values when replicating measures across platforms.

Full validation results for all metrics are documented in [`cross_validation.md`](cross_validation.md).

---

## Why SQL Server & SSIS

SQL Server and SSIS represent the enterprise standard for relational database management and ETL workflows. This section demonstrates the ability to handle large datasets in a production database environment — a skill set that complements the analytical work shown in the Power BI, R, and Python sections.
