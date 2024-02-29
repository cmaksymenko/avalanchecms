# Avalanche CMS Local Stack stop script

import argparse
import os
import subprocess
from utils.decorators import require_docker_running

# Stops Avalanche CMS Docker containers
@require_docker_running
def stop_docker_compose():
    
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        env_dir = os.path.join(script_dir, '../../environments/local')
        original_dir = os.getcwd()
        
        # Change directory to where the docker-compose file is located
        os.chdir(env_dir)

        # Use subprocess.run to wait for the command to complete
        subprocess.run(["docker", "compose", "down"], check=True)

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
    
    print("Stopping.", flush=True) 
    try:
        stop_docker_compose()
    except KeyboardInterrupt:
        print("Script execution interrupted by user.")

if __name__ == "__main__":
    main()
