-- ============================================================
-- 04_create_indexes.sql
-- Creates non-clustered indexes on dbo.Trips.
--
-- The clustered index (on trip_id) and unique index (on ride_id)
-- are created as part of 03_create_trips.sql via the PK and UQ
-- constraints. This script adds non-clustered indexes on the
-- columns most commonly used as analytical query filters.
--
-- Safe to re-run — drops each index if it exists before creating.
-- ============================================================

USE CyclisticCaseStudy;
GO

-- member_casual: used in virtually every segmented query
DROP INDEX IF EXISTS IX_Trips_member_casual ON dbo.Trips;
GO
CREATE INDEX IX_Trips_member_casual
    ON dbo.Trips (member_casual);
GO

-- started_at: date range filtering and time intelligence queries
DROP INDEX IF EXISTS IX_Trips_started_at ON dbo.Trips;
GO
CREATE INDEX IX_Trips_started_at
    ON dbo.Trips (started_at);
GO

-- rideable_type: bike type segmentation queries
DROP INDEX IF EXISTS IX_Trips_rideable_type ON dbo.Trips;
GO
CREATE INDEX IX_Trips_rideable_type
    ON dbo.Trips (rideable_type);
GO

-- start_station_name: top station queries and round trip detection
DROP INDEX IF EXISTS IX_Trips_start_station_name ON dbo.Trips;
GO
CREATE INDEX IX_Trips_start_station_name
    ON dbo.Trips (start_station_name);
GO

PRINT 'Indexes on [dbo].[Trips] created.';
GO
