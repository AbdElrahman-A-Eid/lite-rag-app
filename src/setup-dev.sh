#!/bin/bash

echo "Setting up development environment..."

# Install development dependencies
pip install -r src/requirements-dev.txt

# Install pre-commit hooks
pre-commit install

echo "Running pre-commit on all files..."
pre-commit run --all-files

echo "Development environment setup complete!"
echo ""
echo "Available commands:"
echo "  pre-commit run --all-files  # Run all hooks"
echo "  pre-commit run black        # Run just black"
echo "  pre-commit autoupdate       # Update hook versions"
