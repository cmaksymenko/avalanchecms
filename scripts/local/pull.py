import argparse
import builtins
import json
import os
import subprocess
from utils.decorators import require_docker_running

# Redefine the print function to always flush by default
def print(*args, **kwargs):
    kwargs.setdefault('flush', True)
    return builtins.print(*args, **kwargs)

@require_docker_running
def pull_docker_images():
    
    # load Docker image list from config
    json_file_path = './config/docker_images.json'
    with open(json_file_path, 'r') as file:
        data = json.load(file)        
    images = data["images"]
    
    print("Pulling Docker images.")
    
    env = os.environ.copy()
    env["DOCKER_CLI_HINTS"] = "false" # disable CLI hints

    for image in images:
        
        print(f"Pulling image: {image}")
        try:
            
            # pull container image using Docker
            subprocess.run(["docker", "pull", image], check=True, env=env)
            
            print(f"Successfully pulled {image}")
            
        except subprocess.CalledProcessError as e:
            print(f"Failed to pull {image}. Error: {e}")

    print("Docker images pulled successfully.")

# Main
def main():
    pull_docker_images()
    
def parse_args():
    parser = argparse.ArgumentParser(description="Avalanche CMS local development image pull script.")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    main()