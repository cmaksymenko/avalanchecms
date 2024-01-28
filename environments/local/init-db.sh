#!/bin/bash
set -eou pipefail

# returns secret from mounted file content
# $1: file path to secret file
get_secret_from_file() {

    local file_path="$1"
    
    if [ ! -e "$file_path" ]; then # check if the secret file exists
        echo "Error: The secret file '$file_path' does not exist. Rerun Avalanche CMS setup.py."
        return 1
    fi

    if [ ! -f "$file_path" ]; then # check if the file path is a file and not a directory
        echo "Error: The path '$file_path' is not a file, possibly a directory. Delete and rerun Avalanche CMS setup.py."
        return 1
    fi

    cat "$file_path" || { # output secret
        echo "Failed to get the secret from file '$file_path'" >&2
        return 1
    }
}

echo "Creating the 'avalanchecms' database and user, and granting connection privileges and other necessary rights..."
AVALANCHECMS_SECRET=$(get_secret_from_file "/run/secrets/postgres-avalanchecms-db-user-secret") || exit 1
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE avalanchecms;
    CREATE USER avalanchecms WITH ENCRYPTED PASSWORD '$AVALANCHECMS_SECRET';
	GRANT ALL PRIVILEGES ON DATABASE avalanchecms TO avalanchecms;
EOSQL

echo "Creating the 'keycloak' database and user, and granting connection privileges and other necessary rights..."
KEYCLOAK_SECRET=$(get_secret_from_file "/run/secrets/postgres-keycloak-db-user-secret") || exit 1
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE keycloak;
    CREATE USER keycloak WITH ENCRYPTED PASSWORD '$KEYCLOAK_SECRET';
	GRANT ALL PRIVILEGES ON DATABASE keycloak TO keycloak;
EOSQL
