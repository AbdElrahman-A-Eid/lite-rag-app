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

- Python 3.12 (or later)
- Anaconda or Miniconda
- Git

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
├── assets/              # Static assets and resources
├── .env.example         # Environment variables template
├── .gitignore          # Git ignore file
├── requirements.txt     # Python dependencies
├── README.md           # Project documentation
└── LICENSE             # MIT License
```

## Usage

*Coming soon - usage instructions will be added as the project develops*

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

