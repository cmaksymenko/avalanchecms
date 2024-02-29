from functools import wraps
import subprocess
import sys

# Decorator that checks if the Docker engine is running, terminating the script if not.
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
