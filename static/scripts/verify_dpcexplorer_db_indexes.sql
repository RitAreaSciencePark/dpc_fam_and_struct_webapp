-- =============================================================================
-- DPCexplorer — Index Performance Verification Suite
-- =============================================================================
-- Purpose   : Verify that every index declared in
--             dpcexplorer schema is present, structurally correct, and
--             actively chosen by the PostgreSQL query planner.
--
-- Usage     : psql -U $DB_USER -d $DB_NAME -f static/scripts/verify_dpcexplorer_indexes.sql
--
-- Structure :
--   Section 1  — Index inventory           (all indexes exist with correct type)
--   Section 2  — Index size & bloat        (indexes are populated, not empty)
--   Section 3  — GIN trigram proof         (Bitmap Index Scan on pfam_da)
--   Section 4  — Functional sort proof     (Index Scan on natural MCID sort)
--   Section 5  — B-Tree FK join proof      (Index Scan on foreign key lookups)
--   Section 6  — Live usage counters       (pg_stat_user_indexes hit counts)
--   Section 7  — Sequential scan audit     (no unexpected Seq Scans on indexed cols)
-- =============================================================================

\timing on
\pset footer off

-- =============================================================================
-- SECTION 1 — INDEX INVENTORY
-- Expected: every index from dpcexplorer schema appears with the correct
-- access method (btree or gin) and on the correct table.
-- =============================================================================

\echo ''
\echo '============================================================'
\echo 'SECTION 1  —  INDEX INVENTORY'
\echo 'Every index created by dpcexplorer schema must appear here.'
\echo '============================================================'

SELECT
    t.relname                           AS table_name,
    i.relname                           AS index_name,
    am.amname                           AS index_type,
    array_to_string(
        array_agg(a.attname ORDER BY x.n), ', '
    )                                   AS indexed_columns,
    ix.indisunique                      AS is_unique,
    ix.indisprimary                     AS is_primary
FROM
    pg_class         t
    JOIN pg_index    ix ON t.oid = ix.indrelid
    JOIN pg_class    i  ON i.oid = ix.indexrelid
    JOIN pg_am       am ON i.relam = am.oid
    JOIN pg_namespace ns ON t.relnamespace = ns.oid
    -- unnest the key attribute array to get column names
    JOIN LATERAL unnest(ix.indkey) WITH ORDINALITY AS x(attnum, n)
         ON true
    LEFT JOIN pg_attribute a
         ON a.attrelid = t.oid AND a.attnum = x.attnum
WHERE
    ns.nspname = 'public'
    AND t.relname IN (
        'dpc_uniprot_proteins',
        'dpc_pfam_domains',
        'dpc_uniref50_pfam',
        'dpcfam_mcs_properties',
        'dpcfam_mcs_sequences',
        'dpcfam_alphafold_reps',
        'dpcstruct_mcs_properties',
        'dpcstruct_mcs_sequences',
        'dpcstruct_cath',
        'dpcstruct_scop'
    )
GROUP BY
    t.relname, i.relname, am.amname, ix.indisunique, ix.indisprimary
ORDER BY
    t.relname, is_primary DESC, index_name;


-- =============================================================================
-- SECTION 2 — INDEX SIZE & POPULATION
-- A zero-size index would mean the index exists but was never built over data.
-- All indexes must report a non-zero pg_size_pretty value.
-- =============================================================================

\echo ''
\echo '============================================================'
\echo 'SECTION 2  —  INDEX SIZE & POPULATION'
\echo 'Confirms each index is built over real data (non-zero size).'
\echo '============================================================'

SELECT
    t.relname                           AS table_name,
    i.relname                           AS index_name,
    pg_size_pretty(pg_relation_size(i.oid))  AS index_size,
    pg_size_pretty(pg_total_relation_size(t.oid)) AS table_total_size
FROM
    pg_class      t
    JOIN pg_index ix ON t.oid = ix.indrelid
    JOIN pg_class  i ON i.oid = ix.indexrelid
    JOIN pg_namespace ns ON t.relnamespace = ns.oid
WHERE
    ns.nspname = 'public'
    AND t.relname IN (
        'dpc_uniprot_proteins',
        'dpc_pfam_domains',
        'dpc_uniref50_pfam',
        'dpcfam_mcs_properties',
        'dpcfam_mcs_sequences',
        'dpcfam_alphafold_reps',
        'dpcstruct_mcs_properties',
        'dpcstruct_mcs_sequences',
        'dpcstruct_cath',
        'dpcstruct_scop'
    )
