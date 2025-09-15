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

- **MongoDB**
  - Used for document metadata and project management
  - Configured through Docker Compose

### Supported Document Formats

- **PDF files** (.pdf)
- **Text files** (.txt)

## Installation

### 1. Install Anaconda/Miniconda

If you don't have Anaconda or Miniconda installed:

**Miniconda (recommended for lighter installation):**
- Download from: https://docs.conda.io/en/latest/miniconda.html
- Follow the installation instructions for your operating system

**Anaconda (full distribution):**
- Download from: https://www.anaconda.com/products/distribution
- Follow the installation instructions for your operating system

### 2. Install Docker and Docker Compose

If you don't have Docker and Docker Compose installed:

**Docker Desktop (recommended for Windows and macOS):**
- Download from: https://www.docker.com/products/docker-desktop/
- Follow the installation instructions for your operating system
- Docker Desktop includes Docker Compose automatically

**Docker Engine (for Linux):**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose

# CentOS/RHEL/Fedora
sudo yum install docker docker-compose
# or for newer versions:
sudo dnf install docker docker-compose

# Start and enable Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to the docker group (optional, to run without sudo)
sudo usermod -aG docker $USER
```

**Verify Docker installation:**
```bash
docker --version
docker-compose --version
```

### 3. Clone the Repository

```bash
git clone https://github.com/AbdElrahman-A-Eid/lite-rag-app.git
cd lite-rag-app
```

### 4. Create and Activate Conda Environment

```bash
# Create a new conda environment with Python 3.12
conda create -n lite-rag python=3.12

# Activate the environment
conda activate lite-rag
```

### 5. Install Dependencies

```bash
# Install project dependencies
pip install -r requirements.txt
```

### 6. Start MongoDB with Docker

The application requires MongoDB for document metadata and project management:

```bash
# Navigate to the docker directory
cd docker

# Start MongoDB using Docker Compose
docker-compose up -d

# Verify MongoDB is running
docker-compose ps
```

### 7. Run the Application

```bash
# Navigate to src directory and ensure conda environment is activated
cd ../src
conda activate lite-rag

# Start the FastAPI application using uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000
```

The application will be available at:
- **API**: http://localhost:8000
- **Interactive API Documentation**: http://localhost:8000/docs
- **Alternative API Documentation**: http://localhost:8000/redoc

### 8. Verify Installation

You can verify the installation by accessing the API documentation at http://localhost:8000/docs and checking that all endpoints are available.

### 9. Stopping the Application

To stop the application:

```bash
# Stop the FastAPI application
# Press Ctrl+C in the terminal where uvicorn is running

# Stop MongoDB (optional)
cd ../docker
docker-compose down
```

## Environment Configuration

### 1. Application Environment Configuration

Create your application environment file from the template:

```bash
# Navigate to src directory
cd src

# Copy the environment template
cp .env.example .env
```

Edit the `.env` file with your specific configuration:

```bash
nano .env
# or use your preferred text editor
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
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=lite_rag_app
```

**LLM Provider Configuration:**

Choose and configure at least one LLM provider:

*For OpenAI:*
```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE_URL=https://api.openai.com/v1
```

*For Cohere:*
```env
COHERE_API_KEY=your_cohere_api_key_here
COHERE_API_BASE_URL=https://api.cohere.ai/v1
```

*For OpenAI-Compatible APIs (e.g., Ollama):*
```env
OPENAI_API_KEY=not_required_for_local
OPENAI_API_BASE_URL=http://localhost:11434/v1
```

**Generation Settings (Optional):**
```env
GENERATION_DEFAULT_MAX_TOKENS=1000
GENERATION_DEFAULT_TEMPERATURE=0.7
DEFAULT_INPUT_MAX_CHARACTERS=4000
```

**Vector Database Settings (Optional):**
```env
QDRANT_VECTOR_SIZE=768
QDRANT_DISTANCE_METRIC=COSINE
```

### 2. Docker Environment Configuration

Configure the Docker environment for MongoDB:

```bash
# Navigate to docker directory
cd docker

# Copy the Docker environment template
cp .env.example .env
```

Edit the Docker `.env` file:

```bash
nano .env
# or use your preferred text editor
```

**Docker Environment Variables:**

```env
# MongoDB Configuration
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=your_secure_password_here
MONGO_INITDB_DATABASE=lite_rag_app

