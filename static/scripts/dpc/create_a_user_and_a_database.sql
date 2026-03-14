-- This script creates a PostgreSQL user(dpc_admin) and a database(dpc_db) for our project:
-- 0. Installation
-- sudo apt update
-- sudo apt install postgresql postgresql-contrib

-- 1. Start the PostgreSQL service from the terminal
--sudo service postgresql start

-- 2. Connect as postgres: default superuser created during installation
--sudo -u postgres psql

-- SQL COMMANDS:
-- Create a user
CREATE USER dpc_admin WITH PASSWORD '***REMOVED***';

-- Create the database
CREATE DATABASE dpc_db OWNER dpc_admin;

-- Grant all privileges on the database
GRANT ALL PRIVILEGES ON DATABASE dpc_db TO dpc_admin;

-- Connect to the database to grant schema privileges
\c dpc_db

-- Grant schema permissions to dpc_admin : Optional
GRANT ALL ON SCHEMA public TO dpc_admin;

-- =========================================================================
-- PERMISSIONS (Standardizing for Django access)
-- =========================================================================
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO dpc_admin;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO dpc_admin;




-- Exit
\q

-- 3. Verification (Run in the terminal; use password = ***REMOVED***)
--psql -U dpc_admin -h localhost -d dpc_db -c "SELECT 1;"