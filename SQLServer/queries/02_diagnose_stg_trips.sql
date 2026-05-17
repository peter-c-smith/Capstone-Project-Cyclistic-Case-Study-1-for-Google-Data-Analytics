-- ============================================================
-- 02_diagnose_stg_trips.sql
-- Diagnoses why rows may be failing the stg → dbo transform.
-- Run this if dbo.Trips is empty after a load.
-- ============================================================

USE CyclisticCaseStudy;
GO

-- Sample 5 raw rows to inspect actual values
SELECT TOP 5
    ride_id,
    rideable_type,
    started_at,
    ended_at,
    member_casual,
    source_file
FROM stg.Trips;
GO

-- Check how many rows pass each WHERE condition individually
SELECT
    COUNT(*)                                                    AS total_rows,
    SUM(CASE WHEN ride_id IS NOT NULL
             AND ride_id <> '' THEN 1 ELSE 0 END)              AS ride_id_ok,
    SUM(CASE WHEN rideable_type IS NOT NULL
             AND rideable_type <> '' THEN 1 ELSE 0 END)        AS rideable_type_ok,
    SUM(CASE WHEN TRY_CAST(started_at AS DATETIME2)
             IS NOT NULL THEN 1 ELSE 0 END)                    AS started_at_ok,
    SUM(CASE WHEN TRY_CAST(ended_at AS DATETIME2)
             IS NOT NULL THEN 1 ELSE 0 END)                    AS ended_at_ok,
    SUM(CASE WHEN member_casual IS NOT NULL
             AND member_casual <> '' THEN 1 ELSE 0 END)        AS member_casual_ok,
    SUM(CASE WHEN ride_id IS NOT NULL AND ride_id <> ''
             AND rideable_type IS NOT NULL AND rideable_type <> ''
             AND TRY_CAST(started_at AS DATETIME2) IS NOT NULL
             AND TRY_CAST(ended_at AS DATETIME2) IS NOT NULL
             AND member_casual IS NOT NULL
             AND member_casual <> '' THEN 1 ELSE 0 END)        AS all_conditions_pass
FROM stg.Trips;
GO
