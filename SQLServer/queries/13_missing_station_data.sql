-- ============================================================
-- 13_missing_station_data.sql
-- Cyclistic Bike-Share Case Study — Missing Station Data
--
-- Business question: How prevalent is missing station data, and
-- does it differ between rider types or bike types?
--
-- Context: Electric bikes can be locked at any rack, not just
-- docking stations, so they frequently have no station name.
-- Missing station data affects station-based analyses and is
-- worth quantifying for data quality transparency.
-- ============================================================

USE CyclisticCaseStudy;
GO

-- Part 1: Overall missing station data summary
SELECT
    -- Start station missing
    SUM(CASE WHEN start_station_name IS NULL
              OR start_station_name = ''
             THEN 1 ELSE 0 END)                     AS missing_start_station,
    CAST(ROUND(100.0 *
        SUM(CASE WHEN start_station_name IS NULL
                  OR start_station_name = ''
                 THEN 1 ELSE 0 END)
        / COUNT(*), 1) AS DECIMAL(5,1))             AS missing_start_pct,

    -- End station missing
    SUM(CASE WHEN end_station_name IS NULL
              OR end_station_name = ''
             THEN 1 ELSE 0 END)                     AS missing_end_station,
    CAST(ROUND(100.0 *
        SUM(CASE WHEN end_station_name IS NULL
                  OR end_station_name = ''
                 THEN 1 ELSE 0 END)
        / COUNT(*), 1) AS DECIMAL(5,1))             AS missing_end_pct,

    -- Both missing
    SUM(CASE WHEN (start_station_name IS NULL OR start_station_name = '')
              AND (end_station_name   IS NULL OR end_station_name   = '')
             THEN 1 ELSE 0 END)                     AS missing_both,
    CAST(ROUND(100.0 *
        SUM(CASE WHEN (start_station_name IS NULL OR start_station_name = '')
                  AND (end_station_name   IS NULL OR end_station_name   = '')
                 THEN 1 ELSE 0 END)
        / COUNT(*), 1) AS DECIMAL(5,1))             AS missing_both_pct

FROM dbo.Trips;
GO

-- Part 2: Missing start station by rider type and bike type
SELECT
    member_casual,
    rideable_type,
    COUNT(*)                                        AS total_rides,
    SUM(CASE WHEN start_station_name IS NULL
              OR start_station_name = ''
             THEN 1 ELSE 0 END)                     AS missing_start,
    CAST(ROUND(100.0 *
        SUM(CASE WHEN start_station_name IS NULL
                  OR start_station_name = ''
                 THEN 1 ELSE 0 END)
        / COUNT(*), 1) AS DECIMAL(5,1))             AS missing_start_pct
FROM dbo.Trips
GROUP BY member_casual, rideable_type
ORDER BY member_casual, rideable_type;
GO
