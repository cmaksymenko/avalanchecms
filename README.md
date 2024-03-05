# Avalanche CMS

## Overview

Avalanche is a specialized image-based **CMS** for **refining, safeguarding and publishing AI-generated art** efficiently.

It offers a unified platform for digital art creators to [mine image concepts](/docs/concept-mining.md), track progression of generative art prompts, images and creative choices, meet legal and community standards, and publish to the public.

**The project is in its initial phase**, concentrating on local deployment, components, and tech. Progress updates will be shared over time.

## Planned Features

- Upload, manage and reference source images, prompts and used AI models.
- Track prompt refinements for generating new, original AI-generated images.
- Explore prompt and generated image evolutions with a filterable 2D interactive graph.
- Integrate with AI tools to feed forward generations and creative decisions (planned: Midjourney)
- Create content origin reports for copyright compliance and community standards risk assessment.
- AI-driven content screening and automatic publication block for infringement or community standards violations.

## Application Server

Server code is in the `/server` directory, tech stack: Java 21, Spring Boot 3.3, and Maven 3.9. See [server README.md](/server/README.md).

## Development Setup

Local stack includes PostgreSQL, Keycloak, and pgAdmin, deployable with Docker Compose. Requires Python 3 for setup; details at [/environments/local/README.md](/environments/local/README.md).
