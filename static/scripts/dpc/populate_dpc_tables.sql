-- =========================================================================
-- II. DPC DATA POPULATION (\copy commands) + INDEX CREATION
-- =========================================================================
BEGIN;

-- Defer foreign key checking until the end of the data ingestion
SET CONSTRAINTS ALL DEFERRED;

\copy dpc_uniprot_proteins FROM 'static/dataframes/dpc/dpc_protein_lengths.csv' WITH (FORMAT csv, HEADER true);
\copy dpc_pfam_domains FROM 'static/dataframes/dpc/dpc_pfam_ids.csv' WITH (FORMAT csv, HEADER true);
\copy dpc_uniref50_pfam(uniref50_id, pfam_ids, pfam_ranges) FROM 'static/dataframes/dpc/uniref50_pfam_valid.csv' WITH (FORMAT csv, HEADER true);

-- Evaluate foreign keys immediately upon load success
SET CONSTRAINTS ALL IMMEDIATE;

-- =========================================================================
-- OPTIMIZATION: INDEXES & PERFORMANCE
-- =========================================================================

-- Fast lookup of Pfam domains per protein
CREATE INDEX IF NOT EXISTS idx_dpc_pfams_per_protein ON dpc_uniref50_pfam(uniref50_id);
CREATE INDEX IF NOT EXISTS idx_dpc_ranges_per_pfamid ON dpc_uniref50_pfam(pfam_ids);

-- Recompute engine optimization metrics
ANALYZE dpc_uniprot_proteins;
ANALYZE dpc_pfam_domains;
ANALYZE dpc_uniref50_pfam;

COMMIT;
