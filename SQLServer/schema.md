# SQL Server Schema Documentation
## Cyclistic Bike-Share Case Study

This document describes the SQL Server database schema used for the Cyclistic case study analysis. The schema follows a staging-to-production pattern — raw CSV data is loaded into a staging table first, then transformed and loaded into the final Trips table.

---

## Database

**Name:** CyclisticCaseStudy
**Version:** SQL Server 2022
**Data files location:** D:\SQLDataFiles\

---

## Schemas

| Schema | Purpose |
|--------|---------|
| `dbo` | Production tables — typed, validated, analytical data |
| `stg` | Staging tables — raw CSV data as received from SSIS import |

The `stg` schema is created by `schema/01_create_schemas.sql`.

---

## Tables

### stg.Trips (Staging Table)

Receives raw CSV data directly from the SSIS flat file import. All columns are NVARCHAR to accept data without type conversion errors during import. Records are validated and transformed before being loaded into `dbo.Trips`.

```sql
CREATE TABLE stg.Trips
(
    ride_id             NVARCHAR(50)        NULL,
    rideable_type       NVARCHAR(50)        NULL,
    started_at          NVARCHAR(50)        NULL,
    ended_at            NVARCHAR(50)        NULL,
    start_station_name  NVARCHAR(100)       NULL,
    start_station_id    NVARCHAR(50)        NULL,
    end_station_name    NVARCHAR(100)       NULL,
    end_station_id      NVARCHAR(50)        NULL,
    start_lat           NVARCHAR(50)        NULL,
    start_lng           NVARCHAR(50)        NULL,
    end_lat             NVARCHAR(50)        NULL,
    end_lng             NVARCHAR(50)        NULL,
    member_casual       NVARCHAR(50)        NULL,
    source_file         NVARCHAR(255)       NOT NULL
);
```

**Design notes:**
- All data columns accept NULL — type validation happens downstream in the SSIS transformation, not at import time
- `source_file` is NOT NULL — it is always populated by SSIS with the filename of each source CSV for traceability and load verification
- `source_file` is not present in the source CSV files; SSIS injects it as a derived column

---

### dbo.Trips (Production Table)

Final analytical table containing validated, typed, and enriched ride records. This is the table queried by all analytical SQL in this project.

```sql
CREATE TABLE dbo.Trips
(
    trip_id             INT             NOT NULL    IDENTITY(1,1),
    ride_id             NVARCHAR(50)    NOT NULL,
    rideable_type       NVARCHAR(50)    NOT NULL,
    started_at          DATETIME2       NOT NULL,
    ended_at            DATETIME2       NOT NULL,
    start_station_name  NVARCHAR(100)   NULL,
    start_station_id    NVARCHAR(50)    NULL,
    end_station_name    NVARCHAR(100)   NULL,
    end_station_id      NVARCHAR(50)    NULL,
    start_lat           DECIMAL(10, 6)  NULL,
    start_lng           DECIMAL(10, 6)  NULL,
    end_lat             DECIMAL(10, 6)  NULL,
    end_lng             DECIMAL(10, 6)  NULL,
    member_casual       NVARCHAR(10)    NOT NULL,
    ride_time_min       DECIMAL(10, 4)  NULL,
    ride_distance_mi    DECIMAL(10, 6)  NULL,
    source_file         NVARCHAR(255)   NOT NULL,

    CONSTRAINT PK_Trips
        PRIMARY KEY CLUSTERED (trip_id),

    CONSTRAINT UQ_Trips_ride_id
        UNIQUE (ride_id),

    CONSTRAINT CK_Trips_member_casual
        CHECK (member_casual IN ('member', 'casual'))
);

-- Non-clustered indexes
CREATE INDEX IX_Trips_member_casual    ON dbo.Trips (member_casual);
CREATE INDEX IX_Trips_started_at       ON dbo.Trips (started_at);
CREATE INDEX IX_Trips_rideable_type    ON dbo.Trips (rideable_type);
CREATE INDEX IX_Trips_start_station_name ON dbo.Trips (start_station_name);
```

**Design notes:**

- `trip_id` is a surrogate identity key — the clustered PK. It guarantees every row is uniquely addressable regardless of source data quality issues with `ride_id`.
- `ride_id` is the natural key from the source CSV. It carries a UNIQUE constraint (`UQ_Trips_ride_id`) which enforces source data integrity and surfaces duplicate records as a load error rather than silently accepting them.
- `ride_id` is assumed to be unique across all 12 source CSV files. The validation query `queries/01_validate_ride_id_duplicates.sql` should be run against `stg.Trips` before each production load to confirm this assumption holds.
- `DATETIME2` is used over `DATETIME` for higher precision and a wider supported date range.
- `DECIMAL(10, 6)` for coordinate fields provides precision to approximately 10cm — sufficient for Haversine distance calculations.
- `DECIMAL(10, 4)` for `ride_time_min` provides four decimal places of precision for duration aggregations.
- `ride_time_min` and `ride_distance_mi` are calculated during the SSIS transformation step and stored as columns rather than computed on the fly — this improves query performance at analytical query time.
- `source_file` is NOT NULL — SSIS always populates this field. A NULL value would indicate a load process failure.
- `member_casual` carries a CHECK constraint enforcing only `'member'` or `'casual'`. Any unexpected value from source data will cause a constraint violation and surface the issue immediately.
- `rideable_type` has no CHECK constraint — current values are `classic_bike` and `electric_bike`, but `docked_bike` may appear in future data. Locking this down would require a schema change to accommodate new bike types.
- Station name and coordinate fields are nullable — missing values are expected, particularly for electric bike rides which can be docked at any public rack.

---

## Staging to Production Pattern

```
Raw CSV files
    → stg.Trips       (SSIS Flat File source → OLE DB destination, all NVARCHAR)
    → [validation]    (duplicate ride_id check, null checks, range checks)
    → dbo.Trips       (SSIS OLE DB source → OLE DB destination, typed + enriched)
```

The staging table is truncated before each load. The production Trips table is also truncated before each load — this is a full refresh pattern rather than incremental. For a dataset of this size a full refresh is simpler to maintain and eliminates the risk of stale or orphaned records.

---

## Script Execution Order

Run scripts in this order when rebuilding the schema from scratch:

| Order | Script | Purpose |
|-------|--------|---------|
| 1 | `schema/01_create_schemas.sql` | Creates the `stg` schema |
| 2 | `schema/02_create_stg_trips.sql` | Creates `stg.Trips` |
| 3 | `schema/03_create_trips.sql` | Creates `dbo.Trips` with constraints |
| 4 | `schema/04_create_indexes.sql` | Creates non-clustered indexes on `dbo.Trips` |

All scripts are safe to re-run — they drop and recreate objects cleanly.
