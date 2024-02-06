#!/bin/sh

# Encode a string for safe use in a URL by percent-encoding non URL-safe characters.
# $1 - The input string to be encoded.
# Returns the encoded string suitable for use in a URL.
urlencode() {

    local input=$(printf "%s" "$1" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    local length=$(printf "%s" "$input" | wc -m | tr -d ' ')

    i=1  # Start from 1 since shell cut command is 1-indexed
    while [ $i -le $length ]; do
        c=$(printf "%s" "$input" | cut -c $i)
        case $c in
            [a-zA-Z0-9.~_-]) printf "%s" "$c" ;;
            *) printf '%%%02X' "'$c" ;;
        esac
        i=$(expr $i + 1)
    done
}

# build and export Keycloak database URL
build_and_export_kc_db_url() {
    
    local host="$1"
    local port="$2"
    local dbname="$3"
    local username="$4"
    local password="$5"
    local sslEnabled="$6"

    # Build the JDBC URL
    KC_DB_URL="jdbc:postgresql://${host}:${port}/${dbname}?user=${username}&password=${password}&ssl=${sslEnabled}"
    export KC_DB_URL

    echo "KC_DB_URL set to: jdbc:postgresql://${host}:${port}/${dbname}?user=${username}&password=*****&ssl=${sslEnabled}"
}

# Main function
main() {

    build_and_export_kc_db_url "${KC_DB_URL_HOST}" "${KC_DB_URL_PORT}" "${KC_DB_URL_DATABASE}" "${KC_DB_USERNAME}" "$(urlencode "$KC_DB_PASSWORD")" "${KC_DB_URL_SSL_ENABLED}"
}

main "$@"