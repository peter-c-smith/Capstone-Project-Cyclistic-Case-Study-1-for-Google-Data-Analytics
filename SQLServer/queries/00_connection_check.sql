-- ============================================================
-- 00_connection_check.sql
-- Verifies connection and reports database object inventory.
-- Run this first to confirm the runner is working correctly.
-- ============================================================

USE CyclisticCaseStudy;
GO

-- Server and database info
SELECT
    @@SERVERNAME            AS server_name,
    DB_NAME()               AS database_name,
    SYSTEM_USER             AS login_name;
GO

-- Schemas present
SELECT
    name                    AS schema_name
FROM sys.schemas
WHERE name NOT IN ('sys', 'INFORMATION_SCHEMA', 'guest',
                   'db_owner', 'db_accessadmin', 'db_securityadmin',
                   'db_ddladmin', 'db_backupoperator', 'db_datareader',
                   'db_datawriter', 'db_denydatareader', 'db_denydatawriter')
ORDER BY name;
GO

-- Tables present with schema, row count, and size
SELECT
    s.name                              AS schema_name,
    t.name                              AS table_name,
    p.rows                              AS row_count,
    CAST(
        SUM(a.total_pages) * 8.0 / 1024
    AS DECIMAL(10, 2))                  AS size_mb
FROM sys.tables t
JOIN sys.schemas s
    ON t.schema_id = s.schema_id
JOIN sys.indexes i
    ON t.object_id = i.object_id
    AND i.index_id IN (0, 1)
JOIN sys.partitions p
    ON i.object_id = p.object_id
    AND i.index_id = p.index_id
JOIN sys.allocation_units a
    ON p.partition_id = a.container_id
GROUP BY
    s.name,
    t.name,
    p.rows
ORDER BY
    s.name,
    t.name;
GO
