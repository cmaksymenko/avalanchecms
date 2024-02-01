# Avalanche CMS Local Stack

## Introduction

Welcome to the Avalanche CMS local stack guide. This document outlines the steps to configure and run the stack, which includes PostgreSQL, pgAdmin, and Keycloak.

## Prerequisites

This setup is primarily designed for and tested on a Windows 11 development environment. However, thanks to the containerized approach and the technology stack used, it should also run seamlessly on Linux environments. Ensure the following software is installed:

- **Docker Desktop**: [Download Docker Desktop](https://www.docker.com/products/docker-desktop) (For Windows 11)
- **Python 3**: [Download Python 3](https://www.python.org/downloads/) (Cross-platform)
- **Git Bash**: Recommended for executing scripts and Docker commands on Windows. [Download Git Bash](https://gitforwindows.org/). Linux users can use bash.

## Stack Components

The Avalanche CMS local development stack is based on Docker Compose and is composed of:

- **PostgreSQL Database (Version 16)**: Exposed on port 5432.
- **pgAdmin (Version 4)**: For database administration, accessible on port 5050.
- **Keycloak (Version 23 - Quarkus)**: Administration UI available on port 8080.

## Setup Instructions

### 1. Generate Secrets

Start by generating necessary secret files for initial deployment (use `-a` for automatic generation of secrets):

```
python scripts/local/setup.py
```

### 2. Start the Stack

To initialize / start the Avalanche CMS stack, run:

```
docker compose up
```

- Optionally, add `-d` for detached mode.
- For log monitoring, run in a shell like Git Bash.

### 3. Access Services

- **pgAdmin**:
  - URL: [http://localhost:5050](http://localhost:5050/)
  - Username: `admin@avalanchecm.com`
  - Password: Found in *.secrets/pgadmin-admin-user-secret.env*
- **Keycloak Admin UI**:
  - URL: [http://localhost:8080](http://localhost:8080/)
  - Username: `admin`
  - Password: Found in *.secrets/keycloak-admin-user-secret.env*

### 4. Setting up pgAdmin

[pgAdmin](http://localhost:5050/) comes preconfigured with a server connection to the local PostgreSQL instance. For security reasons, the only thing you need to manually enter is the PostgreSQL admin user secret found in */.secrets/postgres-admin-user-secret.env*.

## Persistence

- PostgreSQL and pgAdmin data remain persistent across restarts, thanks to Docker volumes.
- Keycloak's data is persistent as well, utilizing PostgreSQL for storage.
