"""
Sets up the Avalanche CMS local dev environment.

Supports interactive or automated setup for secrets, Docker image updates,
and environment reset with options for preserving volumes and secrets.

Options:
- -a, --auto: Automated setup with generated passwords.
- -c, --clean: Full reset. Can keep volumes (-kv) and secrets (-ks).
- -s, --salt-base: Set salt base (debug).
- -p, --password: Specify a password (debug)
- -ip, --image-pull: Update Docker images.
"""

import argparse
import base64
import hashlib
import json
import os
import random
import string
import sys
from cleanup import main as cleanup_main
from pull import main as pull_main
from utils.decorators import require_docker_running
from utils.output import print

# Special characters for secure passwords
SECRET_SPECIAL_CHARS = "!@#$%^&*()-_=+[]{};:,.<>/?|"

# Pool of characters for generating secrets: includes letters, digits, and special characters
SECRET_CHAR_POOL = string.ascii_letters + string.digits + SECRET_SPECIAL_CHARS

def read_credentials():
    
    """
    Reads and validates credentials from a config, requiring 'name', 
    'base_filename', and 'username' if 'in_pgpass_file' is true.

    Returns validated credentials or exits on errors.
    """
    
    file_path = './config/credentials.json'
    
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            
            for item in data:
                
                # validate mandatory fields.
                if 'name' not in item or 'base_filename' not in item:
                    sys.exit(f"Error: Missing 'name'/'base_filename' in item: {item}")
                
                # validate 'username' for items marked for inclusion in pgpass file
                if item.get('in_pgpass_file', False) and 'username' not in item:
                    sys.exit("Error: Missing 'username' when 'in_pgpass_file' is true.")
            
            return data
        
    except FileNotFoundError:
        sys.exit(f"File not found: {file_path}")
    except json.JSONDecodeError:
        sys.exit(f"Error decoding JSON from the file: {file_path}")

def find_project_root(current_file):
    
    """
    Finds project root directory based on script's file path.

    Args:
        current_file (str): Script file path.

    Returns:
        Root directory path.
    """ 
    
    # Assuming the script is in 'scripts/local'
    # Adjust the number of os.path.dirname calls based on actual script location
    return os.path.dirname(os.path.dirname(os.path.dirname(current_file)))

def generate_deterministic_salt(base_string, salt_length=16):
    
    """
    Generates a deterministic salt using SHA-256 hash of 'base_string'.

    Args:
        base_string (str): Input string for hashing.
        salt_length (int): Desired salt length, 1-32, default 16.

    Returns salt or raises ValueError on invalid input.
    """
    
    if base_string is None:
        raise ValueError("base_string cannot be None")

    # Strip whitespace from the string
    stripped_string = base_string.strip()

    if len(stripped_string) == 0:
        raise ValueError("base_string cannot be empty or only whitespace")

    if not 0 < salt_length <= 32:
        raise ValueError("salt_length must be between 1 and 32 for SHA-256")

    hashed = hashlib.sha256(stripped_string.encode()).digest()
    return hashed[:salt_length]

def hash_secret(secret, salt_length=16, iterations=27500, salt_base=None):
    
    """
    Hashes a secret using PBKDF2, supports deterministic salts for debugging.

    Args:
        secret (str): Secret to hash.
        salt_length, iterations (int, optional): Salt length and iterations.
        salt_base (str, optional): Debugging use only.

    Returns hash details or raises errors on failure.
    """

    if not isinstance(secret, str) or not secret:
        raise ValueError("Invalid secret provided.")

    try:

        salt = os.urandom(salt_length) # generate salt
        
        if salt_base:
            salt = generate_deterministic_salt(salt_base, salt_length)
        else:
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

