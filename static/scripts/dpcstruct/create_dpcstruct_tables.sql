-- =========================================================================
-- V. DPCSTRUCT TABLES CREATION
-- =========================================================================

-- 1. Core Table: DPCStruct Metacluster Properties
-- Function: Stores the biological and structural properties of protein metaclusters and their consistency with Pfam-36 labels
-- Fields:
--   - Structural metrics: plddt, disorder, tmscore, lddt (quality metrics)
--   - Length metrics: len_aa, len_std, len_ratio (protein length information)
--   - Pfam consistency: pfam_score, pfam_da

CREATE TABLE IF NOT EXISTS dpcstruct_mcs_properties (
    mc_id VARCHAR(50) PRIMARY KEY,
    mc_size INTEGER NOT NULL,
    len_aa DOUBLE PRECISION,
    len_std DOUBLE PRECISION,
    len_ratio DOUBLE PRECISION,
    plddt DOUBLE PRECISION,
    disorder DOUBLE PRECISION,
    tmscore DOUBLE PRECISION,
    lddt DOUBLE PRECISION,
    pident DOUBLE PRECISION,
    pfam_score DOUBLE PRECISION,
    pfam_da TEXT
);

-- 2. Mapping Table: Metacluster Sequences
-- Function: Links specific Proteins to Metaclusters. Stores position information (sequence ranges) for each protein in the metacluster.
-- Interconnection: Links mc_id (FK -> dpcstruct_mcs_properties) protein_id (FK -> dpc_uniprot_proteins).

CREATE TABLE IF NOT EXISTS dpcstruct_mcs_sequences (
    id BIGSERIAL PRIMARY KEY,
    mc_id VARCHAR(50) NOT NULL REFERENCES dpcstruct_mcs_properties(mc_id) ON DELETE CASCADE,
    protein_id VARCHAR(50) NOT NULL REFERENCES dpc_uniprot_proteins(protein_id) ON DELETE CASCADE,
    prot_range VARCHAR(100) NOT NULL,
    prot_seq TEXT
);

-- 3. CATH Fold Annotations for DPCStruct Metaclusters
-- Function: Stores CATH fold annotations for protein structures in DPCStruct metaclusters
-- Fields:
--   - cath_query: CATH fold identifier queried against DPC proteins
--   - mc_id: DPCStruct metacluster ID (FK to dpcstruct_mcs_properties)
--   - dpc_target: DPC protein ID matched with CATH query
--   - Coverage/quality metrics: qcov, tcov, alnlen, qtmscore, ttmscore, alntmscore, lddt, pident
--   - Coordinate ranges: q_range (query range), t_range (target range)

CREATE TABLE IF NOT EXISTS dpcstruct_cath (
    cath_query VARCHAR(50) PRIMARY KEY,
    dpc_mcid VARCHAR(50) NOT NULL REFERENCES dpcstruct_mcs_properties(mc_id) ON DELETE CASCADE,
    dpc_target VARCHAR(50) NOT NULL,
    q_range VARCHAR(100),
    t_range VARCHAR(100),
    qlen INTEGER,
    tlen INTEGER,
    qcov DOUBLE PRECISION,
    tcov DOUBLE PRECISION,
    alnlen INTEGER,
    qtmscore DOUBLE PRECISION,
    ttmscore DOUBLE PRECISION,
    alntmscore DOUBLE PRECISION,
    lddt DOUBLE PRECISION,
    pident DOUBLE PRECISION
);

-- 4. SCOP Fold Annotations for DPCStruct Metaclusters
-- Function: Stores SCOP fold annotations for protein structures in DPCStruct metaclusters
-- Fields: Similar structure to CATH table with SCOP-specific identifiers

CREATE TABLE IF NOT EXISTS dpcstruct_scop (
    scop_query VARCHAR(50) PRIMARY KEY,
    dpc_mcid VARCHAR(50) NOT NULL REFERENCES dpcstruct_mcs_properties(mc_id) ON DELETE CASCADE,
    dpc_target VARCHAR(50) NOT NULL,
    q_range VARCHAR(50),
    t_range VARCHAR(50),
    qlen INTEGER,
    tlen INTEGER,
    qcov DOUBLE PRECISION,
    tcov DOUBLE PRECISION,
    alnlen INTEGER,
    qtmscore DOUBLE PRECISION,
    ttmscore DOUBLE PRECISION,
    alntmscore DOUBLE PRECISION,
    lddt DOUBLE PRECISION,
    pident DOUBLE PRECISION
);

-- =========================================================================
-- OPTIMIZATION: INDEXES & PERFORMANCE
-- =========================================================================

-- Natural Numeric Sorting: Extracts numbers from 'MC123' for fast integer-based sorting.
-- Used to sort metaclusters numerically (MC1, MC2, MC10) instead of alphabetically.
CREATE INDEX IF NOT EXISTS idx_per_mcid_dpcstruct ON dpcstruct_mcs_properties (CAST(SUBSTRING(mc_id FROM '[0-9]+') AS INTEGER));

-- High-Speed Discovery: Indexes for frequent search queries
CREATE INDEX IF NOT EXISTS idx_dpcstruct_mcs_per_protein ON dpcstruct_mcs_sequences(protein_id);
CREATE INDEX IF NOT EXISTS idx_dpcstruct_seqs_per_mcid ON dpcstruct_mcs_sequences(mc_id);

-- CATH Indexes: Fast lookups for CATH fold analysis
CREATE INDEX IF NOT EXISTS idx_dpcstruct_cath_per_mcid ON dpcstruct_cath(dpc_mcid);
CREATE INDEX IF NOT EXISTS idx_dpcstruct_cath_per_query ON dpcstruct_cath(cath_query);
CREATE INDEX IF NOT EXISTS idx_dpcstruct_cath_per_target ON dpcstruct_cath(dpc_target);

-- SCOP Indexes: Fast lookups for SCOP fold analysis
CREATE INDEX IF NOT EXISTS idx_dpcstruct_scop_per_mcid ON dpcstruct_scop(dpc_mcid);
CREATE INDEX IF NOT EXISTS idx_dpcstruct_scop_per_query ON dpcstruct_scop(scop_query);
CREATE INDEX IF NOT EXISTS idx_dpcstruct_scop_per_target ON dpcstruct_scop(dpc_target);

-- Trigram Index: Optimizes Regex/Text searches on "Fused" Pfam strings
-- Allows the app to quickly find Metaclusters containing a specific Pfam domain.
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX IF NOT EXISTS idx_dpcstruct_mcs_per_pfam_da ON dpcstruct_mcs_properties USING gin (pfam_da gin_trgm_ops);