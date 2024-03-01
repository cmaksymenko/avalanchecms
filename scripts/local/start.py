# Avalanche CMS Local Stack start script

import argparse
import builtins
import os
import subprocess
import sys
import time
from pull import main as pull_main
from setup import main as setup_main
from utils.decorators import require_docker_running
from utils.output import print

@require_docker_running
def update_docker_images(keep_images=False):
    
    if not keep_images:
        
        print("Updating Docker images.")
        try:
            pull_main()
        except subprocess.CalledProcessError as e:
            print(f"Error updating Docker images: {e}. Check your Docker setup and network connection.")
            sys.exit(1)            
        except Exception as e:
            print(f"Unexpected error during Docker image update: {e}")
            sys.exit(1)
    else:
        print("Skipping Docker image update.")

# Starts Avalanche CMS Docker containers
@require_docker_running
def start_docker_compose(detach=False):

    try:

        script_dir = os.path.dirname(os.path.abspath(__file__))
        env_dir = os.path.join(script_dir, '../../environments/local')
        original_dir = os.getcwd()
        
        # Change directory to where the docker-compose file is located
        os.chdir(env_dir)
        
        command = ['docker-compose', 'up', '--remove-orphans']
        
        if detach:
            command.append('-d')

        process = subprocess.Popen(command)

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
    parser.add_argument('-c', '--clean', action='store_true', help="Cleans and reinitializes the stack, deleting old data, volumes, containers and secrets.")
    parser.add_argument('-d', '--detach', action='store_true', help="Runs the stack in detached mode.")
    parser.add_argument('-ki', '--keep-images', action='store_true', help="Doesnt pull the latest Docker images.")
    args = parser.parse_args()
    
    if args.clean:
        
        print("Cleaning and reinitializing environment.")
        try:
            setup_main(auto=True, clean=True, keep_images=args.keep_images)
            
        except Exception as e:
            print("Error during cleanup and reinitialization:", e)
            sys.exit(1)
    else:
        if not args.keep_images:
            update_docker_images(keep_images=args.keep_images)
            
    print("Starting.")
    try:
        start_docker_compose(detach=args.detach)
    except KeyboardInterrupt:
        print("Script execution interrupted by user.")
        sys.exit(0)

if __name__ == "__main__":
    main()
