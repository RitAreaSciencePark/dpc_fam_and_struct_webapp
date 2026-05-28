-- =========================================================================
-- IV. DPCFAM DATA POPULATION (\copy commands) + INDEX CREATION
-- =========================================================================
BEGIN;

SET CONSTRAINTS ALL DEFERRED;

\copy dpcfam_mcs_properties FROM 'static/dataframes/dpcfam/dpcfam_all_mcs_props.csv' WITH (FORMAT csv, HEADER true);
\copy dpcfam_mcs_sequences(mcid, protein_id, seq_range, seq_length, aa_seq) FROM 'static/dataframes/dpcfam/dpcfam_all_mcs_sequences.csv' WITH (FORMAT csv, HEADER true);
\copy dpcfam_alphafold_reps(mcid, alphafold_prot, seq_range, hmm_coverage, avg_plddt) FROM 'static/dataframes/dpcfam/alphafold_dpcfam_reps.csv' WITH (FORMAT csv, HEADER true);

SET CONSTRAINTS ALL IMMEDIATE;

-- =========================================================================
-- OPTIMIZATION: INDEXES & PERFORMANCE
-- =========================================================================

-- Natural Numeric Sorting: Extracts numbers from 'MC123' for fast integer-based sorting.
-- Used to sort metaclusters numerically (MC1, MC2, MC10) instead of alphabetically.
CREATE INDEX IF NOT EXISTS idx_per_mcid_dpcfam ON dpcfam_mcs_properties (CAST(SUBSTRING(mcid FROM '[0-9]+') AS INTEGER));

-- High-Speed Discovery: Indexes for frequent search queries
CREATE INDEX IF NOT EXISTS idx_dpcfam_mcs_per_protein ON dpcfam_mcs_sequences(protein_id);
CREATE INDEX IF NOT EXISTS idx_dpcfam_seqs_per_mcid ON dpcfam_mcs_sequences(mcid);

-- AlphaFold Representatives: Filter by metacluster
CREATE INDEX IF NOT EXISTS idx_dpcfam_reps_per_mcid ON dpcfam_alphafold_reps(mcid);

-- Trigram Index: Optimizes Regex/Text searches on "Fused" Pfam strings
-- Allows the app to quickly find Metaclusters containing a specific Pfam domain.
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX IF NOT EXISTS idx_dpcfam_mcs_per_pfam_da ON dpcfam_mcs_properties USING gin (pfam_da gin_trgm_ops);

-- Refresh optimizer row statistics 
ANALYZE dpcfam_mcs_properties;
ANALYZE dpcfam_mcs_sequences;
ANALYZE dpcfam_alphafold_reps;

COMMIT;
