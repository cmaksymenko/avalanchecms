#!/bin/sh

main() {
    echo "Starting setup."

    SOURCE_FILE="/run/secrets/avalanchecms/.pgpass"

    if [ -r "$SOURCE_FILE" ]; then

        if [ -z "$PGPASSFILE" ]; then
            PGPASSFILE="/tmp/passfile"
            export PGPASSFILE
            echo "PGPASSFILE set to ${PGPASSFILE}"
        fi

        if cp "$SOURCE_FILE" "$PGPASSFILE" && chmod 0600 "$PGPASSFILE"; then
            echo "Configured $PGPASSFILE"
        fi

    else
        echo "Error: Source file issue."
    fi    

    echo "Setup completed."
}

main
