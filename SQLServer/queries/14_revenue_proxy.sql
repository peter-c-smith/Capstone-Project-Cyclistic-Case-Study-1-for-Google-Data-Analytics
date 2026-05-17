-- ============================================================
-- 14_revenue_proxy.sql
-- Cyclistic Bike-Share Case Study — Revenue Proxy Analysis
--
-- Business question: What is the estimated revenue difference
-- between casual and member pricing, and what is the potential
-- upside of converting casual riders to members?
--
-- IMPORTANT: These are illustrative estimates using publicly
-- available Divvy pricing as of the analysis period. Actual
-- Cyclistic pricing may differ. The purpose is to demonstrate
-- the revenue framing of the conversion opportunity, not to
-- produce auditable financial figures.
--
-- Pricing assumptions (Divvy, ~2025):
--   Member:       $9.99/month (~$119.88/yr) unlimited classic
--                 rides; e-bike rides: +$0.18/min
--   Casual single ride: $1.00 unlock + $0.18/min (classic)
--                       $1.00 unlock + $0.18/min (electric)
--   Casual day pass:    $15.00 flat (assumed ~3 rides avg)
--
-- Simplification: model all casual rides as single-ride at
-- unlock + per-minute rate. This overstates casual revenue
-- slightly (some use day passes) but is conservative for the
-- conversion argument.
-- ============================================================

USE CyclisticCaseStudy;
GO

WITH RideMetrics AS (
    SELECT
        member_casual,
        rideable_type,
        COUNT(*)                                    AS total_rides,
        AVG(CASE WHEN ride_time_min > 0
                 THEN ride_time_min END)            AS avg_duration_min,
        SUM(CASE WHEN ride_time_min > 0
                 THEN ride_time_min END)            AS total_minutes
    FROM dbo.Trips
    GROUP BY member_casual, rideable_type
)
SELECT
    member_casual,
    rideable_type,
    total_rides,
    CAST(ROUND(avg_duration_min, 2) AS DECIMAL(8,2)) AS avg_duration_min,

    -- Estimated revenue per ride (casual only — unlock + per-min)
    CASE
        WHEN member_casual = 'casual'
        THEN CAST(ROUND(
                total_rides * 1.00          -- unlock fee
                + total_minutes * 0.18      -- per-minute
             , 2) AS DECIMAL(12,2))
        ELSE NULL
    END                                             AS est_casual_revenue,

    -- For members: flat monthly fee portion is not per-ride,
    -- but e-bike overage is. Show e-bike overage revenue only.
    CASE
        WHEN member_casual = 'member' AND rideable_type = 'electric_bike'
        THEN CAST(ROUND(total_minutes * 0.18, 2) AS DECIMAL(12,2))
        ELSE NULL
    END                                             AS est_member_ebike_overage

FROM RideMetrics
ORDER BY member_casual, rideable_type;
GO

-- Summary: total estimated casual revenue vs member e-bike overage
-- (excludes membership subscription revenue which is not per-ride)
SELECT
    SUM(CASE WHEN member_casual = 'casual'
             THEN total_rides * 1.00 + total_minutes * 0.18
             ELSE 0 END)                            AS total_est_casual_revenue,

    SUM(CASE WHEN member_casual = 'member'
              AND rideable_type = 'electric_bike'
             THEN total_minutes * 0.18
             ELSE 0 END)                            AS total_est_member_ebike_overage,

    -- Total member rides (for context / membership revenue framing)
    SUM(CASE WHEN member_casual = 'member'
             THEN total_rides ELSE 0 END)           AS member_ride_count
FROM (
    SELECT
        member_casual,
        rideable_type,
        COUNT(*)                                    AS total_rides,
        SUM(CASE WHEN ride_time_min > 0
                 THEN ride_time_min END)            AS total_minutes
    FROM dbo.Trips
    GROUP BY member_casual, rideable_type
) base;
GO
