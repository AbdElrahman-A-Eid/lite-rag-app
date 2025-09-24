# Lite RAG Application

A lightweight Retrieval-Augmented Generation (RAG) application that combines document retrieval with language model generation to provide contextual responses based on your documents.

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Environment Configuration](#environment-configuration)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [License](#license)

## Requirements

- **Python 3.12** (or later)
- **Anaconda or Miniconda**
- **Git**
- **Docker & Docker Compose**

### LLM Provider Support

The application supports multiple LLM providers and systems:

- **OpenAI** - GPT models via OpenAI API
- **Cohere** - Cohere AI language models
- **OpenAI-Compatible APIs** - Any system that implements OpenAI's API format, such as:
  - **Ollama**
  - **LocalAI**
  - Other OpenAI-compatible endpoints

*Note: You'll need appropriate API keys or access credentials for your chosen provider(s)*

### Vector Database

- **Qdrant** (embedded/local instance)
  - Automatically managed by the application
  - No separate installation required

### Document Processing

- **Posgres Database**
  - Used for document metadata and project management
  - Configured through Docker Compose

### Supported Document Formats

- **PDF files** (.pdf)
- **Text files** (.txt)

## Installation

### 1. Install Anaconda/Miniconda

If you don't have Anaconda or Miniconda installed:

Miniconda (recommended): https://docs.conda.io/en/latest/miniconda.html
Anaconda (full distribution): https://www.anaconda.com/products/distribution

### 2. Install Docker and Docker Compose

Docker Desktop (Windows/macOS): https://www.docker.com/products/docker-desktop/

Linux (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker $USER   # optional to run without sudo (re-login required)
```

Linux (Fedora/RHEL/CentOS):
```bash
sudo dnf install -y docker docker-compose-plugin || sudo yum install -y docker docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker $USER   # optional (re-login required)
```

Verify:
```bash
docker --version
docker compose version
```

### 3. Clone the Repository

```bash
git clone https://github.com/AbdElrahman-A-Eid/lite-rag-app.git
cd lite-rag-app
```

### 4. Create and Activate Conda Environment

```bash
conda create -n lite-rag python=3.12
conda activate lite-rag
```

### 5. Install Dependencies

```bash
# From repository root
cd src
pip install -r requirements.txt

# (Optional) Dev tools
# pip install -r requirements-dev.txt
```

### 6. Start Postgres Database with Docker

The application requires Postgres for document metadata and project management:

```bash
# From repository root
cd docker
docker compose up -d

# Verify Postgres is running
docker compose ps
```

### 7. Run the Application

```bash
# From repository root
cd src
conda activate lite-rag

# Start the FastAPI application
uvicorn main:app --host 0.0.0.0 --port 8000
# For development:
# uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The application will be available at:
- **API**: http://localhost:8000
- **Interactive API Documentation**: http://localhost:8000/docs
- **Alternative API Documentation**: http://localhost:8000/redoc

### 8. Verify Installation

Open http://localhost:8000/docs and check that endpoints are available.

### 9. Stopping the Application

```bash
# Stop the FastAPI app with Ctrl+C in the terminal

# Stop Postgres (optional)
# From repository root
cd docker
docker compose down
```

## Environment Configuration

### 1. Application Environment Configuration

Create your application environment file from the template:

```bash
# From repository root
cd src
cp .env.example .env
nano .env   # or use your preferred editor
```

**Required Environment Variables:**

**Application Settings:**
```env
RAG_APP_NAME=Lite-RAG-App
RAG_APP_VERSION=1.0.0
RAG_LOG_LEVEL=INFO
```

**Database Configuration:**
```env
RAG_DATABASE_HOSTNAME=localhost
RAG_DATABASE_PORT=5432
RAG_DATABASE_USERNAME=postgres
RAG_DATABASE_PASSWORD=
RAG_DATABASE_NAME=lite_rag
```

**LLM Provider Configuration** (choose at least one):

OpenAI:
```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE_URL=https://api.openai.com/v1
```

Cohere:
```env
COHERE_API_KEY=your_cohere_api_key_here
COHERE_API_BASE_URL=https://api.cohere.ai/v1
```

OpenAI-Compatible (e.g., Ollama):
```env
OPENAI_API_KEY=not_required_for_local
OPENAI_API_BASE_URL=http://localhost:11434/v1
```

Generation Settings (Optional):
```env
GENERATION_DEFAULT_MAX_TOKENS=1000
GENERATION_DEFAULT_TEMPERATURE=0.7
DEFAULT_INPUT_MAX_CHARACTERS=4000
```

Vector Database Settings (Optional):
```env
QDRANT_VECTOR_SIZE=768
QDRANT_DISTANCE_METRIC=COSINE
```

### 2. Docker Environment Configuration

Configure Docker environment variables for Postgres:

```bash
# From repository root
cd docker
cp .env.example .env
nano .env # or use your preferred editor
```

**Docker Environment Variables:**

```env
RAG_POSTGRES_DB=literag
RAG_POSTGRES_USER=postgres
RAG_POSTGRES_PASSWORD=
```

Note: When connecting from the application (running on host), set src/.env to use HOST=localhost and PORT matching the port exposed in docker/compose.yml (default 5432).

### 3. Environment Variable Descriptions

Application Environment (src/.env):

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| RAG_APP_NAME | Application name | Lite-RAG-App | No |
| RAG_APP_VERSION | Application version | 1.0.0 | No |
| RAG_LOG_LEVEL | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO | No |
| RAG_DATABASE_HOSTNAME | Postgres hostname | localhost | Yes |
| RAG_DATABASE_PORT | Postgres port | 5432 | Yes |
| RAG_DATABASE_USERNAME | Postgres username | postgres | Yes |
| RAG_DATABASE_PASSWORD | Postgres password | (empty) | Yes |
| RAG_DATABASE_NAME | Postgres database name | lite_rag | Yes |
| OPENAI_API_KEY | OpenAI API key | - | If using OpenAI |
| OPENAI_API_BASE_URL | OpenAI API base URL | https://api.openai.com/v1 | No |
| COHERE_API_KEY | Cohere API key | - | If using Cohere |
| COHERE_API_BASE_URL | Cohere API base URL | https://api.cohere.ai/v1 | No |
| GENERATION_DEFAULT_MAX_TOKENS | Default max tokens for generation | 1000 | No |
| GENERATION_DEFAULT_TEMPERATURE | Default temperature for generation | 0.7 | No |
| DEFAULT_INPUT_MAX_CHARACTERS | Max input characters | 4000 | No |
| QDRANT_VECTOR_SIZE | Vector dimension size | 768 | No |
| QDRANT_DISTANCE_METRIC | Distance metric for similarity | COSINE | No |

Docker Environment (docker/.env):

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| RAG_POSTGRES_DB | Postgres database name (container) | literag | Yes |
| RAG_POSTGRES_USER | Postgres username (container) | postgres | Yes |
| RAG_POSTGRES_PASSWORD | Postgres password (container) | - | Yes |

### 4. Provider-Specific Notes

OpenAI:
- Obtain API key: https://platform.openai.com/api-keys

Cohere:
- Obtain API key: https://dashboard.cohere.com/api-keys

Ollama (Local):
- Install: https://ollama.ai
- Start: `ollama serve`
- Pull a model: `ollama pull <model-name>`
- Set `OPENAI_API_BASE_URL=http://localhost:11434/v1`
- API key can be any value for local usage

Other OpenAI-Compatible:
- Adjust `OPENAI_API_BASE_URL` to point to your service
- Use appropriate authentication for your service

## Project Structure

```
lite-rag-app/
├── docker/                       # Docker configuration
│   ├── .env.example              # Docker environment template
│   ├── .gitignore                # Docker-specific gitignore
│   └── compose.yml               # Docker Compose configuration
├── src/                          # Main application source code
│   ├── assets/                   # Application assets and data storage
│   │   ├── databases/            # Local/embedded databases storage
│   │   ├── files/                # Uploaded project files storage
│   │   └── logs/                 # Application log files
│   ├── controllers/              # Business logic controllers
│   │   ├── __init__.py
│   │   ├── assets.py
│   │   ├── base.py
│   │   ├── documents.py
│   │   ├── projects.py
│   │   ├── rag.py
│   │   └── vectors.py
│   ├── databases/                # Relational database layer (Postgres)
│   │   ├── __init__.py
│   │   └── lite_rag/
│   │       ├── alembic/          # Database migrations
│   │       │   ├── README
│   │       │   ├── env.py
│   │       │   ├── script.py.mako
│   │       │   └── versions/     # Migration versions
│   │       ├── schemas/          # SQLAlchemy models
│   │       │   ├── __init__.py
│   │       │   ├── asset.py
│   │       │   ├── base.py
│   │       │   ├── chunk.py
│   │       │   └── project.py
│   │       └── __init__.py
│   ├── llm/                      # Large Language Model integration
│   │   ├── controllers/
│   │   │   ├── __init__.py
│   │   │   ├── factory.py        # LLM provider factory
│   │   │   └── templates.py      # Template management controller
│   │   ├── models/
│   │   │   ├── enums/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── inputs.py
│   │   │   │   ├── locales.py
│   │   │   │   ├── providers.py
│   │   │   │   └── roles.py
│   │   │   ├── __init__.py
│   │   │   └── base.py           # Base LLM interfaces
│   │   ├── providers/
│   │   │   ├── __init__.py
│   │   │   ├── cohere_provider.py
│   │   │   └── openai_provider.py
│   │   └── templates/            # LLM prompt templates
│   │       ├── locales/
│   │       │   ├── ar/
│   │       │   │   ├── __init__.py
│   │       │   │   └── rag.py
│   │       │   ├── en/
│   │       │   │   ├── __init__.py
│   │       │   │   └── rag.py
│   │       │   └── __init__.py
│   │       └── __init__.py
│   ├── models/                   # Data models and schemas
│   │   ├── enums/
│   │   │   ├── __init__.py
│   │   │   ├── assets.py
│   │   │   ├── documents.py
│   │   │   ├── log_level.py
│   │   │   └── responses.py
│   │   ├── __init__.py
│   │   ├── asset.py
│   │   ├── base.py
│   │   ├── chunk.py
│   │   ├── project.py
│   │   └── vector.py
│   ├── routes/                   # API route definitions
│   │   ├── schemas/              # Pydantic request/response schemas
│   │   │   ├── __init__.py
│   │   │   ├── assets.py
│   │   │   ├── documents.py
│   │   │   ├── projects.py
│   │   │   ├── rag.py
│   │   │   └── vectors.py
│   │   ├── __init__.py
│   │   ├── assets.py
│   │   ├── base.py
│   │   ├── documents.py
│   │   ├── projects.py
│   │   ├── rag.py
│   │   └── vectors.py
│   ├── vectordb/                 # Vector database integration
│   │   ├── controllers/
│   │   │   ├── __init__.py
│   │   │   └── factory.py        # Vector DB factory
│   │   ├── models/
│   │   │   ├── enums/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── providers.py
│   │   │   │   └── similarities.py
│   │   │   ├── __init__.py
│   │   │   └── base.py
│   │   └── providers/
│   │       ├── __init__.py
│   │       └── qdrant_provider.py
│   ├── .env.example              # Environment variables template
│   ├── .gitignore                # Git ignore file
│   ├── alembic.ini               # Alembic configuration
│   ├── config.py                 # Application configuration
│   ├── dependencies.py           # FastAPI dependency injections
│   ├── main.py                   # Application entry point
│   └── requirements.txt          # Python dependencies
├── LICENSE                       # MIT License
└── README.md                     # Project documentation
```

## Usage

### 1. Getting Started

After completing the installation and environment configuration, you can start using the RAG application through the interactive API documentation or direct API calls.

### 2. Access the API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. Basic Workflow

1. Create a Project — Organize your documents into projects
2. Upload Documents — Add PDF or text files to your project
3. Process Documents — Convert documents into searchable chunks
4. Index Vectors — Create embeddings and store them in the vector database
5. Perform RAG Queries — Ask questions and get contextual responses

### 4. Available API Endpoints

Base Endpoints

**`GET /api/v1/`** - Root endpoint
- Returns application name and version

**`GET /api/v1/health`** - Health check endpoint
- Returns application health status

Project Management

**`POST /api/v1/projects/create`** - Create a new project
- **Optional**: `name` (string), `description` (string, max 500 chars)
- **Response**: 201 Created with project details

**`GET /api/v1/projects/list`** - List all projects
- **Optional**: `skip` (integer, default: 0), `limit` (integer, default: 10, max: 100)
- **Response**: 200 OK with projects list, count, and total

**`GET /api/v1/projects/{project_id}`** - Get project details
- **Required**: `project_id` (path parameter)
- **Response**: 200 OK with project details, 404 if not found

**`DELETE /api/v1/projects/{project_id}`** - Delete project
- **Required**: `project_id` (path parameter)
- **Response**: 204 No Content, 404 if not found

Asset Management

**`POST /api/v1/p/{project_id}/assets/upload`** - Upload single file
- **Required**: `project_id` (path parameter), `file` (multipart/form-data)
- **Supported formats**: PDF (.pdf), Text (.txt)
- **Response**: 200 OK with asset details, 400/404/500 for errors

**`POST /api/v1/p/{project_id}/assets/upload/batch`** - Upload multiple files
- **Required**: `project_id` (path parameter), `files` (list of multipart/form-data)
- **Response**: 200 OK with batch upload results

**`GET /api/v1/p/{project_id}/assets/`** - List project assets
- **Required**: `project_id` (path parameter)
- **Response**: 200 OK with assets list and count

**`DELETE /api/v1/p/{project_id}/assets/{asset_id}`** - Delete specific asset
- **Required**: `project_id` (path parameter), `asset_id` (path parameter)
- **Response**: 204 No Content, 404 if not found

**`DELETE /api/v1/p/{project_id}/assets/`** - Delete all project assets
- **Required**: `project_id` (path parameter)
- **Response**: 204 No Content, 404 if not found

Document Processing

**`POST /api/v1/p/{project_id}/documents/process`** - Process document into chunks
- **Required**: `project_id` (path parameter), `file_id` (string)
- **Optional**: `chunk_size` (integer, default: 300, min: 1), `chunk_overlap` (integer, default: 40, min: 0)
- **Response**: 201 Created with chunks details

**`POST /api/v1/p/{project_id}/documents/refresh`** - Refresh all project documents
- **Required**: `project_id` (path parameter)
- **Optional**: `chunk_size` (integer, default: 300), `chunk_overlap` (integer, default: 40)
- **Response**: 201 Created with processing results for all assets

**`GET /api/v1/p/{project_id}/documents/{file_id}/list`** - List document chunks
- **Required**: `project_id` (path parameter), `file_id` (path parameter)
- **Optional**: `skip` (integer, default: 0), `limit` (integer, default: 100, max: 300)
- **Response**: 200 OK with chunks list, count, and total

**`DELETE /api/v1/p/{project_id}/documents/{file_id}`** - Delete document chunks
- **Required**: `project_id` (path parameter), `file_id` (path parameter)
- **Response**: 204 No Content, 404 if not found

Vector Operations

**`POST /api/v1/p/{project_id}/vectors/index`** - Index document vectors
- **Required**: `project_id` (path parameter)
- **Optional**: `reset` (boolean, default: false)
- **Response**: 201 Created on success, 404/500 for errors

**`POST /api/v1/p/{project_id}/vectors/query`** - Query similar vectors
- **Required**: `project_id` (path parameter), `query` (string)
- **Optional**: `top_k` (integer, default: 5, min: 1), `threshold` (float, range: 0.0-1.0)
- **Response**: 200 OK with results and count

RAG Operations

**`POST /api/v1/p/{project_id}/rag/generate`** - Generate RAG response
- **Required**: `project_id` (path parameter), `query` (string)
- **Optional**:
  - `top_k` (integer, default: 5, min: 1)
  - `threshold` (float, range: 0.0-1.0)
  - `temperature` (float, range: 0.0-2.0)
  - `max_output_tokens` (integer, min: 1)
- **Response**: 202 Accepted with response, citations, and contexts

### 5. Request/Response Examples

Project Creation
**`POST /api/v1/projects/create`**

**Request Body:**
```json
{
  "name": "Research Papers",
  "description": "Academic papers on machine learning"
}
```

**Response:**
```json
{
  "id": "1867260d-cf8e-4535-9441-54988ad100e3",
  "name": "Research Papers",
  "description": "Academic papers on machine learning"
}
```

Document Processing
**`POST /api/v1/p/1867260d-cf8e-4535-9441-54988ad100e3/documents/process`**

**Request Body:**
```json
{
  "file_id": "70e865ce_document_filename.pdf",
  "chunk_size": 500,
  "chunk_overlap": 50
}
```

**Response:**
```json
{
  "project_id": "1867260d-cf8e-4535-9441-54988ad100e3",
  "file_id": "70e865ce_document_filename.pdf",
  "chunks": [
    {
      "chunk_order": 0,
      "page_content": "Document content...",
      "metadata": {
        ...
      }
    }
  ],
  "count": 1
}
```

Vector Indexing
**`POST /api/v1/p/1867260d-cf8e-4535-9441-54988ad100e3/vectors/index`**

**Request Body:**
```json
{
  "reset": false
}
```

RAG Query
**`POST /api/v1/p/1867260d-cf8e-4535-9441-54988ad100e3/rag/generate`**

**Request Body:**
```json
{
  "query": "What machine learning techniques are discussed?",
  "top_k": 5,
  "threshold": 0.7,
  "temperature": 0.7,
  "max_output_tokens": 1000
}
```

**Response:**
```json
{
  "response": "Based on the provided documents, the main machine learning techniques include...",
  "citations": [
    {
      "text": "Relevant text from the document...",
      "metadata": {
        ...
      }
    }
  ],
  "contexts": [
    {
      "text": "Context document content...",
      "metadata": {
        ...
      }
    }
  ]
}
```

### 6. Parameter Reference

Common Parameters

| Parameter | Type | Description | Default | Range/Notes |
|-----------|------|-------------|---------|-------------|
| project_id | string | Project identifier | - | Path parameter |
| file_id | string | File/asset identifier | - | Usually filename |
| asset_id | string | Asset identifier | - | System-generated |
| chunk_size | integer | Document chunk size | 300 | Min: 1 |
| chunk_overlap | integer | Overlap between chunks | 40 | Min: 0 |
| top_k | integer | Number of results to return | 5 | Min: 1 |
| threshold | float | Similarity threshold | - | 0.0-1.0 |
| temperature | float | LLM response creativity | - | 0.0-2.0 |
| max_output_tokens | integer | Maximum response tokens | - | Min: 1 |
| reset | boolean | Reset index before indexing | false | - |
| skip | integer | Number of items to skip | 0 | Pagination |
| limit | integer | Maximum items to return | varies | Endpoint-specific |

### 7. Best Practices

Document Upload
- Use descriptive file names
- Ensure PDFs have selectable text
- Supported formats: PDF (.pdf), Text (.txt)

Document Processing
- Adjust chunk_size based on document type (300–1000 typical)
- Use chunk_overlap ~10–20% of chunk_size
- Process documents before indexing vectors

Vector Operations
- Use reset: true to rebuild the index
- Test retrieval via vector queries before RAG

RAG Queries
- Start with higher thresholds (0.7–0.8) for precision
- Lower thresholds (0.5–0.6) for broader recall
- Tune top_k (3–5 simple, 5–10 complex)
- Tune temperature (0.1–0.3 factual, 0.7–1.0 creative)

### 8. Common Response Codes

| Code | Description |
|------|-------------|
| 200 | OK |
| 201 | Created |
| 202 | Accepted |
| 204 | No Content |
| 400 | Bad Request |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |

### 9. Error Messages

Common standardized error signals include:
- FILE_UPLOAD_FAILED: File Upload Failed
- NO_FILE_PROVIDED: No File Provided
- UNSUPPORTED_FILE_TYPE: Unsupported File Type
- FILE_TOO_LARGE: File Too Large
- FILE_VALIDATION_ERROR: File Validation Error
- DOCUMENT_PROCESSING_FAILED: Document Processing Failed
- PROJECT_CREATION_FAILED: Project Creation Failed
- CHUNK_NOT_FOUND: No Chunks Found for the specified Project or File
- PROJECT_NOT_FOUND: Project Not Found
- ASSET_NOT_FOUND: Asset Not Found
- NO_DOCUMENTS_FOUND: No Documents Found
- VECTOR_INDEXING_FAILED: Vector Indexing Failed
- VECTOR_INDEX_NOT_FOUND: Vector Index Not Found
- VECTOR_INDEX_EMPTY: Vector Index is Empty
- RAG_GENERATION_FAILED: RAG Generation Failed
- FILE_NOT_FOUND: File Not Found
- ASSET_DELETION_FAILED: Asset Deletion Failed

### 10. Troubleshooting

Upload failures (400)
- Verify file format is PDF or TXT
- Ensure project exists before uploading

Processing errors (500)
- Confirm uploaded file is readable (PDFs must have selectable text)
- Verify asset exists in the project
- Check application logs

Vector indexing failures
- Ensure documents are processed into chunks first
- Verify chunks exist
- Verify embedding/model provider configuration

Empty RAG responses
- Confirm vector index exists and contains vectors
- Lower similarity threshold (e.g., 0.5–0.6)
- Ensure query matches document content
- Verify LLM provider API keys

Template errors in RAG
- Verify local templates exist in `src/llm/templates/locales/`
- Check template controller configuration
- Review logs for missing template errors

Getting Help

For detailed error information:
- Check the interactive API documentation at http://localhost:8000/docs
- Review application logs in `src/assets/logs/app.log`
- Use the "Try it out" feature in Swagger UI for testing endpoints
- Check Postgres Database and application status with `docker-compose logs`
- Verify environment configuration matches requirements

## Future Work
- Add support for local [Unstructured Loader](https://python.langchain.com/docs/integrations/document_loaders/unstructured_file/)

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
