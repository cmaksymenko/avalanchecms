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

echo "Preparing Keycloak realm config."

input_file="/tmp/avalanchecms/keycloak-realm-config.orig.json"

current_epoch_ms=$(date +%s%3N)

echo "input_file: $input_file"
echo "current_epoch_ms: $current_epoch_ms"

find /tmp -type f -name 'avalanchecms.*' -exec rm {} +

tmp_output_file=$(mktemp /tmp/avalanchecms.XXXXXX)

# Set users createdTimestamp to current epoch
jq --arg epoch "$current_epoch_ms" '
  if .users and (.users | type) == "array" and (.users | length) > 0 then
    .users |= map(
      if .createdTimestamp then
        .createdTimestamp = ($epoch | tonumber)
      else
        . + {"createdTimestamp": ($epoch | tonumber)}
      end
    )
  else
    .
  end
' "$input_file" > "$tmp_output_file"

if [ $? -eq 0 ]; then
  echo "Set user createdTimestamp to current epoch."
else
  echo "Failed to set user createdTimestamp." >&2
  exit 1
fi

echo "Copying modified Keycloak config to /opt/keycloak/data/import/keycloak-realm-config.json"

mkdir -p /opt/keycloak/data/import/
mv ${tmp_output_file} /opt/keycloak/data/import/keycloak-realm-config.json

echo "Keycloak successfully configured."
