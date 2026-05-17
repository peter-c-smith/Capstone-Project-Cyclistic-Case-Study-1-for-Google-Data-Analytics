-- ============================================================
-- 04_validate_month_coverage.sql
-- Confirms which months are present in dbo.Trips and how many
-- rides each month contains. Expected: April 2025 – March 2026.
-- A missing month indicates a source file was not loaded.
-- ============================================================

USE CyclisticCaseStudy;
GO

SELECT
    FORMAT(started_at, 'yyyy-MM')   AS year_month,
    COUNT(*)                        AS ride_count,
    MIN(started_at)                 AS earliest_ride,
    MAX(started_at)                 AS latest_ride
FROM dbo.Trips
GROUP BY FORMAT(started_at, 'yyyy-MM')
ORDER BY year_month;
GO
