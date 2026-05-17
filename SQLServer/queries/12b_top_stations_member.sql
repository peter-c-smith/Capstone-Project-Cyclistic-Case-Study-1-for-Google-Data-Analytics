-- ============================================================
-- 12b_top_stations_member.sql
-- Cyclistic Bike-Share Case Study — Top 10 Stations by Member Starts
--
-- Companion to 12_top_stations.sql (which covers casual top 10).
-- Expected: commuter hubs, transit connections, neighborhood
-- stations — contrasting with casual's lakefront tourist cluster.
-- ============================================================

USE CyclisticCaseStudy;
GO

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
