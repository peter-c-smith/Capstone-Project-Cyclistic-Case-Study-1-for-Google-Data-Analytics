-- ============================================================
-- 07_weekend_weekday.sql
-- Cyclistic Bike-Share Case Study — Weekend vs Weekday
--
-- Business question: Do casual riders concentrate their usage
-- on weekends more than members?
--
-- Validates against: Page 2 Ride Behavior
--   - Weekend % bars in the clustered column chart (~24% member,
--     ~38% casual)
-- And: Page 1 Executive Summary
--   - Weekend Skew Ratio card (1.61)
--
-- Note: Weekday defined as Monday–Friday (DATEPART weekday 2–6
-- using Sunday=1 convention). Weekend = Saturday–Sunday.
-- ============================================================

USE CyclisticCaseStudy;
GO

-- Pre-label each row with a weekend flag (1/0) so the condition
-- is defined once and reused cleanly across all aggregations.
WITH WeekendFlags AS (
    SELECT
        member_casual,
        CASE WHEN DATEPART(WEEKDAY, started_at) IN (1, 7)
             THEN 1 ELSE 0 END                      AS is_weekend
    FROM dbo.Trips
)
SELECT
    -- Overall weekend/weekday split
    SUM(is_weekend)                                 AS weekend_rides,
    SUM(1 - is_weekend)                             AS weekday_rides,
    CAST(ROUND(100.0 * SUM(is_weekend)
        / COUNT(*), 1) AS DECIMAL(5,1))             AS weekend_pct,

    -- Member weekend %
    CAST(ROUND(100.0 *
        SUM(CASE WHEN member_casual = 'member' THEN is_weekend ELSE 0 END)
        / NULLIF(SUM(CASE WHEN member_casual = 'member' THEN 1 ELSE 0 END), 0)
    , 1) AS DECIMAL(5,1))                           AS member_weekend_pct,

    -- Casual weekend %
    CAST(ROUND(100.0 *
        SUM(CASE WHEN member_casual = 'casual' THEN is_weekend ELSE 0 END)
        / NULLIF(SUM(CASE WHEN member_casual = 'casual' THEN 1 ELSE 0 END), 0)
    , 1) AS DECIMAL(5,1))                           AS casual_weekend_pct,

    -- Weekend skew ratio (casual weekend % / member weekend %)
    CAST(ROUND(
        (100.0 *
            SUM(CASE WHEN member_casual = 'casual' THEN is_weekend ELSE 0 END)
            / NULLIF(SUM(CASE WHEN member_casual = 'casual' THEN 1 ELSE 0 END), 0))
        /
        NULLIF((100.0 *
            SUM(CASE WHEN member_casual = 'member' THEN is_weekend ELSE 0 END)
            / NULLIF(SUM(CASE WHEN member_casual = 'member' THEN 1 ELSE 0 END), 0)), 0)
    , 2) AS DECIMAL(5,2))                           AS weekend_skew_ratio

FROM WeekendFlags;
GO
