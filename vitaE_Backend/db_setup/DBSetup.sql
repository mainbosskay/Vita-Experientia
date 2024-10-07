-- Configure PostgreSQL server for Vita Experientia

-- Drop the database if it exists
DROP DATABASE IF EXISTS vita_experientia_db;

-- Create new database
CREATE DATABASE vita_experientia_db
	WITH
	OWNER = postgres
	ENCODING = 'utf8'
	CONNECTION LIMIT = -1;

-- Add a description on the database
COMMENT ON DATABASE vita_experientia_db
	IS 'Database repository for Vita Experientia';

-- Drop role if it exists
DROP ROLE IF EXISTS vita_experientia_user;

-- Create the new role
CREATE ROLE vita_experientia_user
	WITH
	LOGIN
	REPLICATION
	BYPASSRLS
	PASSWORD 'vita_experientia_pwd';

-- Grant privileges
GRANT ALL ON DATABASE vita_experientia_db TO vita_experientia_user;
