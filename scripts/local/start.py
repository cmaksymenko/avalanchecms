"""
Starts Avalanche CMS local Docker stack.

Optionally cleans data and updates Docker images. Runs containers and supports detached mode.

Usage:
- Default: starts containers as is.
- '-c': Clean start.
- '-d': Detached mode.
- '-ip': Pull latest images.
"""

import argparse
import os
import subprocess
import sys
import time
from pull import main as pull_main
from setup import main as setup_main
from utils.decorators import require_docker_running
from utils.output import print

@require_docker_running
def update_docker_images(image_pull=False):
    
    """
    Updates Docker images if 'image_pull' is True.
    """
    
    if image_pull:
        print("Updating images.")
        try:
            pull_main()
        except subprocess.CalledProcessError as e:
            print(f"Update error: {e}")
            sys.exit(1)            
        except Exception as e:
            print(f"Unexpected error: {e}")
            sys.exit(1)
    else:
        print("Update skipped.")

@require_docker_running
def start_docker_compose(detach=False):
    
    """
    Starts Docker containers for Avalanche CMS. Supports detached mode.
    """

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
            print("Started successfully.")
            process.wait()
        else:
            print("Start failed.")
            return

    except subprocess.CalledProcessError as e:
        print(f"Start failed: {e}")

    except FileNotFoundError:
        print("Compose file missing.")

    except KeyboardInterrupt:
        print("Interrupted. Shutting down.")
        
    finally:

        # Change back to the original directory
        os.chdir(original_dir)

def main():

    parser = argparse.ArgumentParser(description="Starts Avalanche CMS Docker stack.")
    parser.add_argument('-c', '--clean', action='store_true', help="Clean start, deletes data.")
    parser.add_argument('-d', '--detach', action='store_true', help="Detached mode.")
    parser.add_argument('-ip', '--image-pull', action='store_true', help="Updates Docker images.")

    args = parser.parse_args()
    
    if args.clean:
        print("Cleaning environment.")
        try:
            setup_main(auto=True, clean=True, image_pull=False)
        except Exception as e:
            print(f"Cleanup error: {e}")
            sys.exit(1)

    update_docker_images(image_pull=args.image_pull)
    
    print("Starting.")
    try:
        start_docker_compose(detach=args.detach)
    except KeyboardInterrupt:
        print("Interrupted by user.")
        sys.exit(0)

if __name__ == "__main__":
    main()
