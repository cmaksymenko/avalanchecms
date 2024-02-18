# Avalanche CMS Local Stack start script

import argparse
import builtins
import os
import re
import shutil
import subprocess
import sys
import time
from functools import wraps

from setup import main as setup_main

# Redefine the print function to always flush by default
def print(*args, **kwargs):
    kwargs.setdefault('flush', True)
    return builtins.print(*args, **kwargs)

# Decorator that checks if the Docker engine is running, terminating the script if not
def require_docker_running(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        
        def is_docker_running():
            try:
                subprocess.run(["docker", "info"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return True
            except subprocess.CalledProcessError:
                return False

        if not is_docker_running():
            print("Docker engine is not running. Please start Docker engine and try again.")
            sys.exit(1)

        return func(*args, **kwargs)

    return wrapper

# Starts Avalanche CMS Docker containers
@require_docker_running
def start_docker_compose():

    try:

        script_dir = os.path.dirname(os.path.abspath(__file__))
        env_dir = os.path.join(script_dir, '../../environments/local')
        original_dir = os.getcwd()
        
        # Change directory to where the docker-compose file is located
        os.chdir(env_dir)

        process = subprocess.Popen(["docker", "compose", "up", "--remove-orphans"])

        time.sleep(1)

        if process.poll() is None:
            print("Docker environment started successfully.")
            process.wait()
        else:
            print("Failed to start Docker environment.")
            return

    except subprocess.CalledProcessError as e:
        print(f"Failed to start Docker environment: {e}")

    except FileNotFoundError:
        print("Docker Compose file not found. Are you in the correct directory?")

    except KeyboardInterrupt:
        print("Script interrupted. Gracefully shutting down.")

    finally:

        # Change back to the original directory
        os.chdir(original_dir)

# Main
def main():

    parser = argparse.ArgumentParser(description="Avalanche CMS local development start script.")
    parser.add_argument('-c', '--clean', action='store_true', help="Cleans and reinitializes the environment, deleting old data, volumes, containers and secrets.")    
    args = parser.parse_args()
    
    if args.clean:
        
        print("Cleaning and reinitializing environment.")
        try:
            setup_main(auto=True, clean=True)
        except Exception as e:
            print("Error during cleanup and reinitialization:", e)
            sys.exit(1)
            
    print("Starting.")   
    try:
        start_docker_compose()
    except KeyboardInterrupt:
        print("Script execution interrupted by user.")

if __name__ == "__main__":
    main()
