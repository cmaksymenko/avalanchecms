"""
Pulls Docker images for Avalanche CMS local dev setup.

Automates image pulling to ensure consistency. Reads image list from
./config/docker_images.json.

Usage: Run without arguments.
"""

import argparse
import json
import os
import subprocess
from utils.decorators import require_docker_running
from utils.output import print

@require_docker_running
def pull_docker_images():
    
    """
    Pulls Docker images for Avalanche CMS from './config/docker_images.json'.
    """
    
    json_file_path = './config/docker_images.json'
    with open(json_file_path, 'r') as file:
        images = json.load(file)["images"]
    
    print("Pulling Docker images.")
    
    env = os.environ.copy()
    env["DOCKER_CLI_HINTS"] = "false" # disable hints for cleaner output

    for image in images:
        print(f"Pulling image: {image}")
        try:
            subprocess.run(["docker", "pull", image], check=True, env=env)
            print(f"Successfully pulled {image}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to pull {image}. Error: {e}")

    print("Docker images pulled successfully.")

def main():  
    pull_docker_images()
    
def parse_args():
    parser = argparse.ArgumentParser(description="Avalanche CMS Local Docker Image Pull.")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    main()