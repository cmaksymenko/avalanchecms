# Avalanche CMS - Spring Boot Server

This directory contains the Spring Boot server for Avalanche CMS.

## Overview

The Spring Boot server is responsible for handling the backend logic of the CMS, including data management, API endpoints for the frontend interfaces, and integration.

## Building the Project Locally

This project is built using the Microsoft Build of OpenJDK 21 LTS and Apache Maven 3.9.6 on Windows 11. Follow the steps below to set up your environment and build the project.

### Prerequisites

1. **Java Development Kit (JDK):**
   - Download and install it from [Microsoft's Java OpenJDK download page](https://learn.microsoft.com/en-us/java/openjdk/download#openjdk-21), e.g., to `C:\Program Files\Microsoft\jdk-21.0.1.12-hotspot`.
   - Ensure that the `JAVA_HOME` environment variable is set to the JDK installation path and that the `bin` directory of the JDK is added to the system's `PATH`.

2. **Apache Maven:**
   - Download from the [Apache Maven official website](https://maven.apache.org/download.cgi).
   - Extract and install it to a directory without spaces in the path, e.g., `C:\maven\apache-maven-3.9.6`.
   - Add the `bin` directory of the Maven installation to the system's `PATH`.

### Building the Server

Once you have the JDK and Maven set up:

1. Open a command prompt or terminal.
2. Run the following Maven command to clean, compile, and package the project:

   ```bash
    mvn clean package
   ```

This command will compile the source code, run any tests, and package the compiled code into a JAR file. The JAR file can be found in the target directory created within the server directory.