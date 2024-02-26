#!/bin/sh

main() {
    echo "Starting pgAdmin setup process..."

    SOURCE_FILE="/run/secrets/avalanchecms/.pgpass"

    if [ -r "$SOURCE_FILE" ]; then

        if [ -z "$PGPASSFILE" ]; then
            PGPASSFILE="/tmp/passfile"
            export PGPASSFILE
            echo "Setting env var PGPASSFILE to ${PGPASSFILE}"
        fi

        cp "$SOURCE_FILE" "$PGPASSFILE" && \
        chmod 0600 "$PGPASSFILE"
        echo "Copied $SOURCE_FILE to $PGPASSFILE"

    else
        echo "Error: '$SOURCE_FILE' does not exist or is not readable."
    fi    

    echo "pgAdmin setup completed."
}

main
