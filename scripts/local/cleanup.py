# Avalanche CMS Local Stack cleanup script
#
# This script cleans up the local development environment for Avalanche CMS. It does the following:
# - It shuts down the Docker compose stack with docker compose down, removing containers and networks
# - It removes Avalanche CMS volumes specifically through regex matching (avalanchecms_.*), skippable

import argparse
import builtins
import os
import re
import shutil
import subprocess
import sys
from utils.decorators import require_docker_running

# Redefine the print function to always flush by default
def print(*args, **kwargs):
    kwargs.setdefault('flush', True)
    return builtins.print(*args, **kwargs)

# Get all Docker volumes, returning them as a list
# On failure, an empty list is returned
@require_docker_running
def get_docker_volumes():

    result = subprocess.run(["docker", "volume", "ls", "-q"], capture_output=True, text=True)

    if result.returncode != 0:
        print("Error listing Docker volumes")
        return []

    volumes = result.stdout.splitlines()
    return volumes

# Removes each Docker volume of a list of volume names
@require_docker_running
def remove_volumes(volumes):
    for volume in volumes:
        print(f"Removing volume {volume}...")
        subprocess.run(["docker", "volume", "rm", volume], check=True)
        print(f"Removed volume {volume}")

# Retrieves all Avalanche CMS Docker volumes and removes them
def purge_avalanchecms_volumes():

    volumes = get_docker_volumes()

    pattern_string = 'avalanchecms_.*'
    pattern = re.compile(pattern_string)

    filtered_volumes = [volume for volume in volumes if pattern.match(volume)]

    if not filtered_volumes:
        print(f"No volumes match the pattern: {pattern_string}")
        return

    remove_volumes(filtered_volumes)

# Stops and removes Avalanche CMS Docker containers, and purges volumes, too (skippable)
@require_docker_running
def purge_docker_environment(keep_volumes=False):

    try:

        script_dir = os.path.dirname(os.path.abspath(__file__))
        env_dir = os.path.join(script_dir, '../../environments/local')
        original_dir = os.getcwd()
        
        # Change directory to where the docker-compose file is located
        os.chdir(env_dir)

        # Stop and remove all containers and networks
        subprocess.run(["docker", "compose", "down"], check=True)

        if keep_volumes:
            print("Volume purge skipped.")
        else:
            purge_avalanchecms_volumes()

        print("Docker environment purged successfully.")

    except subprocess.CalledProcessError as e:
        print(f"Failed to purge Docker environment: {e}")
        sys.exit(1)

    except FileNotFoundError:
        print("Docker Compose file not found. Are you in the correct directory?")
        sys.exit(1)

    finally:

        # Change back to the original directory
        os.chdir(original_dir)

# Removes '.secrets' folder in root directory, if it exists 
def remove_secret_folder():

    script_dir = os.path.dirname(os.path.abspath(__file__))
    secrets_dir = os.path.join(script_dir, '../../.secrets')
   
    try:
        shutil.rmtree(secrets_dir)
        print("/.secret folder removed successfully.")
    except FileNotFoundError:
        print("/.secret folder does not exist or has already been removed.")

# Purges Avalanche CMS secrets (skippable)
def purge_secrets(keep_secrets=False):

    if keep_secrets:
        print("Secret purge skipped.")
    else:
        remove_secret_folder()
        print("Secrets purged successfully.")

# Main
def main(keep_volumes=False, keep_secrets=False):

    purge_docker_environment(keep_volumes)
    purge_secrets(keep_secrets)

    print("Local development environment cleanup is complete.")

def parse_args():
    parser = argparse.ArgumentParser(description="Avalanche CMS local development cleanup script.")
    parser.add_argument('-kv', '--keep-volumes', action='store_true', help='Doesnt remove Docker volumes')
    parser.add_argument('-ks', '--keep-secrets', action='store_true', help='Doesnt remove secrets and hashes in /.secrets')
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    main(keep_volumes=args.keep_volumes, keep_secrets=args.keep_secrets)