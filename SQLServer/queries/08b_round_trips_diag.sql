-- ============================================================
-- 08b_round_trips_diag.sql
-- Cyclistic Bike-Share Case Study — Round Trip Definition Diag
--
-- Purpose: Investigate why 08_round_trips.sql results (~2% member,
-- ~6% casual, ratio 3.01) don't match Power BI (~11% member,
-- ~18% casual, ratio 1.63).
--
-- Hypothesis: Power BI DAX treats BLANK() = BLANK() as TRUE,
-- so rides where BOTH start and end station names are empty/NULL
-- are counted as round trips. Our SQL excludes those rows.
--
-- This query tests both definitions side by side and counts the
-- "blank-blank" rides that would explain the gap.
-- ============================================================

USE CyclisticCaseStudy;
GO

-- 1. How many rides have both stations empty/NULL?
--    These would count as round trips in Power BI but not in our SQL.
SELECT
    member_casual,
    COUNT(*)                                        AS both_stations_blank,
    CAST(ROUND(100.0 * COUNT(*) /
        SUM(COUNT(*)) OVER (PARTITION BY member_casual), 1)
    AS DECIMAL(5,1))                                AS pct_of_rider_type
FROM dbo.Trips
WHERE (start_station_name IS NULL OR start_station_name = '')
  AND (end_station_name   IS NULL OR end_station_name   = '')
GROUP BY member_casual;
GO

-- 2. Broad definition: start = end (including empty string matches,
--    but still excluding NULLs since NULL = NULL is UNKNOWN in SQL)
SELECT
    member_casual,
    COUNT(*)                                        AS total_rides,
    SUM(CASE WHEN start_station_name = end_station_name
             THEN 1 ELSE 0 END)                     AS round_trips_broad,
    CAST(ROUND(100.0 *
        SUM(CASE WHEN start_station_name = end_station_name
                 THEN 1 ELSE 0 END)
        / COUNT(*), 1) AS DECIMAL(5,1))             AS round_trip_pct_broad
FROM dbo.Trips
GROUP BY member_casual;
GO

-- 3. Broadest definition: ISNULL to empty string so NULL=NULL matches too
SELECT
    member_casual,
    COUNT(*)                                        AS total_rides,
    SUM(CASE WHEN ISNULL(start_station_name,'') = ISNULL(end_station_name,'')
             THEN 1 ELSE 0 END)                     AS round_trips_isnull,
    CAST(ROUND(100.0 *
        SUM(CASE WHEN ISNULL(start_station_name,'') = ISNULL(end_station_name,'')
                 THEN 1 ELSE 0 END)
        / COUNT(*), 1) AS DECIMAL(5,1))             AS round_trip_pct_isnull
FROM dbo.Trips
GROUP BY member_casual;
GO
