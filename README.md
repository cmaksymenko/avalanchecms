# Avalanche CMS

Avalanche CMS is a specialized content management system designed for curating and enhancing AI-generated artwork. Useful for anyone engaged in visual exploration and digital art creation within the generative AI space.

## Project Status: Bootstrapping

**Note:** Avalanche CMS is currently in the bootstrapping phase. This initial stage involves setting up the fundamental components and technologies that form the core of the project. As such, the current state represents the early steps in development, focusing on establishing the basic infrastructure and functionalities. I appreciate your patience and interest as I work on building and refining it.

## Server
- The application server component of Avalanche CMS is a Spring Boot application, using Java 21 LTS.
- The server codebase is located in the `/server` directory of the repository.
- For detailed setup and build instructions, see [server README.md](/server/README.md) in the `/server` directory.

## Local Development
- Requires Python 3, Java 21, Maven, Docker Desktop
- Run the `python scripts/local-dev/setup.py` for initialization of your local development setup.
- A Docker Compose Stack for local database deployment of a PostgreSQL database and pgAdmin is provided in `\database\postgres`. See [README.md](/database/postgres/README.md) in the `\database\postgres` directory.