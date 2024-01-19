# Docker Compose for Avalanche CMS - Local Development Database

## Overview
This Docker Compose setup is tailored for local development and deploys the database. It comprises two services:
- `postgres`: PostgreSQL database utilizing the Alpine image for enhanced efficiency and security.
- `pgadmin`: A user-friendly, web-based administration tool for PostgreSQL.

## Features
- Secure management of sensitive data through Docker secret files.
- Persistent volumes for both the database and pgAdmin, ensuring data durability.

## Usage
- Start the services by running `docker compose up` in this directory.
- Alternatively, execute `docker compose -f database/postgres/docker-compose.yml up` in the repository's root directory.
- Use `-d` to launch in detached mode and monitor via Docker Desktop.

## Service Descriptions

### PostgreSQL Database
The `postgres` service is the used database management system and is configured with environment variables. These include `POSTGRES_DB` for the database name (`avalanche-cms-db`) and `POSTGRES_USER` for the admin username (`admin`). The database's administrative password is securely handled through a Docker secret file (see local development setup.py script for creation). The service exposes port 5432 for database connection.

### pgAdmin for Database Management
`pgadmin` serves as web-based administration interface for the PostgreSQL database. It's configured with an admin username (`admin@avalanche-cms.com`). The admins password is securely handled through a Docker secret file (see local development setup.py script for creation). The service, which depends on `postgres` (starts after), is accessible through http://localhost:8080.

**Note:** pgAdmin requires initial configuration to connect to the PostgreSQL server. Upon first login, you must manually add the PostgreSQL server to pgAdmin.

### Configuring pgAdmin
- Log in to pgAdmin using admin credentials.
- Right-click on 'Servers' in the pgAdmin dashboard and select 'Create' -> 'Server'.
- In the 'General' tab, give a meaningful name to the server (e.g., `Avalanche CMS DB`).
- Switch to the 'Connection' tab and enter `postgres` as the host (the service name in Docker Compose acts as the hostname).
- Fill in the PostgreSQL admin user and secret details.
- Save the configuration to connect to the PostgreSQL database. The configuration is persisted for later use.

## Volumes
- **postgres-data:** This volume is dedicated to PostgreSQL data, ensuring that all database information is persistently stored across device restarts.
- **pgadmin-data:** Used by the pgAdmin service, this volume maintains pgAdmin's configuration and state.

## Network Configuration
A custom bridge network, `avalanche-cms` interconnects the services, facilitating secure and efficient container-to-container communication.

