#!/bin/bash

# This script is designed for the automated setup of PostgreSQL for Avalanche CMS and Keycloak.
# During the initialization phase of PostgreSQL, this script is executed, being mounted to /docker-entrypoint-initdb.d/.
# It securely retrieves user passwords from designated secret files.


# Exit on error, unset variables and errors in pipelines
set -eou pipefail


# Functions

# Retrieves a secret from a given file
# This function reads the first line of a file and treats it as a secret.
#
# Arguments:
#   $1 - The file path to the secret file. This should be a readable file containing the secret.
#
# Returns:
#   The secret value, or terminates with code 1 if it failed
#
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

# Creates a new database in PostgreSQL and a user for it. 
# Uses a secret file to inject the password for the created user.
# 
# Arguments:
#   $1 - Database name. The name of the database to be created.
#   $2 - Username. The name of the user to be created for managing the database.
#   $3 - Secret file path. The file path containing the password for the newly created user.
#
# Returns:
#   0 if the database and user were successfully created and configured; 
#   non-zero on error (e.g., if psql commands fail, or the secret file is unreadable).
#
create_db_and_user() {

    local db_name=$1
    local user_name=$2
    local secret_file=$3

    echo "Creating the '$db_name' database and '$user_name' user, and granting connection privileges and other necessary rights..."

    # Retrieve the secret password
    local db_password=$(get_secret_from_file "$secret_file") || exit 1

    # execute PostgreSQL commands
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<EOSQL
        CREATE USER $user_name WITH PASSWORD '$db_password';
        CREATE DATABASE $db_name;
        ALTER DATABASE $db_name OWNER TO $user_name;
        GRANT ALL PRIVILEGES ON DATABASE $db_name TO $user_name;
        GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $user_name;
        ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $user_name;
EOSQL
}


# Main
main() {

    # Create databases and users for 'avalanchecms' and 'keycloak'
    create_db_and_user "avalanchecms" "avalanchecms" "/run/secrets/postgres-avalanchecms-db-user-secret"
    create_db_and_user "keycloak" "keycloak" "/run/secrets/postgres-keycloak-db-user-secret"
}

# Check if the script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
