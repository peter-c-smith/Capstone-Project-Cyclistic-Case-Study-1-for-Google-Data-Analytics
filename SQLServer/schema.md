# SQL Server Schema Documentation
## Cyclistic Bike-Share Case Study

This document describes the SQL Server database schema used for the Cyclistic case study analysis. The schema follows a staging-to-production pattern — raw CSV data is loaded into a staging table first, then transformed and loaded into the final Trips table.

---

## Database

**Name:** CyclisticCaseStudy
**Version:** SQL Server 2022
**Location:** D:\SQLDataFiles\

---

## Tables

### stg_Trips (Staging Table)

Receives raw CSV data directly from the SSIS package. All columns are NVARCHAR to accept data without type conversion errors during import. Records are validated and transformed before being loaded into the Trips table.

```sql
CREATE TABLE stg_Trips
(
    ride_id             NVARCHAR(50),
    rideable_type       NVARCHAR(50),
    started_at          NVARCHAR(50),
    ended_at            NVARCHAR(50),
    start_station_name  NVARCHAR(100),
    start_station_id    NVARCHAR(50),
    end_station_name    NVARCHAR(100),
    end_station_id      NVARCHAR(50),
    start_lat           NVARCHAR(50),
    start_lng           NVARCHAR(50),
    end_lat             NVARCHAR(50),
    end_lng             NVARCHAR(50),
    member_casual       NVARCHAR(50),
    source_file         NVARCHAR(255)
);
```

**Design notes:**
- All columns accept NVARCHAR to prevent import failures caused by unexpected values or formatting inconsistencies in source files
- `source_file` is not present in the source CSV — it is populated by the SSIS package with the filename of each source file for traceability and load verification

---

### Trips (Production Table)

Final analytical table containing validated, typed, and enriched ride records. This is the table queried by all analytical SQL in this project.

```sql
CREATE TABLE Trips
(
    ride_id             NVARCHAR(50)        NOT NULL,
    rideable_type       NVARCHAR(50)        NOT NULL,
    started_at          DATETIME2           NOT NULL,
    ended_at            DATETIME2           NOT NULL,
    start_station_name  NVARCHAR(100)       NULL,
    start_station_id    NVARCHAR(50)        NULL,
    end_station_name    NVARCHAR(100)       NULL,
    end_station_id      NVARCHAR(50)        NULL,
    start_lat           DECIMAL(10, 6)      NULL,
    start_lng           DECIMAL(10, 6)      NULL,
    end_lat             DECIMAL(10, 6)      NULL,
    end_lng             DECIMAL(10, 6)      NULL,
    member_casual       NVARCHAR(10)        NOT NULL,
    ride_time_min       DECIMAL(10, 4)      NULL,
    ride_distance_mi    DECIMAL(10, 6)      NULL,
    source_file         NVARCHAR(255)       NULL,
    CONSTRAINT PK_Trips PRIMARY KEY CLUSTERED (ride_id)
);

-- Indexes
CREATE INDEX IX_Trips_member_casual
ON Trips (member_casual);

CREATE INDEX IX_Trips_started_at
ON Trips (started_at);

CREATE INDEX IX_Trips_rideable_type
ON Trips (rideable_type);

CREATE INDEX IX_Trips_start_station_name
ON Trips (start_station_name);
```

**Design notes:**
- `DATETIME2` is used over `DATETIME` for higher precision and a wider supported date range
- `DECIMAL(10, 6)` for coordinate fields provides precision to approximately 10cm — sufficient for geographic distance calculations
- `DECIMAL(10, 4)` for `ride_time_min` provides four decimal places of precision for duration aggregations
- `ride_time_min` and `ride_distance_mi` are calculated during the SSIS transformation step and stored as columns rather than computed on the fly — this improves query performance at analytical query time
- Station name and coordinate fields are nullable — missing values are expected, particularly for electric bike rides
- `source_file` is carried through from staging for traceability
- Primary key on `ride_id` provides a clustered index on the natural key
- Non-clustered indexes on `member_casual`, `started_at`, `rideable_type`, and `start_station_name` support the most common analytical query filters

---

## Staging to Production Pattern

Raw CSV data → `stg_Trips` (SSIS Flat File import) → validation and transformation → `Trips` (SSIS OLE DB destination)

The staging table is truncated before each load to support full reloads. The Trips table is also truncated before each load — this is a full refresh pattern rather than incremental. For a dataset of this size a full refresh is appropriate and simpler to maintain.