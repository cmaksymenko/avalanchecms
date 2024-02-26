# Avalanche CMS Local Stack stop script

import argparse
import builtins
import os
import subprocess
import sys
import time
from functools import wraps

from setup import main as setup_main

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

# Stops Avalanche CMS Docker containers
@require_docker_running
def stop_docker_compose():

    try:

        script_dir = os.path.dirname(os.path.abspath(__file__))
        env_dir = os.path.join(script_dir, '../../environments/local')
        original_dir = os.getcwd()
        
        # Change directory to where the docker-compose file is located
        os.chdir(env_dir)

        subprocess.Popen(["docker", "compose", "down"])

    except subprocess.CalledProcessError as e:
        print(f"Failed to stop Docker environment: {e}")

    except FileNotFoundError:
        print("Docker Compose file not found. Are you in the correct directory?")

    except KeyboardInterrupt:
        print("Script interrupted.")

    finally:

        # Change back to the original directory
        os.chdir(original_dir)

# Main
def main():

    parser = argparse.ArgumentParser(description="Avalanche CMS local development stop script.")
    args = parser.parse_args()
    
    print("Stopping.")   
    try:
        stop_docker_compose()
    except KeyboardInterrupt:
        print("Script execution interrupted by user.")

if __name__ == "__main__":
    main()
