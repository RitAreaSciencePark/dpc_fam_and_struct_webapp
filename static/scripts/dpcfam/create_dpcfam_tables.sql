-- =========================================================================
-- III. DPCFAM TABLES CREATION
-- =========================================================================

-- 1. Core Table: DPCFam Metacluster Properties
-- Function: Stores biological and structural properties of protein metaclusters from DPCFam database
-- Fields:
--   - Cluster metrics: size_uniref50 (cluster size)
--   - Length metrics: avg_len, std_avg_len (average and standard deviation of protein lengths)
--   - Region composition: lc_percent, cc_percent, dis_percent (low complexity, coiled-coil, disordered percentages)
--   - Structural: tm (transmembrane score)
--   - Pfam metrics: pfam_labels (dash-separated Pfam domain IDs), da_percent (percentage with domain annotations)
--   - Overlap metrics: avg_ov_percent (average overlap), overlap_label (overlap classification)

CREATE TABLE IF NOT EXISTS dpcfam_mcs_properties (
    mcid VARCHAR(50) PRIMARY KEY,
    size_uniref50 INTEGER NOT NULL,
    avg_len DOUBLE PRECISION,
    std_avg_len DOUBLE PRECISION,
    lc_percent DOUBLE PRECISION,
    cc_percent DOUBLE PRECISION,
    dis_percent DOUBLE PRECISION,
    tm DOUBLE PRECISION,
    pfam_da TEXT,
    da_percent DOUBLE PRECISION,
    avg_ov_percent DOUBLE PRECISION,
    overlap_label VARCHAR(50)
);

-- 2. Mapping Table: DPCFam Metacluster Sequences
-- Function: Links specific UniRef50 proteins to Metaclusters with position information (sequence ranges).
-- Interconnection: Links protein_id (FK -> dpc_uniprot_proteins) and mcid (FK -> dpcfam_mcs_properties).

CREATE TABLE IF NOT EXISTS dpcfam_mcs_sequences (
    id BIGSERIAL PRIMARY KEY,
    mcid VARCHAR(50) NOT NULL REFERENCES dpcfam_mcs_properties(mcid) ON DELETE CASCADE,
    protein_id VARCHAR(50) NOT NULL REFERENCES dpc_uniprot_proteins(protein_id) ON DELETE CASCADE,
    seq_range VARCHAR(100) NOT NULL,
    seq_length INTEGER NOT NULL,
    aa_seq TEXT NOT NULL
);

-- 3. Structural Table: DPCFam AlphaFold Representatives
-- Function: Stores AlphaFold representative structures for each metacluster
-- Interconnection: Links back to dpcfam_mcs_properties(mcid)

CREATE TABLE IF NOT EXISTS dpcfam_alphafold_reps (
    id BIGSERIAL PRIMARY KEY,
    mcid VARCHAR(50) NOT NULL REFERENCES dpcfam_mcs_properties(mcid) ON DELETE CASCADE,
    alphafold_prot TEXT NOT NULL,
    seq_range VARCHAR(100) NOT NULL,
    hmm_coverage DOUBLE PRECISION NOT NULL,
    avg_plddt DOUBLE PRECISION NOT NULL
);

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
