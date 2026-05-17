-- ============================================================
-- 05_core_ride_counts.sql
-- Cyclistic Bike-Share Case Study — Core Ride Counts
--
-- Business question: How are rides distributed between annual
-- members and casual riders?
--
-- Validates against: Page 1 Executive Summary
--   - Total Rides card
--   - Member Ride % card
--   - Donut chart (Member Rides vs Casual Rides)
-- ============================================================

USE CyclisticCaseStudy;
GO

SELECT
    -- Totals
    COUNT(*)                                        AS total_rides,

    -- Member / Casual counts
    SUM(CASE WHEN member_casual = 'member'
             THEN 1 ELSE 0 END)                     AS member_rides,
    SUM(CASE WHEN member_casual = 'casual'
             THEN 1 ELSE 0 END)                     AS casual_rides,

    -- Percentages
    CAST(
        ROUND(
            100.0 * SUM(CASE WHEN member_casual = 'member'
                             THEN 1 ELSE 0 END)
            / COUNT(*), 1)
    AS DECIMAL(5,1))                                AS member_ride_pct,

    CAST(
        ROUND(
            100.0 * SUM(CASE WHEN member_casual = 'casual'
                             THEN 1 ELSE 0 END)
            / COUNT(*), 1)
    AS DECIMAL(5,1))                                AS casual_ride_pct

FROM dbo.Trips;
GO
