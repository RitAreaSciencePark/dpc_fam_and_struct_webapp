-- This script creates a PostgreSQL user(enyanduk) and a database(dpcfam_mcs_db) for our project:
-- 0. Installation
-- sudo apt update
-- sudo apt install postgresql postgresql-contrib

-- 1. Start the PostgreSQL service from the terminal
--sudo service postgresql start

-- 2. Connect as postgres: default superuser created during installation
--sudo -u postgres psql

-- SQL COMMANDS:
-- Create a user
CREATE USER enyanduk WITH PASSWORD '***REMOVED***';

-- Create the database
CREATE DATABASE dpcfam_mcs_db OWNER enyanduk;

-- Grant all privileges on the database
GRANT ALL PRIVILEGES ON DATABASE dpcfam_mcs_db TO enyanduk;

-- Connect to the database to grant schema privileges
\c dpcfam_mcs_db

-- Grant schema permissions to enyanduk
GRANT USAGE, CREATE ON SCHEMA public TO enyanduk;
GRANT ALL ON SCHEMA public TO enyanduk;

-- Exit
\q

-- 3. Verification (Run in the terminal; use password = ***REMOVED***)
--psql -U enyanduk -h localhost -d dpcfam_mcs_db -c "SELECT 1;"