def write_pgpass_file(folder, hostname, port=5432, triplets=None):
    
    """
    Writes .pgpass for PostgreSQL connections in specified folder.
    Automatically escapes colons and backslashes for pgpass formatting.

    Args:
        folder (str): Target directory.
        hostname (str), port (int), database (str): Connection details.
        triplets (list of triplets): Database, Username, Password triplets.

    Returns path to .pgpass or raises ValueError on missing info.
    """

    # validate required parameters
    if not all([hostname, triplets]):
        raise ValueError("Hostname and triplets cannot be None or empty.")

    pgpass_file_path = os.path.join(folder, '.pgpass')

    # create the file
    with open(pgpass_file_path, 'w', newline='\n') as file:
        for database, username, password in triplets:
            
            # escape backslash first to avoid escaping already escaped colons
            escaped_password = password.replace("\\", "\\\\")  # replace \ with \\
            escaped_password = escaped_password.replace(":", "\\:")  # replace : with \:
            
            # format connection string for each database-username-password triplet
            connection_string = f"{hostname}:{port}:{database}:{username}:{escaped_password}\n"
            
            file.write(connection_string)

    # secure the .pgpass file by setting its file permission to 0600 (read/write for owner only)
    os.chmod(pgpass_file_path, 0o600)
    
    return pgpass_file_path

def generate_random_password(length=22):
    
    """
    Generates a random password of specified length. Default length is 22.
    """
    
    return ''.join(random.choice(SECRET_CHAR_POOL) for i in range(length))

def prompt_for_secret(description, auto=False):
    
    """
    Prompts for a secret or generates one automatically based on 'auto' flag.
    Triggers auto-generation on empty input. Description provided for prompt.
    """
    
    if not auto:
        user_input = input(f"Secret for {description} [Enter=random]: ").strip()
        if user_input: # Will be False for empty, whitespace-only strings, or return key
            return user_input

    print(f"Generating secret for {description}.")
    
    return generate_random_password()

def create_secret_file(path, secret):
    
    """
    Creates a secret file at 'path' if not existing, without overwriting.
    """

    if not os.path.exists(path):
        with open(path, 'w', newline='\n') as file:
            file.write(secret)
        print(f"Secret file created: {path}")
    else:
        print(f"Existing secret file: {path}, skipped")

def create_hash_file(path, secret, salt_base=None):
    
    """
    Creates a hash file from a secret at 'path', with optional 'salt_base'.
    Skips if file exists.
    """

    if not os.path.exists(path):

        hashed_data = hash_secret(secret=secret, salt_base=salt_base)
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, 'w', newline='\n') as file:
            for key, value in hashed_data.items():
                file.write(f"{key.upper()}={value}\n")

        print(f"Hash file created: {path}")
    else:
        print(f"Existing hash file: {path}, skipped")       

def clean_environment(clean=False, keep_volumes=None, keep_secrets=None):
    
    """
    Cleans up the environment by delegating to the cleanup.py script.
    """
    
    if clean:
        print("Cleaning environment.")
        try:

            cleanup_main(keep_volumes, keep_secrets)

        except Exception as e:
            print("Error during cleanup:", e)
            sys.exit(1)