ORDER BY
    t.relname, pg_relation_size(i.oid) DESC;


-- =============================================================================
-- SECTION 3 — GIN TRIGRAM INDEX PROOF
-- Query: find all DPCfam metaclusters whose pfam_da contains 'PF02990'.
--
-- What we must see in the EXPLAIN output:
--   "Bitmap Index Scan on idx_dpcfam_mcs_per_pfam_da"
--
-- If it shows "Seq Scan" instead, the GIN index is not being used.
-- The same proof is then repeated for DPCstruct.
-- =============================================================================

\echo ''
\echo '============================================================'
\echo 'SECTION 3a  —  GIN TRIGRAM PROOF  (dpcfam_mcs_properties)'
\echo 'Emmanuel checkpoint: plan must contain'
\echo '  "Bitmap Index Scan on idx_dpcfam_mcs_per_pfam_da"'
\echo '============================================================'

EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT mcid, pfam_da
FROM   dpcfam_mcs_properties
WHERE  pfam_da ILIKE '%PF02990%';


\echo ''
\echo '============================================================'
\echo 'SECTION 3b  —  GIN TRIGRAM PROOF  (dpcstruct_mcs_properties)'
\echo 'Emmanuel checkpoint: plan must contain'
\echo '  "Bitmap Index Scan on idx_dpcstruct_mcs_per_pfam"'
\echo '============================================================'

EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT mc_id, pfam_da
FROM   dpcstruct_mcs_properties
WHERE  pfam_da ILIKE '%PF02990%';


\echo ''
\echo '============================================================'
\echo 'SECTION 3c  —  GIN TRIGRAM PROOF WITH REGEX'
\echo 'The application uses a regex for exact token matching.'
\echo 'The GIN index still assists as a trigram pre-filter.'
\echo 'Emmanuel checkpoint: plan must NOT show a pure Seq Scan.'
\echo '============================================================'

EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT mcid, pfam_da
FROM   dpcfam_mcs_properties
WHERE  pfam_da ~ '(^|-)PF02990(-|$)';


-- =============================================================================
-- SECTION 4 — FUNCTIONAL INDEX PROOF (natural MCID sort)
-- The functional index pre-computes CAST(SUBSTRING(mcid FROM '[0-9]+') AS INTEGER).
-- Django's get_queryset() annotates with the same expression and sorts by it.
--
-- What we must see:
--   "Index Scan using idx_per_mcid_dpcfam on dpcfam_mcs_properties"
--   OR
--   "Index Only Scan using idx_per_mcid_dpcfam"
--
-- Without the functional index this would be a sequential scan + sort in memory.
-- =============================================================================

\echo ''
\echo '============================================================'
\echo 'SECTION 4a  —  FUNCTIONAL SORT INDEX PROOF  (DPCfam)'
\echo 'Emmanuel checkpoint: plan must use idx_per_mcid_dpcfam'
\echo '  — not a Sort node over a Seq Scan.'
\echo '============================================================'

EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT mcid
FROM   dpcfam_mcs_properties
ORDER BY CAST(SUBSTRING(mcid FROM '[0-9]+') AS INTEGER)
LIMIT  20;


\echo ''
\echo '============================================================'
\echo 'SECTION 4b  —  FUNCTIONAL SORT INDEX PROOF  (DPCstruct)'
\echo 'Emmanuel checkpoint: plan must use idx_per_mcid_dpcstruct.'
\echo '============================================================'

EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT mc_id
FROM   dpcstruct_mcs_properties
ORDER BY CAST(SUBSTRING(mc_id FROM '[0-9]+') AS INTEGER)
LIMIT  20;


