#!/bin/sh
set -e

# Generic entrypoint for containers used in the Avalanche CMS local stack.
# It performs a variety of streamlined operations, such as file validation, 
# loading of sensitive information from secret files, and custom script execution, 
# before invoking the original entrypoint of the used container.
#
# Options:
#
# - Env _FILE Path Validation: Automatically checks if filepaths in env vars
#   denoted with _FILE are valid and readable. Skip with setting AV_SKIP_FILE_CHECKS 
#   to any value.
#
# - Secret Loading from _FILE Envs: If AV_LOAD_SECRET_ENVS is set, env vars
#   with _FILE suffix and keywords PASSWORD or SECRET in them are loaded, and a new
#   env var with the same name (minus the suffix) is exported. Should not be used
#   if the container already performs this operation, such as Postgres.
#
# - Custom Script: If AV_CUSTOM_SCRIPT is set to a filepath, the script is called 
#   before invoking the original entrypoint to run custom initialization logic.
#
# Usage:
#
# Pass the original name of the container to AV_APP_NAME for stdout.
# You need to pass the path to the original entrypoint via AV_ORIGINAL_ENTRYPOINT, 
# otherwise, /entrypoint.sh is used.
#
# Note: This script is designed to be POSIX sh compliant, to support a wide range 
# of shells inside 3rd party containers.

# Default values for environment variables (if not set)
: ${AV_APP_NAME:="container"}
: ${AV_ORIGINAL_ENTRYPOINT:="/entrypoint.sh"}

# Functions

# Validate the actual files referenced in _FILE envs
validate_file_envs() {

    # Skip file checks if AV_SKIP_FILE_CHECKS is set
    if [ -n "$AV_SKIP_FILE_CHECKS" ]; then
        echo "Skipping file checks for _FILE environment variables."
    else

        echo "Validating file paths in _FILE environment variables."

        total_env_vars=0
        file_env_vars=0

        # Iterate over all _FILE envs
        for env_var in $(env); do

            var_name=$(echo "$env_var" | cut -d '=' -f 1)
            var_value=$(echo "$env_var" | cut -d '=' -f 2-)

            total_env_vars=$((total_env_vars + 1))

            case $var_name in
                *_FILE)

                    if [ -z "$(echo "$var_value" | tr -d '[:space:]')" ]; then
                        echo "Error: $var_name is blank or whitespace only." >&2
                        return 1

                    elif [ ! -f "$var_value" ]; then
                        echo "Error: File in $var_name does not exist." >&2
                        return 1

                    elif [ ! -r "$var_value" ]; then
                        echo "Error: File in $var_name is not readable." >&2
                        return 1

                    elif ! grep -q '[^[:space:]]' "$var_value"; then
                        echo "Error: File in $var_name is empty or all whitespace." >&2
                        return 1
                    fi

                    file_env_vars=$((file_env_vars + 1))

                    ;;
            esac
        done

        echo "_FILE validation results: total env vars: $total_env_vars, _FILE env vars: $file_env_vars"
    fi
}

# Load secrets into environment variables if enabled with AV_LOAD_SECRET_ENVS
load_secret_envs() {

    # Check if secret env loading is enabled
    if [ -n "$AV_LOAD_SECRET_ENVS" ]; then

        echo "Loading secrets from designated _FILE env vars."

        total_env_vars=0
        file_env_vars=0
        exported_secrets=0        

        # Iterate over all _FILE envs
        for env_var in $(env); do

            var_name=$(echo "$env_var" | cut -d '=' -f 1)
            var_value=$(echo "$env_var" | cut -d '=' -f 2-)

            total_env_vars=$((total_env_vars + 1))

            case $var_name in
                *_FILE)

                    file_env_vars=$((file_env_vars + 1))

                    # Filter for PASSWORD and SECRET keywords
                    if echo "$var_name" | grep -q -e PASSWORD -e SECRET; then

                        # Check if file is non-empty
                        if [ -s "$var_value" ]; then

                            # Ensure file has a single non-blank line
                            line_count=$(sed -n '$=' "$var_value")
                            if [ "$line_count" -eq 1 ] && [ -n "$(sed -n '/^[ \t]*[^ \t]/p;q' "$var_value")" ]; then
                                
                                # Trim and export the content as a new variable
                                new_var_name="${var_name%_FILE}"
                                var_content_trimmed=$(sed 's/^[ \t]*//;s/[ \t]*$//' "$var_value")
                                export "$new_var_name=$var_content_trimmed"

                                echo "Secret $new_var_name loaded from $var_value"
                                exported_secrets=$((exported_secrets + 1))

                            else
                                echo "Error: '$var_name' must have 1 non-blank line." >&2
                                return 1
                            fi
                        else
                            echo "Error: '$var_name' is unreadable or empty." >&2
                            return 1
                        fi
                    fi
                    ;;
            esac
        done

        echo "_FILE secret loading results: total env vars: $total_env_vars, _FILE env vars: $file_env_vars, secret exports: $exported_secrets"

    else
        echo "Skipping secret envs loading."
    fi
}

# Execute custom script if AV_CUSTOM_SCRIPT is defined
exec_custom_script() {

    # Check if AV_CUSTOM_SCRIPT variable is set
    if [ -n "$AV_CUSTOM_SCRIPT" ]; then

        echo "Executing custom script: $AV_CUSTOM_SCRIPT"

        # Check if the custom script file exists and is executable
        if [ -f "$AV_CUSTOM_SCRIPT" ]; then
            if [ -x "$AV_CUSTOM_SCRIPT" ]; then

                # Execute the custom script
                "$AV_CUSTOM_SCRIPT"

            else
                echo "Error: Script '$AV_CUSTOM_SCRIPT' is not executable." >&2
                return 1
            fi
        else
            echo "Error: Script file '$AV_CUSTOM_SCRIPT' not found." >&2
            return 1
        fi

    else
        echo "No custom script specified."
    fi   
}

# Main
main() {

    # Validate file envs unless AV_SKIP_FILE_CHECKS is set
    validate_file_envs

    # Load secrets from files if AV_LOAD_SECRET_ENVS is set
    load_secret_envs

    # Execute custom script if AV_CUSTOM_SCRIPT is set
    exec_custom_script

    # Echo the app name, original entrypoint and passed arguments, if any
    echo "Starting ${AV_APP_NAME} using ${AV_ORIGINAL_ENTRYPOINT}"
    if [ $# -ne 0 ]; then
        echo "Arguments: $*"
    fi

    # Execute the original entrypoint with passed arguments
    exec "${AV_ORIGINAL_ENTRYPOINT}" "$@"
}

main "$@"
