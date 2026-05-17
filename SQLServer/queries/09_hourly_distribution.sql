-- ============================================================
-- 09_hourly_distribution.sql
-- Cyclistic Bike-Share Case Study — Hourly Ride Distribution
--
-- Business question: At what hours of the day do members and
-- casual riders most frequently start rides?
--
-- Validates against: Page 2 Ride Behavior
--   - "Rides by Hour of Day" line chart
--     Members: dual peaks ~8 AM and ~5 PM (commute pattern)
--     Casual: single broad afternoon peak ~3–5 PM (leisure pattern)
-- ============================================================

USE CyclisticCaseStudy;
GO

-- Aggregate by hour, then join type totals for clean % calculation.
-- Using a CROSS JOIN to totals avoids nested window aggregates
-- (SUM(SUM(...)) OVER ()) and makes the percentage logic explicit.
WITH HourlyAgg AS (
    SELECT
        DATEPART(HOUR, started_at)                  AS hour_of_day,
        COUNT(*)                                    AS total_rides,
        SUM(CASE WHEN member_casual = 'member'
                 THEN 1 ELSE 0 END)                 AS member_rides,
        SUM(CASE WHEN member_casual = 'casual'
                 THEN 1 ELSE 0 END)                 AS casual_rides
    FROM dbo.Trips
    GROUP BY DATEPART(HOUR, started_at)
),
TypeTotals AS (
    SELECT
        SUM(member_rides)                           AS total_member,
        SUM(casual_rides)                           AS total_casual
    FROM HourlyAgg
)
SELECT
    h.hour_of_day,
    h.total_rides,
    h.member_rides,
    h.casual_rides,

    -- As % of each rider type's total (useful for shape comparison)
    CAST(ROUND(100.0 * h.member_rides
        / NULLIF(t.total_member, 0), 2) AS DECIMAL(6,2)) AS member_pct_of_type,
    CAST(ROUND(100.0 * h.casual_rides
        / NULLIF(t.total_casual, 0), 2) AS DECIMAL(6,2)) AS casual_pct_of_type

FROM HourlyAgg h
CROSS JOIN TypeTotals t
ORDER BY h.hour_of_day;
GO
