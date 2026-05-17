# ETL Process Documentation
## Cyclistic Bike-Share Case Study — SQL Server & SSIS

---

## Overview

This document describes the ETL pipeline that loads 12 months of Cyclistic (Divvy) bike-share trip data from raw CSV files into a SQL Server production database. The pipeline was built using SQL Server Integration Services (SSIS) and follows a staging-to-production pattern that mirrors enterprise data warehouse practice.

**Source:** 12 monthly CSV files, April 2025 – March 2026  
**Destination:** `CyclisticCaseStudy` database on SQL Server 2022  
**Tool:** SSIS package `LoadTrips.dtsx` (Visual Studio / SSDT)  
**Final row count:** 5,620,544 rides

---

## Architecture: Staging-to-Production Pattern

Rather than loading directly from CSV into the production table, the pipeline uses an intermediate staging table (`stg.Trips`). This is standard enterprise practice for several reasons:

- **Separation of concerns.** The staging table receives raw data exactly as it arrives — all columns typed as NVARCHAR, no constraints, no computed columns. Validation and transformation happen separately in a controlled SQL step.
- **Auditability.** If the production load fails, the staging data is still intact and can be inspected or reloaded without re-reading the source files.
- **Error isolation.** Bad rows can be redirected to an error table at the staging load stage, before they ever touch production.
- **Flexibility.** The transform SQL can be modified and re-run against the staged data without re-reading the CSVs.

---

## Database Schema

Four tables across two schemas support the pipeline:

| Table | Schema | Purpose |
|---|---|---|
| `stg.Trips` | Staging | Raw CSV data — all NVARCHAR, no constraints |
| `stg.Trips_Errors` | Staging | Rows rejected by the Data Flow error output |
| `dbo.Trips` | Production | Typed, validated, enriched ride records |
| `dbo.ETL_ErrorLog` | Production | Package-level errors from the SSIS OnError handler |

The production table adds structure that doesn't exist in the source:
- `trip_id` — surrogate integer primary key (IDENTITY)
- `ride_id` — natural key with a UNIQUE constraint
- `member_casual` — constrained to `('member', 'casual')`
- `ride_time_min` — computed from timestamps (see Transformations)
- `ride_distance_mi` — computed via Haversine formula (see Transformations)
- `source_file` — tracks which CSV file each row came from

---

## Control Flow — Step by Step

The SSIS package executes six steps in sequence. Any failure stops the pipeline and logs to `dbo.ETL_ErrorLog` via an OnError event handler.

### Step 1 — Truncate stg.Trips
Clears the staging table before each load. This ensures the staging table only ever contains data from the current run — no accumulation of rows from previous executions.

### Step 2 — Truncate dbo.Trips
Clears the production table. Because the full dataset is always reloaded from source, a full truncate-and-reload is simpler and safer than an incremental upsert for this use case.

### Step 3 — Foreach Loop (CSV files → stg.Trips)
A Foreach Loop File Enumerator iterates over all `*.csv` files in the source directory. For each file, a Data Flow task executes:

**Data Flow components:**

1. **Flat File Source (CSV_Source)** — reads the CSV using a connection manager configured with:
   - Text qualifier: `"` (double-quote) — required because date fields in the source files are stored with surrounding quotes (e.g., `"2025-04-28 08:14:22"`)
   - All columns typed as `DT_WSTR` (Unicode string) to match the NVARCHAR destination
   - `member_casual` output width set to 50 to match the destination column

2. **Derived Column (Add_SourceFile)** — appends the current filename as a new column using the SSIS package variable `@[User::CurrentFile]`, cast explicitly to `DT_WSTR(255)`. This populates `source_file` in the staging table and makes every row traceable to its origin file.

3. **OLE DB Destination (stg_Trips_Dest)** — inserts all columns into `stg.Trips`. The error output is redirected to a second OLE DB destination writing to `stg.Trips_Errors`, so malformed rows are captured rather than aborting the load.

### Step 4 — Row Count Validation
An Execute SQL task queries `COUNT(*) FROM stg.Trips` and compares it against a minimum threshold (1,000,000 rows). If staging is empty or suspiciously small — indicating a failed or partial file load — the package raises an error and aborts before touching production. This guards against accidentally truncating and not refilling the production table.

### Step 5 — Transform and Load (stg.Trips → dbo.Trips)
A single Execute SQL task runs the INSERT/SELECT that moves data from staging to production. This step performs all type casting, validation filtering, and computed column calculation (see Transformations below). Only rows that pass all validation conditions are inserted into `dbo.Trips`.

### Step 6 — OnError Event Handler
An OnError event handler at the package level fires if any task fails. It inserts a row into `dbo.ETL_ErrorLog` capturing the package name, task name, error code, error message, and timestamp. This provides a persistent audit trail without requiring manual inspection of SSIS logs.

---

## Transformations

All transformations occur in the Step 5 INSERT/SELECT statement. The staging table columns are all NVARCHAR; the production table expects typed, validated data.

### Type Casting
All datetime columns use `TRY_CAST` rather than `CAST`. If a date string cannot be parsed, `TRY_CAST` returns NULL rather than raising an error, allowing the row to be evaluated by the NULL filter (see Filtering below).

