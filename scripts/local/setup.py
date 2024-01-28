# main setup script

import os
import random
import string
from pathlib import Path
import argparse

# Low-risk characters for secure passwords: minimal escaping, high compatibility.
SECRET_LOW_RISK_SPECIAL_CHARS = "*+-=^_~"

# Pool of characters for generating secrets: includes letters, digits, and low-risk special characters.
SECRET_CHAR_POOL = string.ascii_letters + string.digits + SECRET_LOW_RISK_SPECIAL_CHARS

# Default length for generated secrets
SECRET_DEFAULT_LEN = 20

# Secrets and filenames
secrets = [
    {"name": "Postgres Admin User", "file": "postgres-admin-user-secret.env"},
    {"name": "PgAdmin Admin User", "file": "pgadmin-admin-user-secret.env"},
    {"name": "Postgres Avalanche CMS Database User", "file": "postgres-avalanchecms-db-user-secret.env"},
    {"name": "Postgres Keycloak Database User", "file": "postgres-keycloak-db-user-secret.env"},
    {"name": "Keycloak Admin User", "file": "keycloak-admin-user-secret.env"}
]

def find_project_root(current_file):
    # Assuming the script is in 'scripts/dev-setup'
    # Adjust the number of os.path.dirname calls based on actual script location
    return os.path.dirname(os.path.dirname(os.path.dirname(current_file)))

def generate_random_password(length=SECRET_DEFAULT_LEN):
    return ''.join(random.choice(SECRET_CHAR_POOL) for i in range(length))

def prompt_for_password(description, auto=False):
    if auto:
        return generate_random_password()
    else:
        choice = input(f"Do you want to generate a random password for {description}? [Y/n]: ").strip().lower()
        if choice in ['n', 'no']:
            return input(f"Enter your desired password for {description}: ").strip()
        else:
            return generate_random_password()

def create_secret_file(path, content):
    if not os.path.exists(path):
        with open(path, 'w') as file:
            file.write(content)
        print(f"Created secret file: {path}")
    else:
        print(f"Secret file already exists: {path}, skipping...")

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
        secret_value = prompt_for_password(secret["name"], args.auto)
        create_secret_file(secret_file, secret_value)

    print("Local development environment setup for Avalanche CMS is complete.")

    if not args.auto:
        print("Tip: You can use '--auto' next time for automatic mode.")

if __name__ == "__main__":
    main()