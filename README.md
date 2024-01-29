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

## Application Server

- An application server will be built using Java 21 and Spring Boot 3.3, utilizing Maven 3.9 for building.
- The server's codebase can be found in the `/server` directory of the repository.
- For more information on setup and build procedures, refer to the [server README.md](/server/README.md) located in the `/server` directory.

## Local Development Environment

- The local development stack includes a PostgreSQL database, Keycloak for identity and access management, and pgAdmin for database administration.
- This stack can be deployed locally using Docker Compose.
- Python 3 is required for the initial setup. Detailed instructions and additional prerequisites are available in the [/environments/local/README.md](/environments/local/README.md).