All coordinate columns use `TRY_CAST(... AS FLOAT)`. Latitude and longitude values that can't be parsed become NULL.

### Filtering
A row is excluded from the production table if any of the following critical fields are NULL after casting:
- `ride_id`
- `rideable_type`
- `started_at`
- `ended_at`
- `member_casual`

This filtering removed **2,736 rows** from the 5,623,280-row raw source, leaving 5,620,544 in production. These rows had missing or unparseable values in fields required for any meaningful analysis. The excluded rows appear to be predominantly casual rider records.

> **Note on Power BI comparison:** The Power BI report was built directly from the raw CSVs without this filtering step, giving a total of 5,623,280 rows. This explains the small count-based difference between the two tools. All percentage and ratio measures match exactly between SQL Server and Power BI, since the 2,736 excluded rows do not meaningfully affect proportions.

### Computed Column: ride_time_min
```sql
CASE WHEN DATEDIFF(SECOND, TRY_CAST(started_at AS DATETIME2),
                            TRY_CAST(ended_at   AS DATETIME2)) > 0
     THEN DATEDIFF(SECOND, TRY_CAST(started_at AS DATETIME2),
                            TRY_CAST(ended_at   AS DATETIME2)) / 60.0
     ELSE NULL
END
```
Duration is stored in decimal minutes. Negative durations (where `ended_at` precedes `started_at`) are set to NULL rather than a negative number, as they represent data anomalies — likely maintenance pulls or system errors rather than real rides.

### Computed Column: ride_distance_mi
Straight-line distance between start and end coordinates is calculated using the **Haversine formula**, which accounts for the curvature of the Earth:

```sql
CASE
    WHEN start_lat IS NOT NULL AND start_lng IS NOT NULL
     AND end_lat   IS NOT NULL AND end_lng   IS NOT NULL
    THEN
        3958.8 * 2 * ATN2(
            SQRT(
                POWER(SIN(RADIANS(end_lat - start_lat) / 2), 2) +
                COS(RADIANS(start_lat)) * COS(RADIANS(end_lat)) *
                POWER(SIN(RADIANS(end_lng - start_lng) / 2), 2)
            ),
            SQRT(1 - (
                POWER(SIN(RADIANS(end_lat - start_lat) / 2), 2) +
                COS(RADIANS(start_lat)) * COS(RADIANS(end_lat)) *
                POWER(SIN(RADIANS(end_lng - start_lng) / 2), 2)
            ))
        )
    ELSE NULL
END
```

The Earth's radius constant (3958.8 miles) gives the result in miles. Rides with any missing coordinate are set to NULL. Note that this is a straight-line ("as the crow flies") distance, not the actual route ridden — it underestimates true ride distance but is consistent and suitable for comparative analysis.

---

## Error Handling Summary

| Layer | Mechanism | Destination |
|---|---|---|
| Data Flow | Error output redirection | `stg.Trips_Errors` |
| Row count validation | Threshold check, abort on failure | `dbo.ETL_ErrorLog` (via OnError) |
| Package-level failures | OnError event handler | `dbo.ETL_ErrorLog` |

---

## Notable Challenges and Resolutions

### Text Qualifier on Date Fields
During initial load, all `TRY_CAST` operations on `started_at` and `ended_at` returned NULL — meaning zero rows were inserted into the production table. Diagnostic query `03_inspect_stg_dates.sql` revealed that date values were stored in the CSVs with surrounding double-quote characters (e.g., `"2025-04-28 08:14:22"`), making the raw string unparseable as a datetime. The fix was setting the Text Qualifier property to `"` in the CSV_Source flat file connection manager, which caused SSIS to strip the quotes during the read.

### Unicode / Non-Unicode Type Mismatch
SSIS flat file sources default to non-unicode (`DT_STR`) column types, which cannot map to NVARCHAR (`DT_WSTR`) destination columns. All source columns were changed to `DT_WSTR` in the flat file source's Advanced Editor to resolve the type mismatch.

### Variable Expression for source_file
The SSIS Derived Column component requires explicit casting of package variables when the destination column has a defined width. The expression `@[User::CurrentFile]` alone produced a length of 0; the correct form is `(DT_WSTR, 255) @[User::CurrentFile]`.

### Missing Source File (January 2026)
After the initial load, the month coverage query (`04_validate_month_coverage.sql`) revealed only 18 rows for January 2026 — far fewer than expected. Investigation confirmed the January 2026 CSV had been lost during a prior file recovery. The file was re-downloaded from the Divvy data portal and the full load was re-run, restoring the expected ~137,782 January rows.

---

## Data Quality Outcomes

| Metric | Value |
|---|---|
| Source files processed | 12 |
| Raw rows in source CSVs | 5,623,280 |
| Rows excluded (missing critical fields) | 2,736 |
| Rows loaded to production | 5,620,544 |
| Error rows in stg.Trips_Errors | 0 |
| ETL_ErrorLog entries | 0 |
| Month coverage | April 2025 – March 2026 (complete) |
