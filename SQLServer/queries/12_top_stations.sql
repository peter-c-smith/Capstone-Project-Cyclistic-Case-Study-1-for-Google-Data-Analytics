-- ============================================================
-- 12_top_stations.sql
-- Cyclistic Bike-Share Case Study — Top Start Stations
--
-- Business question: Which stations are most popular, and do
-- casual and member riders concentrate at different locations?
--
-- Validates against: Page 3 Geographic Analysis
--   - Top stations tables / map visual
--
-- Note: Rides with missing start_station_name are excluded.
-- Results are split into top 10 by member starts and top 10
-- by casual starts — the two lists are expected to diverge,
-- reflecting commuter hubs (members) vs tourist/leisure
-- destinations (casuals).
-- ============================================================

USE CyclisticCaseStudy;
GO

-- Part 1: Top 10 stations by member ride starts
WITH StationCounts AS (
    SELECT
        start_station_name,
        SUM(CASE WHEN member_casual = 'member' THEN 1 ELSE 0 END) AS member_starts,
        SUM(CASE WHEN member_casual = 'casual' THEN 1 ELSE 0 END) AS casual_starts,
        COUNT(*)                                                   AS total_starts
    FROM dbo.Trips
    WHERE start_station_name IS NOT NULL
      AND start_station_name <> ''
    GROUP BY start_station_name
)
SELECT TOP 10
    start_station_name,
    member_starts,
    casual_starts,
    total_starts,
    CAST(ROUND(100.0 * member_starts / NULLIF(total_starts, 0), 1)
         AS DECIMAL(5,1))                                          AS member_pct
FROM StationCounts
ORDER BY member_starts DESC;
GO

-- Part 2: Top 10 stations by casual ride starts
WITH StationCounts AS (
    SELECT
        start_station_name,
        SUM(CASE WHEN member_casual = 'member' THEN 1 ELSE 0 END) AS member_starts,
        SUM(CASE WHEN member_casual = 'casual' THEN 1 ELSE 0 END) AS casual_starts,
        COUNT(*)                                                   AS total_starts
    FROM dbo.Trips
    WHERE start_station_name IS NOT NULL
      AND start_station_name <> ''
    GROUP BY start_station_name
)
SELECT TOP 10
    start_station_name,
    casual_starts,
    member_starts,
    total_starts,
    CAST(ROUND(100.0 * casual_starts / NULLIF(total_starts, 0), 1)
         AS DECIMAL(5,1))                                          AS casual_pct
FROM StationCounts
ORDER BY casual_starts DESC;
GO
