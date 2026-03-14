-- =========================================================================
-- VI. DPCSTRUCT DATA POPULATION (\copy commands)
-- =========================================================================
-- After creating tables, we populate them with data, by executing the following commands in psql in the given order (Parent tables first):
\copy dpcstruct_mcs_properties FROM 'static/dataframes/dpcstruct/dpcstruct_mcs_properties.csv' WITH (FORMAT csv, HEADER true);
-- Populate dpcstruct_mcs_sequences with data from the CSV file, ensuring that the mc_id values match those in dpcstruct_mcs_properties for referential integrity.
\copy dpcstruct_mcs_sequences (mc_id, protein_id, prot_range, prot_seq) FROM 'static/dataframes/dpcstruct/dpcstruct_mcs_sequences.csv' WITH (FORMAT csv, HEADER true);
-- CATH :From  static/dataframes/dpcstruct/cleaned_annotated_cath_qc0.8_t0.5_l0.5.csv
\copy dpcstruct_cath FROM 'static/dataframes/dpcstruct/cleaned_annotated_cath_qc0.8_t0.5_l0.5.csv' WITH (FORMAT csv, HEADER true);
-- SCOP : From static/dataframes/dpcstruct/cleaned_annotated_scop_qc0.8_t0.5_l0.5.csv
\copy dpcstruct_scop FROM 'static/dataframes/dpcstruct/cleaned_annotated_scop_qc0.8_t0.5_l0.5.csv' WITH (FORMAT csv, HEADER true);