-- =========================================================================
-- DPCStruct Tables
-- =========================================================================

-- 1. Core Table: DPCStruct Metacluster Properties
-- Function: Stores the biological and structural properties of protein metaclusters and their consistency with Pfam-36 labels:

CREATE TABLE IF NOT EXISTS dpcstruct_mcs_properties (
    mc_id VARCHAR(50) PRIMARY KEY,
    mc_size INTEGER,
    len_aa DOUBLE PRECISION,
    len_std DOUBLE PRECISION,
    len_ratio DOUBLE PRECISION,
    plddt DOUBLE PRECISION,
    disorder DOUBLE PRECISION,
    tmscore DOUBLE PRECISION,
    lddt DOUBLE PRECISION,
    pident DOUBLE PRECISION,
    pfam_score DOUBLE PRECISION,
    pfam_labels TEXT
);

-- 2. Mapping Table: Metacluster Sequences
-- Function: Links specific Proteins to Metaclusters and stores coordinates.
-- Interconnection: Links mc_id (FK -> mcs_properties).
CREATE TABLE IF NOT EXISTS dpcstruct_mcs_sequences (
    id BIGSERIAL PRIMARY KEY,
    mc_id VARCHAR(50) NOT NULL REFERENCES dpcstruct_mcs_properties(mc_id) ON DELETE CASCADE,
    protein_id VARCHAR(50) NOT NULL,
    prot_range VARCHAR(100) NOT NULL,
    prot_seq TEXT
);

-- Natural Numeric Sorting: Extracts numbers from 'MC123' for fast integer-based sorting.
-- Used to sort metaclusters numerically (MC1, MC2, MC10) instead of alphabetically.
CREATE INDEX IF NOT EXISTS idx_dpcstruct_mcs_prop_num ON dpcstruct_mcs_properties (CAST(SUBSTRING(mc_id FROM '[0-9]+') AS INTEGER));
CREATE INDEX IF NOT EXISTS idx_dpcstruct_mcs_seq_protein ON dpcstruct_mcs_sequences(protein_id);
CREATE INDEX IF NOT EXISTS idx_dpcstruct_mcs_seq_mcid ON dpcstruct_mcs_sequences(mc_id);

