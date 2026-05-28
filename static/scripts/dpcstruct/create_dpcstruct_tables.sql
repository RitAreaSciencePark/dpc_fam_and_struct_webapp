-- =========================================================================
-- V. DPCSTRUCT TABLES CREATION
-- =========================================================================
BEGIN;

-- 1. Core Table: DPCstruct Metacluster Properties
-- Function: Stores the biological and structural properties of DPCstruct metaclusters and their consistency with Pfam-36 labels
-- Fields:
--   - Structural metrics: plddt, disorder, tmscore, lddt (quality metrics)
--   - Length metrics: len_aa, len_std, len_ratio (domain length information)
--   - Pfam consistency: pfam_score, pfam_da(Pfam Labels: Max 5 per metacluster)
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

-- 2. Mapping Table: DPCstruct Metacluster Sequences
-- Function: Links specific Proteins to Metaclusters. Stores position information (sequence ranges) for each protein in the metacluster.
-- Interconnection: Links mc_id (FK -> dpcstruct_mcs_properties) protein_id (FK -> dpc_uniprot_proteins).

CREATE TABLE IF NOT EXISTS dpcstruct_mcs_sequences (
    id BIGSERIAL PRIMARY KEY,
    mc_id VARCHAR(50) NOT NULL REFERENCES dpcstruct_mcs_properties(mc_id) ON DELETE CASCADE,
    protein_id VARCHAR(50) NOT NULL REFERENCES dpc_uniprot_proteins(protein_id) ON DELETE CASCADE,
    prot_range VARCHAR(100) NOT NULL,
    prot_seq TEXT
);

-- 3. CATH Fold Annotations vs DPCstruct Metaclusters
-- Function: Stores CATH fold annotations mapped to DPCstruct metaclusters
-- Fields:
--   - cath_query: CATH fold identifier queried against DPCstruct metaclusters
--   - mc_id: DPCstruct metacluster ID (FK to dpcstruct_mcs_properties)
--   - dpc_target: DPCstruct domain matched with CATH query
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

-- 4. SCOP Fold Annotations vs DPCstruct Metaclusters
-- Function: Stores SCOP fold annotations mapped to DPCstruct metaclusters
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

COMMIT;