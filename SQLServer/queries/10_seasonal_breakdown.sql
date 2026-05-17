-- ============================================================
-- 10_seasonal_breakdown.sql
-- Cyclistic Bike-Share Case Study — Seasonal Ride Breakdown
--
-- Business question: How does ridership vary by season, and do
-- casual riders show stronger seasonal concentration than members?
--
-- Validates against: Page 2 Ride Behavior
--   - "Rides by Month" bar chart (seasonal shape)
-- And: Page 3 Temporal Patterns
--   - Seasonal ride distribution
--
-- Season definitions (Northern Hemisphere):
--   Spring: March, April, May
--   Summer: June, July, August
--   Fall:   September, October, November
--   Winter: December, January, February
-- ============================================================

USE CyclisticCaseStudy;
GO

-- Part 1: Monthly breakdown
SELECT
    FORMAT(started_at, 'yyyy-MM')                   AS ride_month,
    COUNT(*)                                        AS total_rides,
    SUM(CASE WHEN member_casual = 'member'
             THEN 1 ELSE 0 END)                     AS member_rides,
    SUM(CASE WHEN member_casual = 'casual'
             THEN 1 ELSE 0 END)                     AS casual_rides,
    CAST(ROUND(100.0 *
        SUM(CASE WHEN member_casual = 'casual' THEN 1 ELSE 0 END)
        / COUNT(*), 1) AS DECIMAL(5,1))             AS casual_pct
FROM dbo.Trips
GROUP BY FORMAT(started_at, 'yyyy-MM')
ORDER BY ride_month;
GO

-- Part 2: Season rollup
WITH SeasonRollup AS (
    SELECT
        CASE
            WHEN MONTH(started_at) IN (3,4,5)   THEN 'Spring'
            WHEN MONTH(started_at) IN (6,7,8)   THEN 'Summer'
            WHEN MONTH(started_at) IN (9,10,11) THEN 'Fall'
            ELSE                                     'Winter'
        END                                         AS season,
        member_casual
    FROM dbo.Trips
)
SELECT
    season,
    COUNT(*)                                        AS total_rides,
    SUM(CASE WHEN member_casual = 'member'
             THEN 1 ELSE 0 END)                     AS member_rides,
    SUM(CASE WHEN member_casual = 'casual'
             THEN 1 ELSE 0 END)                     AS casual_rides,
    CAST(ROUND(100.0 *
        SUM(CASE WHEN member_casual = 'member' THEN 1 ELSE 0 END)
        / COUNT(*), 1) AS DECIMAL(5,1))             AS member_pct,
    CAST(ROUND(100.0 *
        SUM(CASE WHEN member_casual = 'casual' THEN 1 ELSE 0 END)
        / COUNT(*), 1) AS DECIMAL(5,1))             AS casual_pct
FROM SeasonRollup
GROUP BY season
ORDER BY
    CASE season
        WHEN 'Spring' THEN 1
        WHEN 'Summer' THEN 2
        WHEN 'Fall'   THEN 3
        ELSE               4
    END;
GO
