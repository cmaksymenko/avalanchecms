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

            echo "Replaced all \$ chars with \\\$ in Keycloak database connection secret."

        else
            echo "No \$ found in Keycloak database connection secret. No modification made."
        fi
    else
        echo "Keycloak database connection secret is not set"
    fi
else
    echo "Dollarsign substitution skipped."
fi

echo "Updating Keycloak config."

input_file="/tmp/avalanchecms/keycloak-realm-config.orig.json"

current_epoch_ms=$(date +%s%3N)

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
  echo "Successfully set all users createdTimestamp to current epoch ${current_epoch_ms} in Keycloak config."
else
  echo "Failed to set all users createdTimestamp to current epoch ${current_epoch_ms} in Keycloak config." >&2
  exit 1
fi

DIR="/run/secrets/avalanchecms/hashes"

if [ ! -d "$DIR" ]; then
    echo "Directory $DIR does not exist, not adding any user credentials to Keycloak config."
elif [ -z "$(find "$DIR" -maxdepth 1 -type f -name "*.hash")" ]; then
    echo "No .hash files found in $DIR, not adding any user credentials to Keycloak config."
else

    tmp_output_file2=$(mktemp /tmp/avalanchecms.XXXXXX)

    for filepath in "$DIR"/*.hash; do
        
        filename=$(basename "$filepath")
        user_id=$(echo "$filename" | sed -n 's/^.*-\(.*\)-secret\.hash$/\1/p')

        if [ -z "$user_id" ]; then
            echo "Warning: Filename '$filename' does not follow hash pattern, skipping."
        else

          if jq --arg user_id "$user_id" '.users[] | select(.username == $user_id)' "$tmp_output_file" | grep -q .; then
              
              echo "User ${user_id} found in Keycloak config for hash file ${filename}."

              # Check if the file contains all required keys
              required_keys=("ALGORITHM" "ITERATIONS" "SALT" "HASH")
              missing_keys=()        

              for key in "${required_keys[@]}"; do
                  if ! grep -q "^$key=" "$filepath"; then
                      missing_keys+=("$key")
                  fi
              done

              if [ ${#missing_keys[@]} -ne 0 ]; then
                  echo "Missing keys in hash file ${filename}: ${missing_keys[*]}" >&2
                  exit 1
              fi        

              algorithm=$(sed -n 's/^ALGORITHM=\(.*\)$/\1/p' "$filepath")
              iterations=$(sed -n 's/^ITERATIONS=\(.*\)$/\1/p' "$filepath")
              salt=$(sed -n 's/^SALT=\(.*\)$/\1/p' "$filepath")
              hash=$(sed -n 's/^HASH=\(.*\)$/\1/p' "$filepath")

              jq --arg current_epoch_ms "$current_epoch_ms" \
                --arg hash "$hash" \
                --arg salt "$salt" \
                --arg iterations "$iterations" \
                --arg algorithm "$algorithm" \
                --arg username "$user_id" \
                '(.users[] | select(.username == $username) | .credentials) |= [
                    {
                      "type": "password",
                      "userLabel": "Password",
                      "createdDate": ($current_epoch_ms | tonumber),
                      "secretData": ("{\"value\":\"" + $hash + "\",\"salt\":\"" + $salt + "\",\"additionalParameters\":{}}"),
                      "credentialData": ("{\"hashIterations\":" + $iterations + ",\"algorithm\":\"" + $algorithm + "\",\"additionalParameters\":{}}")
                    }
                  ]' ${tmp_output_file} > ${tmp_output_file2}                

              # Check for success
              if [ $? -eq 0 ]; then
                  echo "Credentials for user '${user_id}' added to Keycloak config."
              else
                  echo "Failed to add credentials for user '${user_id}' to Keycloak config." >&2
                  exit 1
              fi

              mv ${tmp_output_file2} ${tmp_output_file}

          else
              echo "User ${user_id} not found in Keycloak config for hash file ${filename}, skipping."
          fi

        fi        
    done
fi

echo "Moving modified Keycloak config to /opt/keycloak/data/import/"

mkdir -p /opt/keycloak/data/import/
mv ${tmp_output_file} /opt/keycloak/data/import/keycloak-realm-config.json

find /tmp -type f -name 'avalanchecms.*' -exec rm {} +

echo "Keycloak config successfully updated."
