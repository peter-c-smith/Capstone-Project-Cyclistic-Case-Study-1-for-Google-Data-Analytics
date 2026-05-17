-- ============================================================
-- 00_connection_check.sql
-- Verifies connection and reports database object inventory.
-- Run this first to confirm the runner is working correctly.
-- ============================================================

-- Server and database info
SELECT
    @@SERVERNAME            AS server_name,
    DB_NAME()               AS database_name,
    SYSTEM_USER             AS login_name,
    @@VERSION               AS sql_server_version;

-- Tables present and their row counts
SELECT
    t.name                              AS table_name,
    p.rows                              AS row_count,
    CAST(
        SUM(a.total_pages) * 8.0 / 1024
    AS DECIMAL(10,2))                   AS size_mb
FROM sys.tables t
JOIN sys.indexes i
    ON t.object_id = i.object_id
    AND i.index_id IN (0, 1)            -- heap or clustered index
JOIN sys.partitions p
    ON i.object_id = p.object_id
    AND i.index_id = p.index_id
JOIN sys.allocation_units a
    ON p.partition_id = a.container_id
GROUP BY
    t.name,
    p.rows
ORDER BY
    t.name;
