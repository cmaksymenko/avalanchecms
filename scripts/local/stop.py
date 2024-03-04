"""
Stops Avalanche CMS local Docker stack.

Safely shuts down Docker containers for Avalanche CMS. Checks for Docker,
handles errors, and supports graceful interruption.
"""

import argparse
import os
import subprocess
from utils.decorators import require_docker_running
from utils.output import print

# Stops Avalanche CMS Docker containers
@require_docker_running
def stop_docker_compose():
    
    """
    Stops local Avalanche CMS Docker containers.
    """
    
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        env_dir = os.path.join(script_dir, '../../environments/local')
        original_dir = os.getcwd()
        
        # Change directory to where the docker-compose file is located
        os.chdir(env_dir)

        # Use subprocess.run to wait for the command to complete
        subprocess.run(["docker", "compose", "down"], check=True)

    except subprocess.CalledProcessError as e:
        print(f"Stop failed: {e}")
    except FileNotFoundError:
        print("Compose file missing.")
    except KeyboardInterrupt:
        print("Interrupted.")
    finally:
        # Change back to the original directory
        os.chdir(original_dir)
        
# Main
def main():

    parser = argparse.ArgumentParser(description="Avalanche CMS local development stack stop.")
    args = parser.parse_args()
    
    print("Stopping.") 
    try:
        stop_docker_compose()
        print("Stopped.") 
    except KeyboardInterrupt:
        print("Interrupted.")

if __name__ == "__main__":
    main()