# MongoDB Connection (used by application)
MONGODB_PORT=27017
MONGODB_HOST=localhost
```

### 3. Environment Variable Descriptions

**Application Environment (src/.env):**

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `RAG_APP_NAME` | Application name | Lite-RAG-App | No |
| `RAG_APP_VERSION` | Application version | 1.0.0 | No |
| `RAG_LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO | No |
| `MONGODB_URL` | MongoDB connection string | mongodb://localhost:27017 | Yes |
| `MONGODB_DATABASE` | MongoDB database name | lite_rag_app | No |
| `OPENAI_API_KEY` | OpenAI API key | - | If using OpenAI |
| `OPENAI_API_BASE_URL` | OpenAI API base URL | https://api.openai.com/v1 | No |
| `COHERE_API_KEY` | Cohere API key | - | If using Cohere |
| `COHERE_API_BASE_URL` | Cohere API base URL | https://api.cohere.ai/v1 | No |
| `GENERATION_DEFAULT_MAX_TOKENS` | Default max tokens for generation | 1000 | No |
| `GENERATION_DEFAULT_TEMPERATURE` | Default temperature for generation | 0.7 | No |
| `DEFAULT_INPUT_MAX_CHARACTERS` | Max input characters | 4000 | No |
| `QDRANT_VECTOR_SIZE` | Vector dimension size | 768 | No |
| `QDRANT_DISTANCE_METRIC` | Distance metric for similarity | COSINE | No |

**Docker Environment (docker/.env):**

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MONGO_INITDB_ROOT_USERNAME` | MongoDB root username | admin | Yes |
| `MONGO_INITDB_ROOT_PASSWORD` | MongoDB root password | - | Yes |
| `MONGO_INITDB_DATABASE` | Initial MongoDB database | lite_rag_app | No |
| `MONGODB_PORT` | MongoDB exposed port | 27017 | No |
| `MONGODB_HOST` | MongoDB host | localhost | No |

### 4. Provider-Specific Notes

**OpenAI:**
- Obtain API key from: https://platform.openai.com/api-keys
- Standard OpenAI API endpoint is used by default

**Cohere:**
- Obtain API key from: https://dashboard.cohere.com/api-keys
- Standard Cohere API endpoint is used by default

**Ollama (Local):**
- Install Ollama from: https://ollama.ai
- Start Ollama service: `ollama serve`
- Pull a model: `ollama pull <model-name>`  <!-- Replace `<model-name>` with your preferred model id -->
- Set `OPENAI_API_BASE_URL=http://localhost:11434/v1`
- API key can be any value for local usage

**Other OpenAI-Compatible:**
- Adjust `OPENAI_API_BASE_URL` to point to your service
- Use appropriate authentication method for your service

## Project Structure

