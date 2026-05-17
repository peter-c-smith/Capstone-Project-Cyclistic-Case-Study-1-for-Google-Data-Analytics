-- ============================================================
-- 05_create_error_log.sql
-- Creates the ETL error log table used by the SSIS package
-- OnError event handler to record package failures.
--
-- Safe to re-run — drops and recreates the table.
-- Note: dropping this table clears historical error records.
-- ============================================================

USE CyclisticCaseStudy;
GO

DROP TABLE IF EXISTS dbo.ETL_ErrorLog;
GO

CREATE TABLE dbo.ETL_ErrorLog
(
    error_id        INT             NOT NULL    IDENTITY(1,1),
    log_time        DATETIME2       NOT NULL    DEFAULT SYSUTCDATETIME(),
    package_name    NVARCHAR(255)   NULL,
    task_name       NVARCHAR(255)   NULL,
    error_code      INT             NULL,
    error_message   NVARCHAR(4000)  NULL,
    source_file     NVARCHAR(255)   NULL,

    CONSTRAINT PK_ETL_ErrorLog PRIMARY KEY CLUSTERED (error_id)
);
GO

PRINT 'Table [dbo].[ETL_ErrorLog] created.';
GO
