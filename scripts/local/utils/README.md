# decorators.py Module

## Overview

The `decorators.py` module offers Python decorators to enhance script functions, mainly for Docker-dependent tasks, enabling pre-execution checks and behavior adjustments.

## Features

- **Docker Engine Check Decorator (`require_docker_running`)**: Ensures Docker engine is active before function execution, useful for Docker-dependent apps.

## Usage

### Require Docker Running

To use the `require_docker_running` decorator, import it from the `utils` module and apply it to any function that requires Docker to be running:

```python
from utils.decorators import require_docker_running

@require_docker_running
def my_docker_dependent_function():
    # function logic here
    pass

```
