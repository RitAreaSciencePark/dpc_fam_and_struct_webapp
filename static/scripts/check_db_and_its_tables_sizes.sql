-- 1. Total size of the current database : dpcfam_mcs_db
SELECT 
    current_database() AS database,
    pg_size_pretty(pg_database_size(current_database())) AS total_size;

-- 2. Size of each table (including indexes)
SELECT
    schemaname,
    relname AS table_name,
    pg_size_pretty(pg_total_relation_size(relid)) AS total_size,
    pg_size_pretty(pg_relation_size(relid)) AS table_size,
    pg_size_pretty(pg_total_relation_size(relid) - pg_relation_size(relid)) AS index_size
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC;
