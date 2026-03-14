-- =========================================================================
-- I. DPC CORE TABLES - CENTRAL REGISTRY
-- =========================================================================

-- 1. Master Table: UniProt Proteins
-- Function: Acts as the central registry for all protein sequences in dpcfam and dpcstruct.
-- Interconnection: All mapping tables (dpcfam_mcs_sequences, dpc_uniref50_pfam, dpcstruct_mcs_sequences) link back here.

CREATE TABLE IF NOT EXISTS dpc_uniprot_proteins (
    protein_id VARCHAR(50) PRIMARY KEY,
    protein_length INTEGER NOT NULL
);

-- 2. Master Table: Pfam Domains
-- Function: Stores unique Pfam domain IDs available in both dpcfam and dpcstruct.
-- Interconnection: Referenced by dpc_uniref50_pfam, dpcfam_mcs_properties (pfam_labels), dpcstruct_mcs_properties (pfam_labels)

CREATE TABLE IF NOT EXISTS dpc_pfam_domains (
    pfam_id VARCHAR(50) PRIMARY KEY,
    pfam_type VARCHAR(50)
);

-- 3. Mapping Table: UniRef50 Pfam Domain Annotations
-- Function: Maps Pfam domains to UniRef50 proteins with position information.
-- Interconnection: Links protein_id (FK -> dpc_uniprot_proteins) and pfam_id (FK -> dpc_pfam_domains).

CREATE TABLE IF NOT EXISTS dpc_uniref50_pfam (
    id BIGSERIAL PRIMARY KEY,
    uniref50_id VARCHAR(50) NOT NULL REFERENCES dpc_uniprot_proteins(protein_id) ON DELETE CASCADE,
    pfam_ids VARCHAR(50) NOT NULL REFERENCES dpc_pfam_domains(pfam_id) ON DELETE CASCADE,
    pfam_ranges VARCHAR(100)
);

-- =========================================================================
-- OPTIMIZATION: INDEXES & PERFORMANCE
-- =========================================================================

-- Fast lookup of Pfam domains per protein
CREATE INDEX IF NOT EXISTS idx_dpc_uniref50_pfam_per_protein ON dpc_uniref50_pfam(uniref50_id);
CREATE INDEX IF NOT EXISTS idx_dpc_uniref50_pfam_per_domain ON dpc_uniref50_pfam(pfam_ids);
-- PGPASSWORD="***REMOVED***" psql -U dpc_admin -h localhost -d postgres -c "DROP DATABASE dpc_db;"