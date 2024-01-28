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

echo "Setting KEYCLOAK_ADMIN_PASSWORD..."
export KEYCLOAK_ADMIN_PASSWORD="$(get_secret_from_file "${KEYCLOAK_ADMIN_PASSWORD_FILE}")"

echo "Setting KC_DB and KC_DB_URL for PostgreSQL connection..."
export KC_DB="postgres"
echo "KC_DB: $KC_DB"
export KC_DB_URL="jdbc:postgresql://${KC_DB_URL_HOST}:${KC_DB_URL_PORT}/${KC_DB_URL_DATABASE}?user=${KC_DB_USERNAME}&password=$(get_secret_from_file "${KC_DB_PASSWORD_FILE}")&ssl=${KC_DB_URL_SSL_ENABLED}"
echo "KC_DB_URL: jdbc:postgresql://${KC_DB_URL_HOST}:${KC_DB_URL_PORT}/${KC_DB_URL_DATABASE}?user=${KC_DB_USERNAME}&password=*****&ssl=${KC_DB_URL_SSL_ENABLED}"

if [ -n "$@" ]; then
  echo "Starting Keycloak with arguments: $@"
else
  echo "Starting Keycloak..."
fi

exec /opt/keycloak/bin/kc.sh "$@"
