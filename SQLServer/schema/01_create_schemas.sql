-- ============================================================
-- 01_create_schemas.sql
-- Creates non-default schemas used in this database.
-- Safe to re-run — uses IF NOT EXISTS guard.
-- ============================================================

USE CyclisticCaseStudy;
GO

-- stg schema: holds the raw staging table populated by SSIS
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'stg')
BEGIN
    EXEC('CREATE SCHEMA stg');
    PRINT 'Schema [stg] created.';
END
ELSE
BEGIN
    PRINT 'Schema [stg] already exists — skipped.';
END
GO
