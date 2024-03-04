# Avalanche CMS

## Overview

Avalanche CMS is a specialized **CMS** for **managing, safeguarding and improving AI-generated art** efficiently.

It offers a unified platform for tracking the progression of prompts, images, and creative choices in generative AI art, ideal for visual exploration and digital art creators. Integrated with AI-driven screening and automatic publication control, it safeguards creative processes, ensuring every generative AI image meets legal and community standards.

**The project is in its initial phase**, concentrating on local deployment, components, and tech. Progress updates will be shared over time.

## Planned Features

- Upload, manage and reference source images, prompts and used AI models.
- Track prompt refinements for generating new, original AI-generated images.
- Explore prompt and generated image evolutions with a filterable 2D interactive graph.
- Integrate with AI tools to feed forward generations and creative decisions.
- Create content origin reports for copyright compliance and risk assessment.
- AI-driven screening and publication block for infringement or standards violations.

## Application Server

Server code is in the `/server` directory, tech stack: Java 21, Spring Boot 3.3, and Maven 3.9. See [server README.md](/server/README.md).

## Development Setup

Local stack includes PostgreSQL, Keycloak, and pgAdmin, deployable with Docker Compose. Requires Python 3 for setup; details at [/environments/local/README.md](https://chat.openai.com/environments/local/README.md).
