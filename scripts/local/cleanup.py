"""
Avalanche CMS Local Cleanup Script

Cleans the local development environment for Avalanche CMS.

Features:
- Shuts down Docker compose stack (containers, networks)
- Removes specific Avalanche CMS volumes
- Optional: Keeps volumes and secrets based on flags

Command Line Options:
- -kv, --keep-volumes: Retains Docker volumes.
- -ks, --keep-secrets: Retains secrets and hashes in '.secrets'.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from utils.decorators import require_docker_running
from utils.output import print

@require_docker_running
def get_docker_volumes():
    
    """
    Fetches Docker volume names.

    Uses 'docker volume ls -q' for getting volume names. On success,
    returns a list of names. On failure (e.g., Docker not running), prints an
    error and returns an empty list.

    Returns:
        list: Docker volume names or empty list on failure.
    """

    result = subprocess.run(["docker", "volume", "ls", "-q"], capture_output=True, text=True)

    if result.returncode != 0:
        print("Error listing Docker volumes")
        return []  # return empty on failure

    # return list of volume names
    return result.stdout.splitlines()

@require_docker_running
def remove_volumes(volumes):
    
    """
    Removes specified Docker volumes.

    Iterates over a list of volume names, removing each one.
    Prints the status of each removal operation.

    Args:
        volumes (list): List of volume names to remove.
    """

    for volume in volumes:
        
        print(f"Removing volume {volume}...")
        
        # remove volume
        subprocess.run(["docker", "volume", "rm", volume], check=True)
        
        print(f"Removed volume {volume}")

def purge_avalanchecms_volumes():
    
    """
    Purges all Avalanche CMS Docker volumes.

    Retrieves all Docker volumes and filters volumes matching
    'avalanchecms_.*' regex. If matching volumes are found, they are removed.
    If no volumes match, prints a message and exits.
    """
    
    print("Removing Docker volumes.")

    volumes = get_docker_volumes() # Get all Docker volumes
    pattern = re.compile('avalanchecms_.*') # regex

    # filter volumes matching the regex
    filtered_volumes = [volume for volume in volumes if pattern.match(volume)]

    if not filtered_volumes:
        print("No volumes match the pattern: avalanchecms_.*")
        return

    remove_volumes(filtered_volumes)
    
    print("Docker volumes removed.")

@require_docker_running
def purge_docker_environment(keep_volumes=False):
    
    """
    Stops/removes Avalanche CMS Docker containers and purges volumes.

    Args:
        keep_volumes (bool): If True, skips volume purging. Default is False.
    """
    
    try:
        
        print("Stopping/removing Docker containers and networks.")
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        env_dir = os.path.join(script_dir, '../../environments/local')
        original_dir = os.getcwd()

        os.chdir(env_dir) # change to docker compose dir

        # stop/remove containers and networks
        subprocess.run(["docker", "compose", "down"], check=True)
        
        print("Docker containers and networks stopped/removed.")

        if keep_volumes:
            print("Volume purge skipped.")
        else:
            purge_avalanchecms_volumes()  # purge volumes by default

    except subprocess.CalledProcessError as e:
        print(f"Failed to purge Docker environment: {e}")
        sys.exit(1)

    finally:
        os.chdir(original_dir) # return to original dir

def remove_secret_folder():
    
    """
    Removes the '.secrets' directory from the root if it exists.
    """

    script_dir = os.path.dirname(os.path.abspath(__file__))
    secrets_dir = os.path.join(script_dir, '../../.secrets')
   
    try:
        shutil.rmtree(secrets_dir) # remove the .secrets dir
        print("/.secrets folder removed successfully.")
    except FileNotFoundError:
        # .secrets dir does not exist
        print("/.secrets folder does not exist or has already been removed.")

def purge_secrets(keep_secrets=False):
    
    """
    Purges Avalanche CMS secrets, skippable.
    
    Args:
        keep_secrets (bool): If True, skips the purge operation. Default is False.
    """

    if keep_secrets:
        print("Secret removal skipped.")
    else:
        print("Removing secrets.")
        remove_secret_folder()  # remove .secrets directory
        print("Secrets removed.")


def main(keep_volumes=False, keep_secrets=False):
    
    """
    Main cleanup function.

    Cleans the Docker environment and purges Avalanche CMS secrets.

    Args:
        keep_volumes (bool): If True, skips volume purging. Default is False.
        keep_secrets (bool): If True, skips secret purging. Default is False.
    """
    
    print("Cleaning up local development environment.")

    purge_docker_environment(keep_volumes)
    purge_secrets(keep_secrets)

    print("Local development environment cleanup is complete.")


def parse_args():
    parser = argparse.ArgumentParser(description="Avalanche CMS Local Cleanup Script.")
    parser.add_argument('-kv', '--keep-volumes', action='store_true', help='Doesnt remove Docker volumes')
    parser.add_argument('-ks', '--keep-secrets', action='store_true', help='Doesnt remove secrets and hashes in /.secrets')
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    main(keep_volumes=args.keep_volumes, keep_secrets=args.keep_secrets)