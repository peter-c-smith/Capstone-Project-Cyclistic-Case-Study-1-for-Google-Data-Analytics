-- ============================================================
-- 08_round_trips.sql
-- Cyclistic Bike-Share Case Study — Round Trip Analysis
--
-- Business question: Do casual riders return to their starting
-- station more often than members, indicating recreational use?
--
-- Validates against: Page 1 Executive Summary
--   - Round Trip Ratio Casual to Member card (1.63)
-- And: Page 2 Ride Behavior
--   - Round Trip % bars in the clustered column chart
--     (~11% member, ~18% casual)
--
-- Note: A round trip is defined as a ride where
-- ISNULL(start_station_name,'') = ISNULL(end_station_name,'').
-- This matches Power BI DAX behavior where BLANK() = BLANK()
-- evaluates to TRUE — rides where both stations are missing
-- (e.g., e-bikes locked at arbitrary racks) count as returning
-- to the same "non-station location." Definition confirmed via
-- 08b_round_trips_diag.sql (SQL result: 11.1% member / 18.1%
-- casual / ratio 1.63 — exact match to Power BI).
-- ============================================================

USE CyclisticCaseStudy;
GO

-- Pre-label each row with a round trip flag (1/0) so the
-- ISNULL comparison is defined once and reused cleanly.
WITH RoundTripFlags AS (
    SELECT
        member_casual,
        CASE WHEN ISNULL(start_station_name, '') = ISNULL(end_station_name, '')
             THEN 1 ELSE 0 END                      AS is_round_trip
    FROM dbo.Trips
)
SELECT
    -- Total round trips
    SUM(is_round_trip)                              AS round_trips,

    -- Member round trips and %
    SUM(CASE WHEN member_casual = 'member'
             THEN is_round_trip ELSE 0 END)         AS member_round_trips,

    CAST(ROUND(100.0 *
        SUM(CASE WHEN member_casual = 'member' THEN is_round_trip ELSE 0 END)
        / NULLIF(SUM(CASE WHEN member_casual = 'member' THEN 1 ELSE 0 END), 0)
    , 1) AS DECIMAL(5,1))                           AS member_round_trip_pct,

    -- Casual round trips and %
    SUM(CASE WHEN member_casual = 'casual'
             THEN is_round_trip ELSE 0 END)         AS casual_round_trips,

    CAST(ROUND(100.0 *
        SUM(CASE WHEN member_casual = 'casual' THEN is_round_trip ELSE 0 END)
        / NULLIF(SUM(CASE WHEN member_casual = 'casual' THEN 1 ELSE 0 END), 0)
    , 1) AS DECIMAL(5,1))                           AS casual_round_trip_pct,

    -- Round trip ratio (casual vs member)
    CAST(ROUND(
        (100.0 *
            SUM(CASE WHEN member_casual = 'casual' THEN is_round_trip ELSE 0 END)
            / NULLIF(SUM(CASE WHEN member_casual = 'casual' THEN 1 ELSE 0 END), 0))
        /
        NULLIF((100.0 *
            SUM(CASE WHEN member_casual = 'member' THEN is_round_trip ELSE 0 END)
            / NULLIF(SUM(CASE WHEN member_casual = 'member' THEN 1 ELSE 0 END), 0)), 0)
    , 2) AS DECIMAL(5,2))                           AS round_trip_ratio_casual_to_member

FROM RoundTripFlags;
GO
