-- =========================================================================
-- DPCFam Database Schema
-- Optimized for Performance, Integrity, and Interconnectivity
-- =========================================================================

-- 1. Master Table: UniRef50 Proteins
-- Function: Acts as the central registry for all protein sequences.
-- Interconnection: All mapping tables (mcs_sequences, uniref50_pfam) link back here.
CREATE TABLE IF NOT EXISTS uniref50_proteins (
    uniref50_id VARCHAR(50) PRIMARY KEY,
    uniprotkb_id VARCHAR(100),
    uniprotkb_accession VARCHAR(50),
    length INTEGER
);

-- 2. Master Table: Metaclusters (DPCFam)
-- Function: Stores the biological and structural properties of protein metaclusters.
-- Interconnection: Central hub for clustering data.
CREATE TABLE IF NOT EXISTS mcs_properties (
    mcid VARCHAR(50) PRIMARY KEY,
    size_uniref50 INTEGER,
    avg_len DOUBLE PRECISION,
    std_avg_len DOUBLE PRECISION,
    lc_percent DOUBLE PRECISION,
    cc_percent DOUBLE PRECISION,
    dis_percent DOUBLE PRECISION,
    tm DOUBLE PRECISION,
    pfam_da TEXT,           -- Some samples are merged (e.g., MC100282: PF06743PF08368). We will fix it.
    da_percent DOUBLE PRECISION,
    size_pfam INTEGER,      
    avg_ov_percent DOUBLE PRECISION,
    overlap_label VARCHAR(50)
);

-- 3. Mapping Table: Metacluster Sequences
-- Function: Links specific Proteins to Metaclusters and stores coordinates.
-- Interconnection: Links protein_id (FK -> uniref50_proteins) and mcid (FK -> mcs_properties).
CREATE TABLE IF NOT EXISTS mcs_sequences (
    id BIGSERIAL PRIMARY KEY,
    mcid VARCHAR(50) NOT NULL REFERENCES mcs_properties(mcid) ON DELETE CASCADE,
    protein_id VARCHAR(50) NOT NULL REFERENCES uniref50_proteins(uniref50_id) ON DELETE CASCADE,
    seq_range VARCHAR(100) NOT NULL,
    seq_length INTEGER NOT NULL,
    aa_seq TEXT NOT NULL
);

-- 4. Mapping Table: Pfam Domains
-- Function: Maps Pfam domains to UniRef50 proteins.
-- Interconnection: Links uniref50_id (FK -> uniref50_proteins).
CREATE TABLE IF NOT EXISTS uniref50_pfam (
    id BIGSERIAL PRIMARY KEY,
    uniref50_id VARCHAR(50) NOT NULL REFERENCES uniref50_proteins(uniref50_id) ON DELETE CASCADE,
    pfam_ids VARCHAR(50) NOT NULL,
    pfam_ranges VARCHAR(100)
);

-- 5. Structural Table: AlphaFold Representatives
-- Function: Stores representatives for metaclusters.
-- Interconnection: Links back to mcs_properties(mcid).
CREATE TABLE IF NOT EXISTS alphafold_reps(
    id BIGSERIAL PRIMARY KEY,
    mcid VARCHAR(50) NOT NULL REFERENCES mcs_properties(mcid) ON DELETE CASCADE,
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
CREATE INDEX IF NOT EXISTS idx_mcs_prop_num ON mcs_properties (CAST(SUBSTRING(mcid FROM '[0-9]+') AS INTEGER));

-- High-Speed Discovery: Indexes for frequent search queries
CREATE INDEX IF NOT EXISTS idx_uniref50_uniprot_id ON uniref50_proteins(uniprotkb_id);
CREATE INDEX IF NOT EXISTS idx_mcs_seq_protein ON mcs_sequences(protein_id);
CREATE INDEX IF NOT EXISTS idx_mcs_seq_mcid ON mcs_sequences(mcid);
CREATE INDEX IF NOT EXISTS idx_uniref50_pfam_protein ON uniref50_pfam(uniref50_id);

-- AlphaFold Representatives: Filter by metacluster
CREATE INDEX IF NOT EXISTS idx_alphafold_reps_mcid ON alphafold_reps(mcid);

-- Trigram Index: Optimizes Regex/Text searches on "Fused" Pfam strings
-- Allows the app to quickly find Metaclusters containing a specific Pfam domain.
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX IF NOT EXISTS idx_pfam_da_trgm ON mcs_properties USING gin (pfam_da gin_trgm_ops);



-- =========================================================================
-- PERMISSIONS (Standardizing for Django access)
-- =========================================================================
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO enyanduk;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO enyanduk;
