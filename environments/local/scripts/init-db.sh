# Script automates PostgreSQL setup for Avalanche CMS and Keycloak.
# Executed in initialization, mounted at /docker-entrypoint-initdb.d/.
# Retrieves user passwords from secret files securely.

#!/bin/bash
set -eou pipefail

# Retrieves a secret from a specified file.
# Reads the first line as the secret.
#
# Arguments:
#   $1 - Path to the secret file, expected to contain the secret.
#
# Returns:
#   Secret value, or exits with code 1 on failure.
read_secret_from_file() {

    local file_path="$1"
    
    if [ ! -e "$file_path" ]; then # check if the secret file exists
        echo "Error: Missing '$file_path'." >&2
        return 1
    fi

    if [ ! -f "$file_path" ]; then # check if the file path is a file and not a directory
        echo "Error: '$file_path' not a file, may be a directory." >&2
        return 1
    fi

    cat "$file_path" || { # output secret
        echo "Error: Failed to read secret from '$file_path'" >&2
        return 1
    }
}

# Creates a PostgreSQL database and a user with a password from a secret file.
#
# Arguments:
#   $1 - Database name to create.
#   $2 - Username for managing the database.
#   $3 - Path to secret file with user's password.
#
# Returns:
#   0 on success, non-zero on error (e.g., psql command failure, unreadable secret).
create_db_and_user() {

    local db_name=$1
    local user_name=$2
    local secret_file=$3

    echo "Creating '$db_name' database, '$user_name' user, and setting privileges..."

    # Retrieve the secret password
    local db_password=$(read_secret_from_file "$secret_file") || exit 1

    # execute PostgreSQL commands
    psql -v ON_ERROR_STOP=1 --dbname "$POSTGRES_DB" --username "$POSTGRES_USER" <<EOSQL
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

    # Creates databases and users for 'avalanchecms' and 'keycloak'.
    create_db_and_user "avalanchecmsdb" "postgresavalanchecmsdbuser" "/run/secrets/avalanchecms/postgres-avalanchecms-db-user-secret.env"
    create_db_and_user "keycloakdb" "postgreskeycloakdbuser" "/run/secrets/avalanchecms/postgres-keycloak-db-user-secret.env"
}

main "$@"
