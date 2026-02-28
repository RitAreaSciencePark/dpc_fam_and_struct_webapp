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


-- Natural Numeric Sorting: Extracts numbers from 'MC123' for fast integer-based sorting.
-- Used to sort metaclusters numerically (MC1, MC2, MC10) instead of alphabetically.
CREATE INDEX IF NOT EXISTS idx_dpcstruct_mcs_prop_num ON dpcstruct_mcs_properties (CAST(SUBSTRING(mc_id FROM '[0-9]+') AS INTEGER));

