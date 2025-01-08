# RAG Service

RAG Service is a fully functional Retrieval-Augmented Generation (RAG) system that integrates a variety of modern
technologies to provide advanced search and information retrieval capabilities. The service supports semantic search,
document ingestion, and asynchronous task processing, and offers an intuitive web interface for configuration.

---

Disclaimer
> This is the "lite" version of the system with only one LLM available. For the full version, you can contact me at khonikdev@gmail.com.
---

## Features

- **API**:
    - Built with FastAPI (Python).
    - Provides endpoints for interacting with LLMs, databases, and document management.
- **Databases**:
    - PostgreSQL for storing models and configurations.
    - Elasticsearch for document storage and semantic search.
- **Task Processing**:
    - Uses Kafka for message brokering and an asynchronous task service for document processing.
- **Web Interface**:
    - Built with Vue 3 (TypeScript).
    - Allows user registration, configuration of the RAG system (e.g., selecting LLMs, setting query contexts).
- **Authentication**:
    - Powered by SuperTokens.

---

## Project Structure

- `/api`: FastAPI application for backend services.
- `/web`: Vue 3 application for the frontend interface.
- **Docker Compose**: Streamlined setup for running all services, including Nginx, Kafka, PostgreSQL, Elasticsearch, and
  SuperTokens.

---

## Installation

### Prerequisites

- Docker and Docker Compose installed on your system.
- Basic knowledge of environment variables and shell commands.

### Steps

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Set Up Environment Variables**:
   Copy `.env.example` files to `.env` in their respective directories and update the values as necessary.

   Example for `api/.env`:
   ```env
   APP_ENV=local
   APP_URL=http://localhost:8000

   POSTGRES_DB=rag
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=password
   DATABASE_URL=${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}

   KAFKA_URL=kafka:29092

   S3_ENDPOINT_URL=
   S3_ACCESS_KEY=
   S3_SECRET_KEY=
   S3_BUCKET=

   ES_INDEX_NAME=my_rag_index
   ES_DOCUMENT_LIMIT=64

   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxx

   SENTRY_API_DNS=
   SENTRY_ENVIRONMENT=${APP_ENV}
   ```

   do the same for web directory and root directory


3. **Build and Start Services**:
   ```bash
   docker compose up -d
   ```

4. **Initialize Database and Index**:
   Run the following commands:
   ```bash
   # Create and seed the database
   make create_supertokens_db
   make migrate
   make model_seed

   # Create Elasticsearch index
   make create_index
   ```

5. **Access the Application**:
    - API: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
    - Web Interface: [http://localhost:8000](http://localhost:8000)

---

## Usage

- Configure the system via the web interface to:
    - Select LLM models.
    - Define context settings for queries.
    - Upload documents for processing and indexing.

- Use the API for programmatic interaction with the service.

---

## Makefile Commands

The `Makefile` includes several helpful commands:

- **Create Elasticsearch Index**:
  ```bash
  make create_index
  ```
- **Run Migrations**:
  ```bash
  make migrate
  ```
- **Rollback Migrations**:
  ```bash
  make migrate_rollback
  ```
- **Seed Models**:
  ```bash
  make model_seed
  ```
- **Lint and Format Code**:
    - Backend: `make lint_api`
    - Frontend: `make lint_web`

---

## Tech Stack

- **Backend**: FastAPI, Python
- **Frontend**: Vue 3, TypeScript
- **Databases**: PostgreSQL, Elasticsearch
- **Message Broker**: Kafka
- **Authentication**: SuperTokens

---

## Code Linting and Quality

**Vue Project:**

- Checked using ESLint and Prettier.

**Python Project:**

- Checked using Pylint and MyPy.

Example output from Pylint:
> Your code has been rated at 9.24/10 