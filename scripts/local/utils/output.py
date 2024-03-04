"""
output.py

Improves logging.

- print: Flushes print messages instantly.
"""

import builtins

def print(*args, **kwargs):
    
    """
    Modified print for instant output. Adds 'flush=True'.
    """
    
    kwargs.setdefault('flush', True)
    return builtins.print(*args, **kwargs)
