-- ============================================================
-- 02_create_stg_trips.sql
-- Creates the staging table stg.Trips.
--
-- All columns are NVARCHAR to accept raw CSV data without
-- type conversion failures during import. Type casting and
-- validation happen in the SSIS transformation step.
--
-- source_file is NOT NULL — SSIS always populates it with
-- the source CSV filename for traceability.
--
-- NOTE: Drops dbo.stg_Trips (legacy name) if present, then
-- drops and recreates stg.Trips. Safe to re-run.
-- ============================================================

USE CyclisticCaseStudy;
GO

-- Remove legacy table if it exists from before the stg schema was introduced
DROP TABLE IF EXISTS dbo.stg_Trips;
GO

-- Drop and recreate stg.Trips
DROP TABLE IF EXISTS stg.Trips;
GO

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
GO

PRINT 'Table [stg].[Trips] created.';
GO
