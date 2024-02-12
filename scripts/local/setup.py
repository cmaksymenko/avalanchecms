# Avalanche CMS Local Stack setup script
#
# Script for setting up local dev environment for Avalanche CMS:
# - User inputs or auto-generates secrets for stack components.
# - Generates .env files in project root's '.secrets' directory (plaintext secrets)
# - Creates .hash files for user secrets, aiding KeyCloak prepopulation.
# - Automated secret creation via '-a/--auto' and cleanup via '-c/--clean'.
# - Assumes 'scripts/local' location for project root determination.


import argparse
import base64
import hashlib
import os
import random
import string
import sys
from pathlib import Path

from cleanup import main as cleanup_main


class SecretDefinition:
    def __init__(self, name, base_filename, generate_hash=False):
        self.name = name
        self.base_filename = base_filename
        self.generate_hash = generate_hash

# Special characters for secure passwords
SECRET_SPECIAL_CHARS = "!@#$%^&*()-_=+[]{};:,.<>/?|"

# Pool of characters for generating secrets: includes letters, digits, and special characters
SECRET_CHAR_POOL = string.ascii_letters + string.digits + SECRET_SPECIAL_CHARS

# Default length for generated secrets
SECRET_DEFAULT_LEN = 22

secret_data = [
    # Infrastructure components admin users
    ("Postgres Admin User", "postgres-admin-user-secret"),
    ("PgAdmin Admin User", "pgadmin-admin-user-secret"),
    ("Keycloak Admin User", "keycloak-admin-user-secret"),

    # Database connection users
    ("Postgres Avalanche CMS Database User", "postgres-avalanchecms-db-user-secret"),
    ("Postgres Keycloak Database User", "postgres-keycloak-db-user-secret"),

    # Avalanche CMS Keycloak users (with generate_hash=True)
    ("Avalanche CMS Admin User", "avalanche-cms-adminuser-secret", True),
    ("Avalanche CMS App User 1", "avalanche-cms-appuser1-secret", True),
    ("Avalanche CMS App User 2", "avalanche-cms-appuser2-secret", True),
    ("Avalanche CMS Combined User", "avalanche-cms-combineduser-secret", True),
    ("Avalanche CMS No Group User", "avalanche-cms-nogroupuser-secret", True)
]

secrets = [SecretDefinition(*data) for data in secret_data]


# Finds the root directory of the project
#
# Args: current_file (str): The file path of the current script
# Returns: root directory path of the project
#
def find_project_root(current_file):
    # Assuming the script is in 'scripts/local'
    # Adjust the number of os.path.dirname calls based on actual script location
    return os.path.dirname(os.path.dirname(os.path.dirname(current_file)))


# Hashes a secret with PBKDF2 for Keycloak configuration
#
# Args:
#   secret: Secret to hash
#   salt_length: Salt length in bytes (default: 16)
#   iterations: Hashing iterations (default: 27500)
#
# Returns: dictionary with algorithm, iterations, salt, and hash
#
def hash_secret(secret, salt_length=16, iterations=27500):

    if not isinstance(secret, str) or not secret:
        raise ValueError("Invalid secret provided.")

    try:

        salt = os.urandom(salt_length) # generate salt

        # Hash using PBKDF2
        hashed_secret = hashlib.pbkdf2_hmac('sha256', secret.encode(), salt, iterations)

        # Encode
        encoded_hash = base64.b64encode(hashed_secret).decode()
        encoded_salt = base64.b64encode(salt).decode()

        return {
            "algorithm": "pbkdf2-sha256",
            "iterations": iterations,
            "salt": encoded_salt,
            "hash": encoded_hash
        }

    except Exception as e:
        raise RuntimeError(f"Error during secret hashing: {e}")


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
        user_input = input(f"Secret for {description} [Enter=random]: ").strip()
        if user_input: # Will be False for empty, whitespace-only strings, or return key
            return user_input

    print(f"Generating secret for {description}.")
    return generate_random_password()


# Creates a secret file if it doesn't already exist
#
# Args:
#   path: The file path where the secret should be saved
#   secret: The plaintext secret to write in the file
#
# Note: If the file already exists, creation is skipped
#
def create_secret_file(path, secret):
    if not os.path.exists(path):
        with open(path, 'w') as file:
            file.write(secret)
        print(f"Secret file created: {path}")
    else:
        print(f"Existing secret file: {path}, skipped")


# Creates a hash file if it doesn't already exist
#
# Args:
#   path: The file path where the secret hash should be saved
#   secret: The plaintext secret, for which the hash will be generated and written to file
#
# Note: If the file already exists, creation is skipped
#
def create_hash_file(path, secret):

    if not os.path.exists(path):

        hashed_data = hash_secret(secret)
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, 'w') as file:
            for key, value in hashed_data.items():
                file.write(f"{key.upper()}={value}\n")

        print(f"Hash file created: {path}")
    else:
        print(f"Existing hash file: {path}, skipped")


# Main
def main():

    parser = argparse.ArgumentParser(description="Avalanche CMS local setup.")
    parser.add_argument('-a', '--auto', action='store_true', help='Automates setup with defaults.')
    parser.add_argument('-p', '--password', type=str, help="Set a uniform password (e.g., -p 'Your$ecret!'). Use single quotes for special characters.")
    parser.add_argument('-c', '--clean', action='store_true', help="Clean environment before setup.")
    args = parser.parse_args()

    if not args.password:
        print(f"{'Auto' if args.auto else 'Manual'} mode.")

    if args.password is not None and args.password.strip():
        print("Common password set.")
    else:
        if args.password is not None:
            print("Error: Invalid password.")
            sys.exit(1)

    if args.clean:
        print("Cleaning environment.")
        try:
            cleanup_main()
        except Exception as e:
            print("Error during cleanup:", e)
            sys.exit(1)

    project_root = find_project_root(__file__)
    secrets_path = os.path.join(project_root, '.secrets')

    if not os.path.exists(secrets_path):
        os.makedirs(secrets_path)

    # Process each secret and create corresponding env file
    for secret in secrets:

        # Construct file paths for secret (and hash) files
        secret_file = os.path.join(secrets_path, secret.base_filename + ".env")
        secret_file_hash = os.path.join(secrets_path, "hashes", secret.base_filename + ".hash") if secret.generate_hash else None

        # Choose password: use provided, prompt, or auto-generate
        secret_value = (args.password.strip() if args.password and args.password.strip()
                        else prompt_for_secret(secret.name, args.auto))

        # Create secret (and hash) files on disk
        create_secret_file(secret_file, secret_value)
        if secret_file_hash is not None:
            create_hash_file(secret_file_hash, secret_value)

    print("Avalanche CMS setup complete.")

    # Suggest auto mode if not used and no password provided
    if not args.auto and not args.password:
        print("Tip: Use '--auto' for automatic setup.")

if __name__ == "__main__":
    main()