# This script automates Keycloak setup, including escaping database passwords,
# and updating user credentials.

#!/bin/sh

# Escapes dollar signs in Keycloak DB password to prevent evaluation bugs.
#
# Relevant issue and PR:
# https://github.com/keycloak/keycloak/issues/19831
# https://github.com/keycloak/keycloak/pull/22585
#
# Globals:
#   KC_DB_PASSWORD - Keycloak DB password (modified if it contains $).
#   AV_NO_DLR_SUB - If set, skips $ sign substitution.
#
escape_keycloak_db_pwd() {

    echo "Escaping dollar signs in DB password if necessary."

    # Skip if AV_NO_DLR_SUB is set
    if [ -z "${AV_NO_DLR_SUB}" ]; then
        if [ ! -z "${KC_DB_PASSWORD}" ]; then

            # Check and replace $ with \$ in KC_DB_PASSWORD
            if echo "${KC_DB_PASSWORD}" | grep -q "\$"; then

                KC_DB_PASSWORD=$(echo "${KC_DB_PASSWORD}" | sed 's/\$/\\$/g')
                export KC_DB_PASSWORD
                
                echo "Replaced all \$ with \\\$ in DB password."

            else
                echo "No \$ in DB password. No modification made."
            fi
        else
            echo "DB password not set."
        fi
    else
        echo "Dollar sign substitution skipped."
    fi
}

# Sets Keycloak environment variables.
# Initializes and updates necessary variables for Keycloak.
update_keycloak_env() {

    echo "Setting Keycloak environment variables."

    escape_keycloak_db_pwd

    echo "Environment processing completed."
}

# Cleans up temporary files from /tmp.
# Returns: 0 on success/no files, 1 on error
cleanup_tmp_files() {

    file_count=$(find /tmp -type f -name 'avalanchecms.*' | wc -l)
    if [ $file_count -eq 0 ]; then
        echo "No Avalanche CMS tmp files found in /tmp."
        return 0
    fi

    find /tmp -type f -name 'avalanchecms.*' -exec rm {} +

    if [ $? -eq 0 ]; then
        echo "Successfully removed $file_count Avalanche CMS tmp files from /tmp."
        return 0
    else
        echo "Failed to remove Avalanche CMS files from /tmp." >&2
        return 1
    fi
}

# Asserts existence of secret hash files in the specified directory.
# Checks if dir exists and contains .hash files, returning error codes.
#
# Parameters:
#   dir_path - Directory to check for hash files.
#
# Returns:
#   0 if .hash files found
#   1 if dir_path missing
#   2 if dir doesn't exist or no .hash files
#
assert_secret_hash_files() {

    local dir_path=$1

    # Check if dir_path parameter is provided
    if [ -z "$dir_path" ]; then
        echo "Parameter 'dir_path' is missing for assert_secret_hash_files function." >&2
        return 1
    fi

    if [ ! -d "$dir_path" ]; then
        echo "Directory $dir_path does not exist, not adding any user credentials to Keycloak config."
        return 2
    fi

    local hash_files_count=$(find "$dir_path" -maxdepth 1 -type f -name "*.hash" | wc -l)

    if [ $hash_files_count -eq 0 ]; then
        echo "No .hash files found in $dir_path, not adding any user credentials to Keycloak config."
        return 2
    else
        echo "Found $hash_files_count .hash file(s) in $dir_path."
        return 0
    fi
}

# Updates users' createdTimestamp to current epoch in Keycloak config.
# Calculates epoch if not provided. Creates tmp file if not provided.
#
# Parameters:
#   input_file - File containing Keycloak config.
#   current_epoch_ms (optional) - Current epoch in ms.
#   tmp_output_file (optional) - Temporary output file.
#
# Returns:
#   0 on success, 1 on error. Outputs tmp file path on success.
#
update_users_timestamp() {

    local input_file=$1
    local current_epoch_ms=$2
    local tmp_output_file=$3

    # Check if input_file is provided
    if [ -z "$input_file" ]; then
        echo "Input file is missing." >&2
        return 1
    fi

    # Calculate current_epoch_ms if not provided
    if [ -z "$current_epoch_ms" ]; then
        current_epoch_ms=$(date +%s%3N)
    fi

    # Create a temporary file if tmp_output_file is not provided
    if [ -z "$tmp_output_file" ]; then
        tmp_output_file=$(mktemp /tmp/avalanchecms.XXXXXX)
    fi

    # Set users createdTimestamp to current epoch
    if jq --arg epoch "$current_epoch_ms" '
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
        ' "$input_file" > "$tmp_output_file"; then

        # Using stdout for output data and stderr for log messages to separate data from diagnostics
        echo "Successfully set all users createdTimestamp to current epoch ${current_epoch_ms} in Keycloak config." >&2
        echo "$tmp_output_file"
        
        return 0
    else
        echo "Failed to set all users createdTimestamp to current epoch ${current_epoch_ms} in Keycloak config." >&2
        return 1
    fi
}

