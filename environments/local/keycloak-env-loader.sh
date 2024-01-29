#!/bin/bash

# This script is designed for dynamically loading environment variables and secrets before Keycloak is started.
# It securely retrieves user passwords from designated secret files.


# Exit on error, unset variables and errors in pipelines
set -eou pipefail


# Functions

# Returns secret from mounted file content
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

# Encodes a string for safe use in a URL by percent-encoding characters that are not URL-safe
# $1 - The input string to be encoded.
# Returns the encoded string suitable for use in a URL
#
urlencode() {
    local length="${#1}"
    for (( i = 0; i < length; i++ )); do
        local c="${1:i:1}"
        case $c in
            [a-zA-Z0-9.~_-]) printf "$c" ;;
            *) printf '%%%02X' "'$c" ;;
        esac
    done
}


# Main
main() {

    # set Keycloak env vars

    echo "Setting KEYCLOAK_ADMIN_PASSWORD..."
    export KEYCLOAK_ADMIN_PASSWORD="$(get_secret_from_file "${KEYCLOAK_ADMIN_PASSWORD_FILE}")"

    echo "Setting KC_DB and KC_DB_URL for PostgreSQL connection..."
    export KC_DB="postgres"
    echo "KC_DB: $KC_DB"

    export KC_DB_URL="jdbc:postgresql://${KC_DB_URL_HOST}:${KC_DB_URL_PORT}/${KC_DB_URL_DATABASE}?user=${KC_DB_USERNAME}&password=$(urlencode "$(get_secret_from_file "${KC_DB_PASSWORD_FILE}")")&ssl=${KC_DB_URL_SSL_ENABLED}"
    echo "KC_DB_URL: jdbc:postgresql://${KC_DB_URL_HOST}:${KC_DB_URL_PORT}/${KC_DB_URL_DATABASE}?user=${KC_DB_USERNAME}&password=*****&ssl=${KC_DB_URL_SSL_ENABLED}"

    # start Keycloak

    if [ -n "$@" ]; then
    echo "Starting Keycloak with arguments: $@"
    else
    echo "Starting Keycloak..."
    fi

    exec /opt/keycloak/bin/kc.sh "$@"
}

# Check if the script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
