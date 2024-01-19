# main setup script

import os
import random
import string
from pathlib import Path

def find_project_root(current_file):
    # Assuming the script is in 'scripts/dev-setup'
    # Adjust the number of os.path.dirname calls based on actual script location
    return os.path.dirname(os.path.dirname(os.path.dirname(current_file)))

def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

def prompt_for_password(description):
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

    project_root = find_project_root(__file__)
    secrets_path = os.path.join(project_root, '.secrets')

    db_password_file = os.path.join(secrets_path, 'postgres-secret.env')
    pgadmin_password_file = os.path.join(secrets_path, 'pgadmin-secret.env')

    if not os.path.exists(secrets_path):
        os.makedirs(secrets_path)
    
    db_password = prompt_for_password("PostgreSQL")
    pgadmin_password = prompt_for_password("PgAdmin")

    create_secret_file(db_password_file, db_password)
    create_secret_file(pgadmin_password_file, pgadmin_password)

    print("Local development environment setup for Avalanche CMS is complete.")

if __name__ == "__main__":
    main()