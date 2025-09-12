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

### 2. Clone the Repository

```bash
git clone https://github.com/AbdElrahman-A-Eid/lite-rag-app.git
cd lite-rag-app
```

### 3. Create and Activate Conda Environment

```bash
# Create a new conda environment with Python 3.12
conda create -n lite-rag python=3.12

# Activate the environment
conda activate lite-rag
```

### 4. Install Dependencies

```bash
# Install project dependencies
pip install -r requirements.txt
```

## Environment Configuration

1. Create your environment file from the template:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your specific values:
   ```bash
   nano .env
   # or use your preferred text editor
   ```

**Environment Variables:**
- `RAG_APP_NAME`: Name of your RAG application (default: Lite-RAG-App)
- `RAG_APP_VERSION`: Current version of the application (default: 0.1.0)

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

