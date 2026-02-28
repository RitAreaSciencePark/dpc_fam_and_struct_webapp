-- =========================================================================
-- I. DATA POPULATION (\copy commands)
-- =========================================================================
-- After creating tables, we populate them with data, by executing the following commands in psql in the given order (Parent tables first):
\copy dpcstruct_mcs_properties FROM 'static/dataframes/dpcstruct/dpcstruct_mcs_properties.csv' WITH (FORMAT csv, HEADER true);

