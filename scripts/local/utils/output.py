"""
output.py

Enhances script logging.

Functions:
- print: Redefines print to flush immediately, making messages visible without delay.
"""

import builtins

def print(*args, **kwargs):
    
    """
    Redefines print for immediate output, aiding visibility in buffered
    environments like Docker logs. Useful for fast diagnostics.

    Args:
        *args: Arguments to print.
        **kwargs: Keyword arguments. Defaults to 'flush=True'.

    Returns:
        None.
    """  
    
    kwargs.setdefault('flush', True)
    return builtins.print(*args, **kwargs)
