-- =========================================================================
-- VI. DPCSTRUCT DATA POPULATION (\copy commands) + INDEX CREATION
-- =========================================================================
BEGIN;

SET CONSTRAINTS ALL DEFERRED;

\copy dpcstruct_mcs_properties FROM 'static/dataframes/dpcstruct/dpcstruct_mcs_properties.csv' WITH (FORMAT csv, HEADER true);
\copy dpcstruct_mcs_sequences (mc_id, protein_id, prot_range, prot_seq) FROM 'static/dataframes/dpcstruct/dpcstruct_mcs_sequences.csv' WITH (FORMAT csv, HEADER true);
\copy dpcstruct_cath FROM 'static/dataframes/dpcstruct/cleaned_annotated_cath_qc0.8_t0.5_l0.5.csv' WITH (FORMAT csv, HEADER true);
\copy dpcstruct_scop FROM 'static/dataframes/dpcstruct/cleaned_annotated_scop_qc0.8_t0.5_l0.5.csv' WITH (FORMAT csv, HEADER true);

SET CONSTRAINTS ALL IMMEDIATE;

-- =========================================================================
-- OPTIMIZATION: INDEXES & PERFORMANCE
-- =========================================================================

-- Natural Numeric Sorting: Extracts numbers from 'MC123' for fast integer-based sorting.
-- Used to sort metaclusters numerically (MC1, MC2, MC10) instead of alphabetically.
CREATE INDEX IF NOT EXISTS idx_per_mcid_dpcstruct ON dpcstruct_mcs_properties (CAST(SUBSTRING(mc_id FROM '[0-9]+') AS INTEGER));

-- High-Speed Discovery: Indexes for frequent search queries
CREATE INDEX IF NOT EXISTS idx_dpcstruct_mcs_per_prot ON dpcstruct_mcs_sequences(protein_id);
CREATE INDEX IF NOT EXISTS idx_dpcstruct_seqs_per_mc ON dpcstruct_mcs_sequences(mc_id);

-- CATH & SCOP Indexes: Fast lookups for CATH and SCOP fold analysis
CREATE INDEX IF NOT EXISTS idx_dpcstruct_cath_per_mc ON dpcstruct_cath(dpc_mcid);
CREATE INDEX IF NOT EXISTS idx_dpcstruct_scop_per_mc ON dpcstruct_scop(dpc_mcid);

-- Trigram Index: Optimizes Regex/Text searches on "Fused" Pfam strings
-- Allows the app to quickly find Metaclusters containing a specific Pfam domain.
CREATE INDEX IF NOT EXISTS idx_dpcstruct_mcs_per_pfam ON dpcstruct_mcs_properties USING gin (pfam_da gin_trgm_ops);

-- Refresh optimizer row statistics
ANALYZE dpcstruct_mcs_properties;
ANALYZE dpcstruct_mcs_sequences;
ANALYZE dpcstruct_cath;
ANALYZE dpcstruct_scop;

COMMIT;