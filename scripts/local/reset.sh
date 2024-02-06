#!/bin/sh
set -e

# Main
main() {

    # Define the directory of the script relative to the repository root
    SCRIPT_DIR="$(dirname "$(realpath "$0")")"

    # Navigate to the script directory
    cd "$SCRIPT_DIR"

    # Run Python scripts
    python cleanup.py
    python setup.py -a

    # Return to the original directory
    cd -

}

main "$@"
