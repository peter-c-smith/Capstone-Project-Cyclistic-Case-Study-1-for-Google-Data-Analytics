-- ============================================================
-- 01_validate_ride_id_duplicates.sql
-- Checks stg.Trips for duplicate ride_id values before the
-- staging-to-production load runs.
--
-- ride_id is assumed to be the natural unique key for each trip.
-- Duplicates in the source data will be caught by the UQ_Trips_ride_id
-- constraint on dbo.Trips and cause the SSIS load to fail.
-- Running this query first identifies duplicates so they can be
-- investigated before the load is attempted.
--
-- A result set with rows indicates duplicates exist and the load
-- should be paused for investigation. An empty result set means
-- ride_id is clean across all loaded source files.
-- ============================================================

USE CyclisticCaseStudy;
GO

SELECT
    ride_id,
    COUNT(*)        AS duplicate_count,
    MIN(source_file) AS first_seen_in,
    MAX(source_file) AS last_seen_in
FROM stg.Trips
GROUP BY ride_id
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;