```
lite-rag-app/
├── docker/                       # Docker configuration
│   ├── .env.example              # Docker environment template
│   ├── .gitignore                # Docker-specific gitignore
│   └── compose.yml               # Docker Compose configuration
├── src/                          # Main application source code
│   ├── assets/                   # Application assets and data storage
│   │   ├── databases/            # Vector database storage
│   │   ├── files/                # Uploaded project files storage
│   │   └── logs/                 # Application log files
│   ├── controllers/              # Business logic controllers
│   │   ├── __init__.py           # Controllers module initialization
│   │   ├── assets.py             # Asset management controller
│   │   ├── base.py               # Base controller class
│   │   ├── documents.py          # Document processing controller
│   │   ├── projects.py           # Project management controller
│   │   ├── rag.py                # RAG operations controller
│   │   └── vectors.py            # Vector operations controller
│   ├── llm/                      # Large Language Model integration
│   │   ├── controllers/          # LLM controllers
│   │   │   ├── __init__.py       # LLM controllers initialization
│   │   │   ├── factory.py        # LLM provider factory
│   │   │   └── templates.py      # Template management controller
│   │   ├── models/               # LLM data models
│   │   │   ├── enums/            # LLM enumerations
│   │   │   │   ├── __init__.py   # LLM enums initialization
│   │   │   │   ├── inputs.py     # Input type enums
│   │   │   │   ├── locales.py    # Locale enums
│   │   │   │   ├── providers.py  # LLM provider enums
│   │   │   │   └── roles.py      # Message role enums
│   │   │   ├── __init__.py       # LLM models initialization
│   │   │   └── base.py           # Base LLM interfaces
│   │   ├── providers/            # LLM provider implementations
│   │   │   ├── __init__.py       # Providers initialization
│   │   │   ├── cohere_provider.py # Cohere LLM implementation
│   │   │   └── openai_provider.py # OpenAI LLM implementation
│   │   ├── templates/            # LLM prompt templates
│   │   │   ├── locales/          # Localized templates
│   │   │   │   ├── ar/           # Arabic templates
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── rag.py    # Arabic RAG templates
│   │   │   │   ├── en/           # English templates
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── rag.py    # English RAG templates
│   │   │   │   └── __init__.py   # Locales initialization
│   │   │   └── __init__.py       # Templates initialization
│   │   └── __init__.py           # LLM module initialization
│   ├── models/                   # Data models and schemas
│   │   ├── enums/                # Application enumerations
│   │   │   ├── __init__.py       # Enums module initialization
│   │   │   ├── assets.py         # Asset-related enums
│   │   │   ├── collections.py    # Database collection enums
│   │   │   ├── documents.py      # Document-related enums
│   │   │   ├── log_level.py      # Logging level enums
│   │   │   └── responses.py      # Response signal enums
│   │   ├── __init__.py           # Models module initialization
│   │   ├── asset.py              # Asset data models
│   │   ├── base.py               # Base model classes
│   │   ├── chunk.py              # Document chunk models
│   │   ├── project.py            # Project data models
│   │   └── vector.py             # Vector data models
│   ├── routes/                   # API route definitions
│   │   ├── schemas/              # Pydantic request/response schemas
│   │   │   ├── __init__.py       # Schemas module initialization
│   │   │   ├── assets.py         # Asset-related schemas
│   │   │   ├── documents.py      # Document-related schemas
│   │   │   ├── projects.py       # Project-related schemas
│   │   │   ├── rag.py            # RAG-related schemas
│   │   │   └── vectors.py        # Vector-related schemas
│   │   ├── __init__.py           # Routes module initialization
│   │   ├── assets.py             # Asset-related routes
│   │   ├── base.py               # Base route definitions
│   │   ├── documents.py          # Document-related routes
│   │   ├── projects.py           # Project-related routes
│   │   ├── rag.py                # RAG-related routes
│   │   └── vectors.py            # Vector-related routes
│   ├── vectordb/                 # Vector database integration
│   │   ├── controllers/          # Vector DB controllers
│   │   │   ├── __init__.py       # Controllers initialization
│   │   │   └── factory.py        # Vector DB factory
│   │   ├── models/               # Vector DB models
│   │   │   ├── enums/            # Vector DB enumerations
│   │   │   │   ├── __init__.py   # Vector DB enums initialization
│   │   │   │   ├── providers.py  # Vector DB provider enums
│   │   │   │   └── similarities.py # Similarity metric enums
│   │   │   ├── __init__.py       # Vector DB models initialization
│   │   │   └── base.py           # Base vector DB interfaces
│   │   ├── providers/            # Vector DB provider implementations
│   │   │   ├── __init__.py       # Providers initialization
│   │   │   └── qdrant_provider.py # Qdrant vector DB implementation
│   │   └── __init__.py           # Vector DB module initialization
│   ├── .env.example              # Environment variables template
│   ├── .gitignore                # Git ignore file
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

Navigate to the interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 3. Basic Workflow

The typical workflow involves these steps:

1. **Create a Project** - Organize your documents into projects
2. **Upload Documents** - Add PDF or text files to your project
3. **Process Documents** - Convert documents into searchable chunks
4. **Index Vectors** - Create embeddings and store them in the vector database
5. **Perform RAG Queries** - Ask questions and get contextual responses

### 4. Available API Endpoints

#### Base Endpoints

**`GET /api/v1/`** - Root endpoint
- Returns application name and version

**`GET /api/v1/health`** - Health check endpoint
- Returns application health status

#### Project Management

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

#### Asset Management

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

#### Document Processing

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

#### Vector Operations

**`POST /api/v1/p/{project_id}/vectors/index`** - Index document vectors
- **Required**: `project_id` (path parameter)
- **Optional**: `reset` (boolean, default: false)
- **Response**: 201 Created on success, 404/500 for errors

**`POST /api/v1/p/{project_id}/vectors/query`** - Query similar vectors
- **Required**: `project_id` (path parameter), `query` (string)
- **Optional**: `top_k` (integer, default: 5, min: 1), `threshold` (float, range: 0.0-1.0)
- **Response**: 200 OK with results and count

#### RAG Operations

**`POST /api/v1/p/{project_id}/rag/generate`** - Generate RAG response
- **Required**: `project_id` (path parameter), `query` (string)
- **Optional**:
  - `top_k` (integer, default: 5, min: 1)
  - `threshold` (float, range: 0.0-1.0)
  - `temperature` (float, range: 0.0-2.0)
  - `max_output_tokens` (integer, min: 1)
- **Response**: 202 Accepted with response, citations, and contexts

### 5. Request/Response Examples

#### Project Creation
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

#### Document Processing
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

#### Vector Indexing
**`POST /api/v1/p/1867260d-cf8e-4535-9441-54988ad100e3/vectors/index`**

**Request Body:**
```json
{
  "reset": false
}
```

#### RAG Query
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

#### Common Parameters

| Parameter | Type | Description | Default | Range/Notes |
|-----------|------|-------------|---------|-------------|
| `project_id` | string | Project identifier | - | Path parameter |
| `file_id` | string | File/asset identifier | - | Usually filename |
| `asset_id` | string | Asset identifier | - | System-generated |
| `chunk_size` | integer | Document chunk size | 300 | Min: 1 |
| `chunk_overlap` | integer | Overlap between chunks | 40 | Min: 0 |
| `top_k` | integer | Number of results to return | 5 | Min: 1 |
| `threshold` | float | Similarity threshold | - | Range: 0.0-1.0 |
| `temperature` | float | LLM response creativity | - | Range: 0.0-2.0 |
| `max_output_tokens` | integer | Maximum response tokens | - | Min: 1 |
| `reset` | boolean | Reset index before indexing | false | - |
| `skip` | integer | Number of items to skip | 0 | For pagination |
| `limit` | integer | Maximum items to return | varies | Max limits vary by endpoint |

### 7. Best Practices

#### Document Upload
- Use descriptive file names for better organization
- Ensure PDF files have selectable text (not scanned images)
- Supported formats: PDF (.pdf) and Text (.txt) files

#### Document Processing
- Adjust `chunk_size` based on document type (300-1000 for most documents)
- Use appropriate `chunk_overlap` (10-20% of chunk_size) to maintain context
- Process documents before attempting to index vectors

#### Vector Operations
- Always process documents before indexing vectors
- Use `reset: true` when you want to completely rebuild the index
- Query vectors to test retrieval before using RAG

#### RAG Queries
- Start with higher similarity thresholds (0.7-0.8) for precise matches
- Lower thresholds (0.5-0.6) for broader topic exploration
- Adjust `top_k` based on query complexity (3-5 for simple, 5-10 for complex)
- Fine-tune `temperature` for desired response style (0.1-0.3 for factual, 0.7-1.0 for creative)

### 8. Common Response Codes

| Code | Description | When It Occurs |
|------|-------------|----------------|
| 200 | OK | Successful GET requests |
| 201 | Created | Successful POST operations (creation/processing) |
| 202 | Accepted | Successful RAG generation |
| 204 | No Content | Successful DELETE operations |
| 400 | Bad Request | Invalid file format or parameters |
| 404 | Not Found | Project/asset/file not found |
| 422 | Validation Error | Invalid request body structure |
| 500 | Internal Server Error | Processing failures, missing templates |

### 9. Error Messages

The application uses standardized error messages through `ResponseSignals`. Common error messages include:

- `PROJECT_NOT_FOUND` - The specified project doesn't exist
- `ASSET_NOT_FOUND` - The specified asset/file doesn't exist
- `DOCUMENT_PROCESSING_FAILED` - Document processing failed
- `VECTOR_INDEXING_FAILED` - Vector indexing operation failed
- `VECTOR_INDEX_NOT_FOUND` - No vector index exists for the project
- `VECTOR_INDEX_EMPTY` - Vector index exists but has no vectors
- `RAG_GENERATION_FAILED` - RAG response generation failed
- `CHUNK_NOT_FOUND` - No document chunks found

### 10. Troubleshooting

#### Common Issues

**Upload failures (400):**
- Verify file format is PDF or TXT
- Check file is not corrupted
- Ensure project exists before uploading

**Processing errors (500):**
- Confirm uploaded file is readable (for PDFs, text must be selectable)
- Verify asset exists in the project
- Check application logs for detailed error information

**Vector indexing failures:**
- Ensure documents have been processed into chunks first
- Check that chunks exist for the project
- Verify embedding model is properly configured

**Empty RAG responses:**
- Confirm vector index exists and contains vectors
- Try lowering similarity threshold (0.5-0.6)
- Ensure query relates to document content
- Check that LLM provider is properly configured with valid API keys

**Template errors in RAG:**
- Verify template files exist in `src/llm/templates/locales/en/`
- Check template controller configuration
- Review application logs for missing template errors

#### Getting Help

For detailed error information:
- Check the interactive API documentation at http://localhost:8000/docs
- Review application logs in `src/assets/logs/app.log`
- Use the "Try it out" feature in Swagger UI for testing endpoints
- Check MongoDB and application status with `docker-compose logs`
- Verify environment configuration matches requirements

## Future Work
   - Add support for local [Unstructured Loader](https://python.langchain.com/docs/integrations/document_loaders/unstructured_file/)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
