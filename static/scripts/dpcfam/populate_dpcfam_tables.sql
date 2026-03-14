-- =========================================================================
-- IV. DPCFAM DATA POPULATION (\copy commands)
-- =========================================================================
-- After creating tables, we populate them with data, by executing the following commands in psql in the given order (Parent tables first):
\copy dpcfam_mcs_properties FROM 'static/dataframes/dpcfam/dpcfam_all_mcs_props.csv' WITH (FORMAT csv, HEADER true);
\copy dpcfam_mcs_sequences(mcid, protein_id, seq_range, seq_length, aa_seq) FROM 'static/dataframes/dpcfam/dpcfam_all_mcs_sequences.csv' WITH (FORMAT csv, HEADER true);
\copy dpcfam_alphafold_reps(mcid, alphafold_prot, seq_range, hmm_coverage, avg_plddt) FROM 'static/dataframes/dpcfam/alphafold_dpcfam_reps.csv' WITH (FORMAT csv, HEADER true);