-- =============================================================================
-- SECTION 5 — B-TREE FOREIGN KEY JOIN PROOF
-- These queries mimic the real ORM calls that fire when a user opens a page.
--
-- 5a: protein_detail view — fetch all DPCfam metaclusters for one protein
--     Uses idx_dpcfam_mcs_per_protein on dpcfam_mcs_sequences(protein_id)
--
-- 5b: protein_detail view — fetch all DPCstruct metaclusters for one protein
--     Uses idx_dpcstruct_mcs_per_prot on dpcstruct_mcs_sequences(protein_id)
--
-- 5c: protein_detail view — fetch all Pfam domains for one protein
--     Uses idx_dpc_pfams_per_protein on dpc_uniref50_pfam(uniref50_id)
--
-- 5d: DPCfam detail view — paginate sequences for one metacluster
--     Uses idx_dpcfam_seqs_per_mcid on dpcfam_mcs_sequences(mcid)
--
-- 5e: DPCstruct detail view — paginate sequences for one metacluster
--     Uses idx_dpcstruct_seqs_per_mc on dpcstruct_mcs_sequences(mc_id)
--
-- 5f: DPCstruct detail view — fetch CATH annotations for one metacluster
--     Uses idx_dpcstruct_cath_per_mc on dpcstruct_cath(dpc_mcid)
--
-- 5g: DPCstruct detail view — fetch SCOP annotations for one metacluster
--     Uses idx_dpcstruct_scop_per_mc on dpcstruct_scop(dpc_mcid)
--
-- 5h: AlphaFold reps for one DPCfam metacluster
--     Uses idx_dpcfam_reps_per_mcid on dpcfam_alphafold_reps(mcid)
--
-- What we must see for every query:
--   "Index Scan" or "Index Only Scan" — never "Seq Scan" on the filtered column.
-- =============================================================================

\echo ''
\echo '============================================================'
\echo 'SECTION 5a  —  B-TREE FK PROOF'
\echo 'protein_detail: DPCfam metaclusters for one protein'
\echo 'Expected index: idx_dpcfam_mcs_per_protein'
\echo '============================================================'

EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT seq.protein_id, seq.mcid, seq.seq_range, prop.pfam_da
FROM   dpcfam_mcs_sequences   seq
JOIN   dpcfam_mcs_properties  prop ON seq.mcid = prop.mcid
WHERE  seq.protein_id = 'A0A182N2I3';


\echo ''
\echo '============================================================'
\echo 'SECTION 5b  —  B-TREE FK PROOF'
\echo 'protein_detail: DPCstruct metaclusters for one protein'
\echo 'Expected index: idx_dpcstruct_mcs_per_prot'
\echo '============================================================'

EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT seq.protein_id, seq.mc_id, seq.prot_range, prop.pfam_da
FROM   dpcstruct_mcs_sequences   seq
JOIN   dpcstruct_mcs_properties  prop ON seq.mc_id = prop.mc_id
WHERE  seq.protein_id = 'A0A182N2I3';


\echo ''
\echo '============================================================'
\echo 'SECTION 5c  —  B-TREE FK PROOF'
\echo 'protein_detail: Pfam domains for one protein'
\echo 'Expected index: idx_dpc_pfams_per_protein'
\echo '============================================================'

EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT u.uniref50_id, u.pfam_ids, u.pfam_ranges
FROM   dpc_uniref50_pfam u
WHERE  u.uniref50_id = 'A0A182N2I3';


\echo ''
\echo '============================================================'
\echo 'SECTION 5d  —  B-TREE FK PROOF'
\echo 'DPCfam detail: paginate sequences for one metacluster'
\echo 'Expected index: idx_dpcfam_seqs_per_mcid'
\echo '============================================================'

EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT id, protein_id, seq_range, seq_length
FROM   dpcfam_mcs_sequences
WHERE  mcid = 'MC1'
ORDER BY id
LIMIT  20;


\echo ''
\echo '============================================================'
\echo 'SECTION 5e  —  B-TREE FK PROOF'
\echo 'DPCstruct detail: paginate sequences for one metacluster'
\echo 'Expected index: idx_dpcstruct_seqs_per_mc'
\echo '============================================================'

EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT id, protein_id, prot_range
FROM   dpcstruct_mcs_sequences
WHERE  mc_id = 'MC1'
ORDER BY id
LIMIT  20;


\echo ''
\echo '============================================================'
\echo 'SECTION 5f  —  B-TREE FK PROOF'
\echo 'DPCstruct detail: CATH annotations for one metacluster'
\echo 'Expected index: idx_dpcstruct_cath_per_mc'
\echo '============================================================'

EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT cath_query, dpc_target, qtmscore, lddt
FROM   dpcstruct_cath
WHERE  dpc_mcid = 'MC1';


\echo ''
\echo '============================================================'
\echo 'SECTION 5g  —  B-TREE FK PROOF'
\echo 'DPCstruct detail: SCOP annotations for one metacluster'
\echo 'Expected index: idx_dpcstruct_scop_per_mc'
\echo '============================================================'

EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT scop_query, dpc_target, qtmscore, lddt
FROM   dpcstruct_scop
WHERE  dpc_mcid = 'MC1';


