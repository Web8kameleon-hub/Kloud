#!/bin/bash
set -e

# Create additional database "kloud" if not exists
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    SELECT 'CREATE DATABASE kloud' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'kloud')\gexec
    GRANT ALL PRIVILEGES ON DATABASE kloud TO kloud;
EOSQL

echo "✅ Database 'kloud' created or already exists"

