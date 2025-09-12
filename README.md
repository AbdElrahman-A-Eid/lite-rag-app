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
RAG_APP_VERSION=0.1.0
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
| `RAG_APP_VERSION` | Application version | 0.1.0 | No |
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

*Coming soon - usage instructions will be added as the project develops*

## Future Work
   - Add support for local [Unstructured Loader](https://python.langchain.com/docs/integrations/document_loaders/unstructured_file/)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

