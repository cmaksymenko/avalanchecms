"""
decorators.py

Contains decorators for script functionality.

- @require_docker_running: Checks if Docker is running.
"""

from functools import wraps
import subprocess
import sys
from .output import print

def require_docker_running(func):

    """
    Decorator to check Docker status before running func.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):

        """
        Checks Docker status; proceeds or exits with an error if not running.
        """

        def is_docker_running():
            
            """Verifies Docker engine status via 'docker info' command."""
            
            try:
                subprocess.run(["docker", "info"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return True
            except subprocess.CalledProcessError:
                return False

        if not is_docker_running():
            print("Docker not running.")
            sys.exit(1)

        return func(*args, **kwargs)

    return wrapper
