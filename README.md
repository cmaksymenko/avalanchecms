# Avalanche CMS

## About

Avalanche CMS is a specialized **content management system** designed for **curating and enhancing AI-generated artwork** in a streamlined way. 

It provides a centralized platform to capture and organize the non-linear evolution of prompts, associated generated images, and creative decisions. It is useful for anyone engaged in visual exploration and digital art creation within the generative AI space.

## Project Status

Avalanche CMS is in its early development stages. The focus is currently on establishing the basic components and technologies essential for the project's foundation. Below is an outline of planned future developments - updates and advancements will be shared as the project evolves.

## Planned Features

### Image Echoing

This workflow will enable the tracking of all prompt refinement steps involved in replicating original pictures using generative AI - serving as the foundation for new, original artworks. See [image-echoing.md](/docs/image-echoing.md) for further details.

- Includes the possibility to upload and organize source material.
- Provides an interactive graph interface, which displays the evolution of prompts and their generated images in a 2D space view for easy exploration and experimentation. Possibility to add comments, use custom tags for filtering, and outcome rating.
- Integration of AI tools to support the creative process and decision making. May include integration with Midjourney's Discord interface.

## Server
- The application server component of Avalanche CMS is a Spring Boot application, using Java 21 LTS.
- The server codebase is located in the `/server` directory of the repository.
- For detailed setup and build instructions, see [server README.md](/server/README.md) in the `/server` directory.

## Local Development
- Requires Python 3, Java 21, Maven, Docker Desktop
- Run the `python scripts/local-dev/setup.py` for initialization of your local development setup.
- A Docker Compose Stack for local database deployment of a PostgreSQL database and pgAdmin is provided in `\database\postgres`. See [README.md](/database/postgres/README.md) in the `\database\postgres` directory.