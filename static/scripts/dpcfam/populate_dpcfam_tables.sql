-- =========================================================================
-- I. DATA POPULATION (\copy commands)
-- =========================================================================
-- After creating tables, we populate them with data, by executing the following commands in psql in the given order (Parent tables first):
\copy uniref50_proteins FROM 'static/dataframes/dpcfam/uniref50_proteins.csv' WITH (FORMAT csv, HEADER true);
\copy mcs_properties FROM 'static/dataframes/dpcfam/dpcfam_mcs_props.csv' WITH (FORMAT csv, HEADER true);
\copy mcs_sequences(mcid, protein_id, seq_range, seq_length, aa_seq) FROM 'static/dataframes/dpcfam/dpcfam_sequences.csv' WITH (FORMAT csv, HEADER true);
\copy uniref50_pfam(uniref50_id, pfam_ids, pfam_ranges) FROM 'static/dataframes/dpcfam/uniref50_pfam_valid.csv' WITH (FORMAT csv, HEADER true);
\copy alphafold_reps(mcid, alphafold_prot, seq_range, hmm_coverage, avg_plddt) FROM 'static/dataframes/dpcfam/alphafold_dpcfam_reps.csv' WITH (FORMAT csv, HEADER true);

-- =========================================================================
--II. DATA CLEANUP: Standardizing Pfam labels in pfam_da column 
-- =========================================================================
-- We must ensures that fusionned labels are separated by '-' (e.g., PF00001PF12345 -> PF00001-PF12345)
-- Each Pfam ID starts with 'PF' followed by 5 digits and is 7 characters long.
UPDATE mcs_properties 
SET pfam_da = REGEXP_REPLACE(pfam_da, '([A-Z0-9]{7})(?=PF)', '\1-', 'g')
WHERE pfam_da ~ 'PF[0-9]{5}PF';