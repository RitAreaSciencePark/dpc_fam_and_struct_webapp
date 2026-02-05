BEGIN;

CREATE TABLE IF NOT EXISTS mcs_sequences (
    id BIGSERIAL PRIMARY KEY,
    mcid TEXT NOT NULL,
    protein TEXT NOT NULL,
    seq_length INTEGER NOT NULL CHECK (seq_length > 0),
    amino_acids TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    CONSTRAINT fk_mcid FOREIGN KEY (mcid) REFERENCES mcs_properties(mcid) ON DELETE CASCADE
    -- Optional: ensure seq_length matches amino_acids text length
    -- , CONSTRAINT chk_len_matches_amino CHECK (amino_acids IS NULL OR seq_length = char_length(amino_acids))
);

CREATE INDEX IF NOT EXISTS idx_mcs_sequences_mcid ON mcs_sequences(mcid);

COMMIT;