-- ============================================================
-- 03_create_trips.sql
-- Creates the production table dbo.Trips.
--
-- Design decisions:
--   trip_id   — surrogate identity PK, guarantees row uniqueness
--               regardless of source data quality issues
--   ride_id   — natural key from source CSV, enforced UNIQUE
--               but not the clustered PK; duplicate ride_ids
--               in source data will be caught here
--   DATETIME2 — used over DATETIME for higher precision and
--               a wider supported date range
--   DECIMAL(10,6) — coordinate precision to ~10cm, sufficient
--               for Haversine distance calculations
--   DECIMAL(10,4) — ride_time_min precision for duration aggregations
--   ride_time_min / ride_distance_mi — calculated during SSIS
--               transformation and stored as columns for query
--               performance; not computed on the fly at query time
--   source_file NOT NULL — SSIS always populates this field
--   member_casual CHECK — only 'member' or 'casual' are valid;
--               constraint will surface any unexpected values
--               slipping through from source data
--   rideable_type — no CHECK constraint; current values are
--               classic_bike and electric_bike but docked_bike
--               may appear in future data
--
-- Safe to re-run — drops and recreates the table.
-- Run 04_create_indexes.sql after this script.
-- ============================================================

USE CyclisticCaseStudy;
GO

DROP TABLE IF EXISTS dbo.Trips;
GO

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
GO

PRINT 'Table [dbo].[Trips] created.';
GO
