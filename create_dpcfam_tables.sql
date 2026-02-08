-- Create mcs_properties table
CREATE TABLE IF NOT EXISTS mcs_properties (
    mcid TEXT PRIMARY KEY,
    size_uniref50 INTEGER,
    avg_len FLOAT,
    std_avg_len FLOAT,
    lc_percent FLOAT,
    cc_percent FLOAT,
    dis_percent FLOAT,
    tm FLOAT,
    pfam_da VARCHAR(200),
    da_percent FLOAT,
    size_pfam INTEGER,
    avg_ov_percent FLOAT,
    overlap_label VARCHAR(100)
);

-- # Populate it with data :
-- \copy mcs_properties
-- FROM '/home/p9-30/dpc_data/dpcfam/dataframes/dpcfam_mcs_props.csv'
-- CSV HEADER;


-- Create mcs_sequences table
CREATE TABLE IF NOT EXISTS mcs_sequences (
    id BIGSERIAL PRIMARY KEY,
    mcid TEXT NOT NULL,
    protein_id VARCHAR(255) NOT NULL,
    seq_range VARCHAR(100) NOT NULL,
    seq_length INTEGER NOT NULL,
    aa_seq TEXT NOT NULL
);

-- Create alphafold_reps table
CREATE TABLE IF NOT EXISTS alphafold_reps (
    id BIGSERIAL PRIMARY KEY,
    mcid TEXT NOT NULL,
    alphafold_prot VARCHAR(255) NOT NULL,
    seq_range VARCHAR(100) NOT NULL,
    hmm_coverage FLOAT NOT NULL,
    avg_plddt FLOAT NOT NULL
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_mcs_sequences_mcid ON mcs_sequences(mcid);
CREATE INDEX IF NOT EXISTS idx_alphafold_reps_mcid ON alphafold_reps(mcid);

-- Grant permissions to enyanduk user
GRANT SELECT, INSERT, UPDATE, DELETE ON mcs_properties TO enyanduk;
GRANT SELECT, INSERT, UPDATE, DELETE ON mcs_sequences TO enyanduk;
GRANT SELECT, INSERT, UPDATE, DELETE ON alphafold_reps TO enyanduk;
GRANT USAGE, SELECT ON SEQUENCE mcs_sequences_id_seq TO enyanduk;
GRANT USAGE, SELECT ON SEQUENCE alphafold_reps_id_seq TO enyanduk;
