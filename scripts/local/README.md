# Avalanche CMS Local Stack Scripts

This collection of scripts is designed to streamline the setup, management, and maintenance of the Avalanche CMS local development environment using Docker. Each script serves a specific role in the lifecycle of the development environment, from initialization to cleanup.

## Overview

The scripts included are:
- `setup.py`: Initializes the dev environment.
- `start.py`: Starts the local Docker stack.
- `stop.py`: Stops the local Docker stack.
- `cleanup.py`: Cleans the local dev environment.
- `pull.py`: Pulls Docker images.

## Prerequisites

Before using these scripts, ensure Docker is installed and running on your system. The scripts interact directly with Docker to manage the Avalanche CMS environment.

## Initial Setup

1. **Setup Environment**: Run `setup.py` to initialize secrets and other necessary configurations. For an interactive setup in which secrets are typed in, execute:

```
python setup.py
```

​	Automate secret generation with:
```
python setup.py -a
```

2. **Start the Stack**: To start the Avalanche CMS stack, run `start.py`. For a standard start:

```
python start.py
```

​	To start in detached mode (background), add the `-d` option:
```
python start.py -d
```

## Regular Use

- **Updating Docker Images**: Before setting up or starting the stack, update Docker images with the `-ip` option in `setup.py` or `start.py`.
- **Clean Start**: For development, especially when working on stack setup or DevOps, automate a clean environment initialization and start with:

```
python start.py -c
```

- This command cleans the environment, auto-generates secrets, and starts the stack.

## Scripts Detail

### `cleanup.py`

Cleans the Avalanche CMS local dev environment. Options include:

- `-kv`, `--keep-volumes`: Retain Docker volumes.
- `-ks`, `--keep-secrets`: Retain `.secrets`.

### `pull.py`

Pulls Docker images based on `./config/docker_images.json`. Run without arguments.

### `setup.py`

Initializes the development environment with options for automated setup, Docker image updates, and more. Options include:

- `-a`, `--auto`: Automated setup.
- `-c`, `--clean`: Full reset with options to keep volumes and secrets.
- Additional debug options: `-s`, `-p`.

### `start.py`

Starts the local Docker stack with options for cleaning data, updating images, and detached mode.

### `stop.py`

Stops the Docker containers safely. Use this script to gracefully shut down the stack, especially useful in detached mode.

## Configuration Files

The `./config` subfolder contains configuration files for the development environment, specifically `credentials.json` (credentials for the environment's components) and `docker_images.json` (used Docker images throughout the stack).

## Additional Notes

- Running `start.py` in the terminal will attach the stack to your current terminal session. Use CTRL+C to stop the stack or `-d` for detached mode.
- If the Docker engine starts with the stack previously deployed, containers will automatically run. Use `stop.py` to shut down the stack first if needed.
- The `pull.py` script is useful for updating Docker images to the latest minor versions if they are pinned to a major version.