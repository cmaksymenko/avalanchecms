# Avalanche CMS Local Stack setup script
#
# This script sets up a local development environment for Avalanche CMS. It includes functionalities to:
# - Prompt the user to either enter a secret or generate a strong secure secret automatically, for all stack components
# - Create secret files in a designated '.secrets' directory within the project's root folder
# - Offer an automated mode for generating all secrets without user input, triggered by the '-a/--auto' argument
# - The script assumes its location in 'scripts/local' and calculates the project root from there

import os
import random
import string
from pathlib import Path
import argparse

# Special characters for secure passwords
SECRET_SPECIAL_CHARS = "!@#$%^&*()-_=+[]{};:,.<>/?|"

# Pool of characters for generating secrets: includes letters, digits, and low-risk special characters.
SECRET_CHAR_POOL = string.ascii_letters + string.digits + SECRET_SPECIAL_CHARS

# Default length for generated secrets
SECRET_DEFAULT_LEN = 22

# Secrets and filenames
secrets = [
    {"name": "Postgres Admin User", "file": "postgres-admin-user-secret.env"},
    {"name": "PgAdmin Admin User", "file": "pgadmin-admin-user-secret.env"},
    {"name": "Postgres Avalanche CMS Database User", "file": "postgres-avalanchecms-db-user-secret.env"},
    {"name": "Postgres Keycloak Database User", "file": "postgres-keycloak-db-user-secret.env"},
    {"name": "Keycloak Admin User", "file": "keycloak-admin-user-secret.env"}
]

# Finds the root directory of the project
#
# Args: current_file (str): The file path of the current script
# Returns: root directory path of the project
#
def find_project_root(current_file):
    # Assuming the script is in 'scripts/local'
    # Adjust the number of os.path.dirname calls based on actual script location
    return os.path.dirname(os.path.dirname(os.path.dirname(current_file)))

# Generates a random password
#
# Args: length (int, optional): The length of the password to be generated
# Returns: random password string
#
def generate_random_password(length=SECRET_DEFAULT_LEN):
    return ''.join(random.choice(SECRET_CHAR_POOL) for i in range(length))

# Prompts for a secret or generates one automatically
#
# Args:
#   description (str): Description of the secret
#   auto (bool, optional): If True, generates a secret automatically. Defaults to False.
#
# Returns: User-provided or randomly generated secret
#
def prompt_for_secret(description, auto=False):
    if not auto:
        user_input = input(f"Enter secret for {description} (press enter for random): ").strip()
        if user_input: # This will be False for empty or all-whitespace strings, or if the user pressed return
            return user_input

    print(f"Generating a random secret for {description}...")
    return generate_random_password()

# Creates a secret file if it doesn't already exist
#
# Args:
#   path (str): The file path where the secret should be saved
#   content (str): The content to write in the secret file
#
# Note: If the file already exists, creation is skipped
#
def create_secret_file(path, content):
    if not os.path.exists(path):
        with open(path, 'w') as file:
            file.write(content)
        print(f"Created secret file: {path}")
    else:
        print(f"Secret file already exists: {path}, skipping...")

# Main
def main():

    parser = argparse.ArgumentParser(description="Avalanche CMS setup script for local development.")
    parser.add_argument('-a', '--auto', action='store_true', help='Enable automated mode with default settings.')
    args = parser.parse_args()

    print(f"{'Automated' if args.auto else 'Interactive'} mode enabled.")

    project_root = find_project_root(__file__)
    secrets_path = os.path.join(project_root, '.secrets')

    if not os.path.exists(secrets_path):
        os.makedirs(secrets_path)

    # Loop through each secret, prompt and create env file
    for secret in secrets:
        secret_file = os.path.join(secrets_path, secret["file"])
        secret_value = prompt_for_secret(secret["name"], args.auto)
        create_secret_file(secret_file, secret_value)

    print("Local development environment setup for Avalanche CMS is complete.")

    if not args.auto:
        print("Tip: You can use '--auto' next time for automatic mode.")

if __name__ == "__main__":
    main()