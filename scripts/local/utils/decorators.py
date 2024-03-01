"""
decorators.py

Provides decorators to enhance functionality within scripts.

Decorators:
- @require_docker_running: Ensures Docker engine is running before function
  execution. Useful for Docker-dependent scripts and applications.
"""

from functools import wraps
import subprocess
import sys
from .output import print

def require_docker_running(func):

    """
    Ensures Docker engine is active before the decorated function runs.

    Args:
        func (Callable): Function to decorate.

    Returns:
        Callable: Decorated function with Docker check.
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
            print("Docker not running. Please start it and try again.")
            sys.exit(1)

        return func(*args, **kwargs)

    return wrapper