# Updates Keycloak user credentials from hash file.
# Checks if necessary files exist. Calculates epoch if not provided.
# Creates tmp output config if needed.
#
# Parameters:
#   keycloak_config_filepath - Path to Keycloak config file.
#   hash_filepath - Path to hash file.
#   keycloak_tmp_config (optional) - Temporary output config file.
#   current_epoch_ms (optional) - Current epoch in milliseconds.
#
# Returns:
#   0 on success, 1 on error.
#
update_user_credential_from_hash_file() {

    local keycloak_config_filepath=$1
    local hash_filepath=$2
    local keycloak_tmp_config=$3
    local current_epoch_ms=$4

    # Required args check
    if [ -z "$hash_filepath" ] || [ -z "$keycloak_config_filepath" ]; then
        [ -z "$hash_filepath" ] && echo "Hash file path is required." >&2
        [ -z "$keycloak_config_filepath" ] && echo "Keycloak config filepath is required." >&2
        return 1
    fi

    # Check if the files actually exist
    if [ ! -f "$hash_filepath" ] || [ ! -f "$keycloak_config_filepath" ]; then
        [ ! -f "$hash_filepath" ] && echo "Hash file at '$hash_filepath' does not exist." >&2
        [ ! -f "$keycloak_config_filepath" ] && echo "Keycloak config file at '$keycloak_config_filepath' does not exist." >&2
        return 1
    fi

    # Calculate current_epoch_ms if not provided
    if [ -z "$current_epoch_ms" ]; then
        current_epoch_ms=$(date +%s%3N)
    fi

    local filename=$(basename "$hash_filepath")

    local user_id=$(echo "$filename" | sed -n 's/^.*-\(.*\)-secret\.hash$/\1/p')
    if [ -z "$user_id" ]; then
        echo "Warning: Filename '$filename' does not follow hash pattern, skipping."
        return 0
    fi

    if jq --arg user_id "$user_id" '.users[] | select(.username == $user_id)' "$keycloak_config_filepath" | grep -q .; then

        # Check if keycloak_tmp_config is provided
        if [ -n "$keycloak_tmp_config" ]; then
            if [ ! -f "$keycloak_tmp_config" ] || [ ! -w "$keycloak_tmp_config" ]; then
                echo "Provided Keycloak temporary output config file at '$keycloak_tmp_config' does not exist or is not writable." >&2
                return 1
            fi
        else
            keycloak_tmp_config=$(mktemp /tmp/avalanchecms.XXXXXX)
        fi    
    
        echo "User ${user_id} found in Keycloak config for hash file ${filename}."

        # Check if the file contains all required keys
        required_keys=("ALGORITHM" "ITERATIONS" "SALT" "HASH")
        missing_keys=()        

        for key in "${required_keys[@]}"; do
            if ! grep -q "^$key=" "$hash_filepath"; then
                missing_keys+=("$key")
            fi
        done

        if [ ${#missing_keys[@]} -ne 0 ]; then
            echo "Missing keys in hash file ${filename}: ${missing_keys[*]}" >&2
            return 1
        fi        

        algorithm=$(sed -n 's/^ALGORITHM=\(.*\)$/\1/p' "$hash_filepath")
        iterations=$(sed -n 's/^ITERATIONS=\(.*\)$/\1/p' "$hash_filepath")
        salt=$(sed -n 's/^SALT=\(.*\)$/\1/p' "$hash_filepath")
        hash=$(sed -n 's/^HASH=\(.*\)$/\1/p' "$hash_filepath")

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
            ]' ${keycloak_config_filepath} > ${keycloak_tmp_config}                

        # Check for success
        if [ $? -eq 0 ]; then
            echo "Credentials for user '${user_id}' added to Keycloak config."
        else
            echo "Failed to add credentials for user '${user_id}' to Keycloak config." >&2
            return 1
        fi

        return 0
    else
        echo "User ${user_id} not found in Keycloak config for hash file ${filename}, skipping."
        return 0
    fi
}

# Updates Keycloak config with user timestamps and credentials. Moves final
# config to /opt/keycloak/data/import/ for automatic import by Keycloak.
update_keycloak_config() {

    echo "Updating Keycloak config."

    cleanup_tmp_files

    keycloak_config_orig="/tmp/avalanchecms/keycloak-realm-config.orig.json"
    keycloak_config_updated_user_timestamps=$(update_users_timestamp "$keycloak_config_orig") || return 1

    hashes_dir="/run/secrets/avalanchecms/hashes"

    keycloak_config_updated_from="${keycloak_config_updated_user_timestamps}"
    keycloak_config_updated_user_credentials="${keycloak_config_updated_user_timestamps}"

    if assert_secret_hash_files "$hashes_dir"; then

        echo "Processing user credentials..."

        for hash_filepath in "$hashes_dir"/*.hash; do

            keycloak_config_updated_to=$(mktemp /tmp/avalanchecms.XXXXXX)

            update_user_credential_from_hash_file "${keycloak_config_updated_from}" "${hash_filepath}" "${keycloak_config_updated_to}"
            if [ $? -ne 0 ]; then
                echo "Error occurred in update_user_credential_from_hash_file." >&2
                return 1
            fi            

            keycloak_config_updated_user_credentials="${keycloak_config_updated_to}"
            keycloak_config_updated_from="${keycloak_config_updated_to}"

        done
 
    elif [ $? -eq 2 ]; then
        echo "Skipping user credential processing due to no hash files found..."
    else
        echo "An error occurred, exiting..." >&2
        return 1
    fi

    echo "Moving modified Keycloak config to /opt/keycloak/data/import/"

    mkdir -p /opt/keycloak/data/import/
    mv ${keycloak_config_updated_user_credentials} /opt/keycloak/data/import/keycloak-realm-config.json

    cleanup_tmp_files

    echo "Keycloak config processing completed."
}

# Main
main() {
    echo "Starting Keycloak setup process..."

    update_keycloak_env
    if [ $? -ne 0 ]; then
        echo "Error occurred in update_keycloak_env." >&2
        return 1
    fi

    update_keycloak_config
    if [ $? -ne 0 ]; then
        echo "Error occurred in update_keycloak_config." >&2
        return 1
    fi

    echo "Keycloak setup completed."
}

main