def create_secrets(keep_secrets=None, auto=False, password=None, salt_base=None):
    
    """
    Creates secrets and hash files, supporting auto-generation, common password,
    and interactive prompting. Optionally skips creation.
    """
    
    if password is not None and password.strip():
        print("Common password set.")
    else:
        if password is not None:
            print("Error: Invalid password.")
            sys.exit(1)
    
    if not keep_secrets:

        project_root = find_project_root(__file__)
        secrets_path = os.path.join(project_root, '.secrets')
        if not os.path.exists(secrets_path):
            os.makedirs(secrets_path)
        
        credentials = read_credentials()  # load credentials config

        for entry in credentials:
            
            # prepare target paths for secrets and hashes
            name, base_filename = entry.get("name"), entry.get("base_filename")
            secret_file = os.path.join(secrets_path, f"{base_filename}.env")
            generate_hash = entry.get("generate_hash", False)
            secret_file_hash = None
            if generate_hash:
                secret_file_hash = os.path.join(secrets_path, "hashes", f"{base_filename}.hash")
                entry["secret_file_hash"] = secret_file_hash

            # read/generate secret value
            secret_value = password.strip() if password and password.strip() else prompt_for_secret(name, auto)
            entry["secret_value"] = secret_value

            # write to file
            create_secret_file(secret_file, secret_value)
            if generate_hash:
                create_hash_file(secret_file_hash, secret_value, salt_base)
        
        # generate .pgpass file
        triplets = []
        for entry in credentials:
            if entry.get("in_pgpass_file", False):
                database = entry.get("database", "*") if entry.get("database", "").strip() else "*"
                triplets.append((database, entry["username"], entry["secret_value"]))

        if triplets:          
            pgpass_file_path = write_pgpass_file(secrets_path, "postgres", 5432, triplets)
            print(f".pgpass created: {pgpass_file_path}, credentials: {len(triplets)}")

        else:
            print("No applicable secrets, skipping .pgpass creation.")
            
    else:
        print("Skipping secret creation for cleanup.")

def update_docker_images(image_pull=False):
    
    """
    Pulls latest Docker images if opted in.
    """
    
    if image_pull:
        
        print("Updating Docker images.")
        try:
            
            pull_main()  # pull images
            
        except Exception as e:
            print(f"Error during Docker image update: {e}")
            sys.exit(1)
    else:
        print("Skipping Docker image update.")

def main(auto=False, password=None, clean=False, keep_volumes=None, keep_secrets=None, salt_base=None, image_pull=False):
    
    """
    Main setup function for Avalanche CMS. Configures environment based on
    provided arguments for automation, cleaning, volume and secret retention,
    salt base customization, and Docker image updates.
    """
    
    print("Setting up Avalanche CMS Local Development Environment.")

    if not password:
        print(f"{'Auto' if auto else 'Manual'} mode.")

    clean_environment(clean=clean, keep_volumes=keep_volumes, keep_secrets=keep_secrets)
    create_secrets(keep_secrets=keep_secrets, auto=auto, password=password, salt_base=salt_base)
    update_docker_images(image_pull=image_pull)
        
    print("Avalanche CMS Local Development Environment setted up.")

    # Suggest auto mode if not used and no password provided
    if not auto and not password:
        print("Tip: Use '--auto' for automatic setup.")             

def parse_args():

    parser = argparse.ArgumentParser(description="Setup script for Avalanche CMS.")
    parser.add_argument('-a', '--auto', action='store_true', help='Enables automatic setup.')
    parser.add_argument('-p', '--password', type=str, help="Sets a custom password.")
    parser.add_argument('-c', '--clean', action='store_true', help="Fully resets the environment.")
    parser.add_argument('-s', '--salt-base', type=str, help="Custom salt base for hashing.")
    parser.add_argument('-ip', '--image-pull', action='store_true', help="Updates Docker images.")

    args, remaining_argv = parser.parse_known_args()
    
    purge_args = None
    if args.clean:
        
        purge_parser = argparse.ArgumentParser()
        purge_parser.add_argument('-kv', '--keep-volumes', action='store_true', help='Keeps Docker volumes')
        purge_parser.add_argument('-ks', '--keep-secrets', action='store_true', help='Keeps secrets in /.secrets')
        purge_args = purge_parser.parse_args(remaining_argv)
        
    return args, remaining_argv, purge_args

if __name__ == "__main__":
    
    args, remaining_argv, purge_args = parse_args()
    
    keep_volumes = purge_args.keep_volumes if args.clean else None
    keep_secrets = purge_args.keep_secrets if args.clean else None
    
    main(auto=args.auto, password=args.password, clean=args.clean, 
         keep_volumes=keep_volumes, keep_secrets=keep_secrets, 
         salt_base=args.salt_base, image_pull=args.image_pull)