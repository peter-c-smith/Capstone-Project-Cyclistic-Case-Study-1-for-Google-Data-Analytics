-- ============================================================
-- 06_avg_duration_distance.sql
-- Cyclistic Bike-Share Case Study — Avg Duration & Distance
--
-- Business question: Do casual riders take longer or farther
-- rides than members on average?
--
-- Validates against: Page 1 Executive Summary
--   - Avg Ride Duration card (16.06 min)
--   - Avg Ride Distance card (1.46 mi)
-- And: Page 2 Ride Behavior
--   - Avg Duration Member / Avg Duration Casual card pair
--   - Avg Ride Distance Member / Avg Ride Distance Casual card pair
--   - Duration Ratio Casual to Member (1.82)
--   - Distance Ratio Casual to Member (1.03)
--
-- Note: Matches DAX AVERAGEX(FILTER(..., > 0)) logic by
-- excluding zero and NULL durations/distances from averages.
-- ============================================================

USE CyclisticCaseStudy;
GO

-- Pre-label each row with positive-only metric values.
-- NULL is returned for zero/missing values so they are naturally
-- excluded from AVG without repeating the filter condition inline.
WITH RideMetrics AS (
    SELECT
        member_casual,
        CASE WHEN ride_time_min    > 0 THEN ride_time_min    END AS duration_min,
        CASE WHEN ride_distance_mi > 0 THEN ride_distance_mi END AS distance_mi
    FROM dbo.Trips
)
SELECT
    -- Overall averages
    CAST(ROUND(AVG(duration_min), 2) AS DECIMAL(10,2))               AS avg_duration_all_min,
    CAST(ROUND(AVG(distance_mi),  2) AS DECIMAL(10,2))               AS avg_distance_all_mi,

    -- Member averages
    CAST(ROUND(AVG(CASE WHEN member_casual = 'member'
                        THEN duration_min END), 2) AS DECIMAL(10,2)) AS avg_duration_member_min,
    CAST(ROUND(AVG(CASE WHEN member_casual = 'member'
                        THEN distance_mi  END), 2) AS DECIMAL(10,2)) AS avg_distance_member_mi,

    -- Casual averages
    CAST(ROUND(AVG(CASE WHEN member_casual = 'casual'
                        THEN duration_min END), 2) AS DECIMAL(10,2)) AS avg_duration_casual_min,
    CAST(ROUND(AVG(CASE WHEN member_casual = 'casual'
                        THEN distance_mi  END), 2) AS DECIMAL(10,2)) AS avg_distance_casual_mi,

    -- Ratios (casual vs member)
    CAST(ROUND(
        AVG(CASE WHEN member_casual = 'casual' THEN duration_min END) /
        NULLIF(AVG(CASE WHEN member_casual = 'member' THEN duration_min END), 0)
    , 2) AS DECIMAL(10,2))                                           AS duration_ratio_casual_to_member,

    CAST(ROUND(
        AVG(CASE WHEN member_casual = 'casual' THEN distance_mi END) /
        NULLIF(AVG(CASE WHEN member_casual = 'member' THEN distance_mi END), 0)
    , 2) AS DECIMAL(10,2))                                           AS distance_ratio_casual_to_member

FROM RideMetrics;
GO