\echo ''
\echo '============================================================'
\echo 'SECTION 5h  —  B-TREE FK PROOF'
\echo 'DPCfam detail: AlphaFold reps for one metacluster'
\echo 'Expected index: idx_dpcfam_reps_per_mcid'
\echo '============================================================'

EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT alphafold_prot, seq_range, hmm_coverage, avg_plddt
FROM   dpcfam_alphafold_reps
WHERE  mcid = 'MC1';


-- =============================================================================
-- SECTION 6 — LIVE USAGE COUNTERS
-- pg_stat_user_indexes records how many times each index has been chosen by
-- the query planner since the last pg_stat_reset() call.
-- A non-zero idx_scan proves that real application traffic is using the index.
--
-- Note: counters reset to zero after a server restart or manual pg_stat_reset().
-- Run this section after the application has served real user queries to see
-- non-trivial values. The queries in sections 3–5 above will themselves
-- increment the counters for their respective indexes.
-- =============================================================================

\echo ''
\echo '============================================================'
\echo 'SECTION 6  —  LIVE USAGE COUNTERS'
\echo '(idx_scan counts every index hit since last stats reset.'
\echo ' Run the app, then re-run this section to see growth.)'
\echo '============================================================'

SELECT
    relname                     AS table_name,
    indexrelname                AS index_name,
    idx_scan                    AS times_used_by_planner,
    idx_tup_read                AS index_entries_read,
    idx_tup_fetch               AS heap_rows_fetched
FROM
    pg_stat_user_indexes
WHERE
    schemaname = 'public'
    AND relname IN (
        'dpc_uniprot_proteins',
        'dpc_pfam_domains',
        'dpc_uniref50_pfam',
        'dpcfam_mcs_properties',
        'dpcfam_mcs_sequences',
        'dpcfam_alphafold_reps',
        'dpcstruct_mcs_properties',
        'dpcstruct_mcs_sequences',
        'dpcstruct_cath',
        'dpcstruct_scop'
    )
ORDER BY
    idx_scan DESC, relname, index_name;


-- =============================================================================
-- SECTION 7 — SEQUENTIAL SCAN AUDIT
-- pg_stat_user_tables records seq_scan (sequential scans) and idx_scan
-- (index scans) per table. For large tables, seq_scan should be very low
-- compared to idx_scan. A high seq_scan ratio on dpcfam_mcs_sequences or
-- dpcstruct_mcs_sequences would indicate that some queries bypass the indexes.
-- =============================================================================

\echo ''
\echo '============================================================'
\echo 'SECTION 7  —  SEQUENTIAL SCAN AUDIT'
\echo 'For large tables, seq_scan should be much lower than idx_scan.'
\echo 'A high seq_scan count on a large table signals a missing index.'
\echo '============================================================'

SELECT
    relname                     AS table_name,
    n_live_tup                  AS live_rows,
    seq_scan                    AS sequential_scans,
    idx_scan                    AS index_scans,
    CASE
        WHEN (seq_scan + idx_scan) = 0 THEN 'no traffic yet'
        WHEN seq_scan = 0              THEN '100% indexed  ✓'
        ELSE round(
            100.0 * idx_scan / (seq_scan + idx_scan), 1
        )::text || '% indexed'
    END                         AS index_usage_rate,
    n_dead_tup                  AS dead_rows_pending_vacuum
FROM
    pg_stat_user_tables
WHERE
    schemaname = 'public'
    AND relname IN (
        'dpc_uniprot_proteins',
        'dpc_pfam_domains',
        'dpc_uniref50_pfam',
        'dpcfam_mcs_properties',
        'dpcfam_mcs_sequences',
        'dpcfam_alphafold_reps',
        'dpcstruct_mcs_properties',
        'dpcstruct_mcs_sequences',
        'dpcstruct_cath',
        'dpcstruct_scop'
    )
ORDER BY
    live_rows DESC;


\echo ''
\echo '============================================================'
\echo 'VERIFICATION COMPLETE'
\echo ''
\echo 'Quick review checklist:'
\echo '  Section 1  — all 20+ index names must appear'
\echo '  Section 2  — all index sizes must be > 0'
\echo '  Section 3  — plan must show Bitmap Index Scan (not Seq Scan)'
\echo '  Section 4  — plan must use functional index (not Sort+Seq Scan)'
\echo '  Section 5  — all 8 plans must show Index Scan (not Seq Scan)'
\echo '  Section 6  — idx_scan counters grow with application usage'
\echo '  Section 7  — index_usage_rate should be near 100% on large tables'
\echo '============================================================'

\timing off
