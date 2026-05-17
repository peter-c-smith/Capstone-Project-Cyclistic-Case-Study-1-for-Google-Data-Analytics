-- ============================================================
-- 11_bike_type_mix.sql
-- Cyclistic Bike-Share Case Study — Bike Type Mix
--
-- Business question: Do casual riders and members prefer
-- different bike types?
--
-- Validates against: Page 2 Ride Behavior
--   - "Rides by Bike Type" stacked or clustered chart
--     (classic_bike, electric_bike, electric_scooter)
--
-- Result note: Only classic_bike and electric_bike appear in this
-- 12-month dataset (Apr 2025 – Mar 2026). No electric_scooter rows
-- were present in the source CSVs. Bike type preference is nearly
-- identical between members and casuals (~65% electric both groups)
-- and is therefore not a meaningful behavioral differentiator.
-- ============================================================

USE CyclisticCaseStudy;
GO

-- Aggregate by bike type, then join grand totals for clean %
-- calculations. CROSS JOIN avoids nested window aggregates and
-- keeps the percentage logic readable.
WITH BikeAgg AS (
    SELECT
        rideable_type,
        COUNT(*)                                    AS total_rides,
        SUM(CASE WHEN member_casual = 'member'
                 THEN 1 ELSE 0 END)                 AS member_rides,
        SUM(CASE WHEN member_casual = 'casual'
                 THEN 1 ELSE 0 END)                 AS casual_rides
    FROM dbo.Trips
    GROUP BY rideable_type
),
GrandTotals AS (
    SELECT
        SUM(total_rides)                            AS grand_total,
        SUM(member_rides)                           AS total_member,
        SUM(casual_rides)                           AS total_casual
    FROM BikeAgg
)
SELECT
    b.rideable_type,
    b.total_rides,
    b.member_rides,
    b.casual_rides,

    -- Each bike type as % of all rides
    CAST(ROUND(100.0 * b.total_rides
        / NULLIF(g.grand_total, 0), 1) AS DECIMAL(5,1))  AS pct_of_all_rides,

    -- Each bike type as % within member rides
    CAST(ROUND(100.0 * b.member_rides
        / NULLIF(g.total_member, 0), 1) AS DECIMAL(5,1)) AS member_pct_of_type,

    -- Each bike type as % within casual rides
    CAST(ROUND(100.0 * b.casual_rides
        / NULLIF(g.total_casual, 0), 1) AS DECIMAL(5,1)) AS casual_pct_of_type

FROM BikeAgg b
CROSS JOIN GrandTotals g
ORDER BY b.total_rides DESC;
GO
