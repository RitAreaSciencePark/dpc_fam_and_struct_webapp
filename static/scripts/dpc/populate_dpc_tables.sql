-- =========================================================================
-- II. DPC DATA POPULATION (\copy commands)
-- =========================================================================
-- After creating DPC tables, we populate them with data, by executing the following commands in psql in the given order (Parent tables first):
\copy dpc_uniprot_proteins FROM 'static/dataframes/dpc/dpc_protein_lengths.csv' WITH (FORMAT csv, HEADER true);
\copy dpc_pfam_domains FROM 'static/dataframes/dpc/dpc_pfam_ids.csv' WITH (FORMAT csv, HEADER true);
\copy dpc_uniref50_pfam(uniref50_id, pfam_ids, pfam_ranges) FROM 'static/dataframes/dpc/uniref50_pfam_valid.csv' WITH (FORMAT csv, HEADER true);
