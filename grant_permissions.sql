-- Run this as superuser or postgres user to grant permissions to enyanduk
-- This allows enyanduk to reference mcs_properties in a foreign key constraint

-- Grant usage on schema
GRANT USAGE ON SCHEMA public TO enyanduk;

-- Grant select and references permissions on mcs_properties table
GRANT SELECT, REFERENCES ON TABLE mcs_properties TO enyanduk;

-- Grant create permission on schema
GRANT CREATE ON SCHEMA public TO enyanduk;

-- Verify permissions
\dp mcs_properties
