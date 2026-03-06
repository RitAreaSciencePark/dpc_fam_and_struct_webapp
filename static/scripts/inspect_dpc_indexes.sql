--Check the exact SQL definition of idx_dpcstruct_mcs_prop_num
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'dpcstruct_mcs_properties';
--Check whether the index is being used in queries
EXPLAIN ANALYZE
SELECT *
FROM dpcstruct_mcs_properties
ORDER BY CAST(SUBSTRING(mc_id FROM '[0-9]+') AS INTEGER);
--LIMIT 50;
-- Without indexes :
SET enable_indexscan = off;
SET enable_bitmapscan = off;
EXPLAIN ANALYZE
SELECT *
FROM dpcstruct_mcs_properties
ORDER BY CAST(SUBSTRING(mc_id FROM '[0-9]+') AS INTEGER);
SET enable_indexscan = on;
SET enable_bitmapscan = on;