# Utils Module for Python

## Overview

The `utils` module provides Python utilities to enhance script functionality, focusing on Docker-dependent tasks and improved logging capabilities. It includes decorators for pre-execution checks and behavior adjustments, alongside enhancements for script output logging.

## Modules

### decorators.py

Offers decorators to ensure the necessary runtime conditions are met before executing functions, primarily aimed at Docker-dependent scripts and applications.

#### Features

- **Docker Engine Check Decorator (`require_docker_running`)**: Ensures the Docker engine is active before the execution of decorated functions, useful for Docker-dependent applications.

#### Usage

```python
from utils.decorators import require_docker_running

@require_docker_running
def my_docker_dependent_function():
    # Function logic here
```

### output.py

Enhances script logging by modifying the built-in `print` function to flush output immediately. This is particularly useful in buffered environments like Docker logs where immediate feedback is crucial.

#### Features

- **Enhanced Print Function**: Redefines `print` to automatically flush output, ensuring messages are visible without delay, aiding fast diagnostics in buffered environments.

#### Usage

To use the enhanced `print` function, simply import it from the `utils` module. It can be used exactly like the built-in `print` function, but with the added benefit of immediate output.

```python
from utils.output import print

print("This message will be flushed immediately.")
```

## Getting Started

To get started with the `utils` module, import the required decorators or enhancements in your script:

```python
from utils.decorators import require_docker_running
from utils.output import print
```

Apply the `require_docker_running` decorator to any function that depends on Docker being active, and use the enhanced `print` function for improved logging and output visibility.
