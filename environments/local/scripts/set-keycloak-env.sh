#!/bin/sh

echo "Setting Keycloak environment variables."

# Escape $$ in DB password to avoid KeyCloak param eval bug.
# See: https://github.com/keycloak/keycloak/issues/19831
#      https://github.com/keycloak/keycloak/pull/22585

# Check if AV_NO_DLR_SUB is not set
if [ -z "${AV_NO_DLR_SUB}" ]; then

    if [ ! -z "${KC_DB_PASSWORD}" ]; then
    
        # Check if KC_DB_PASSWORD contains at least one $
        if echo "${KC_DB_PASSWORD}" | grep -q "\$"; then

            # Replace every $ with \$
            KC_DB_PASSWORD=$(echo "${KC_DB_PASSWORD}" | sed 's/\$/\\$/g')

            export KC_DB_PASSWORD

            echo "Replaced every $ with \\\$ in KC_DB_PASSWORD."
        else
            echo "No \$ found in KC_DB_PASSWORD. No modification made."
        fi
    else
        echo "KC_DB_PASSWORD is not set"
    fi
else
    echo "Dollarsign substitution skipped."
fi