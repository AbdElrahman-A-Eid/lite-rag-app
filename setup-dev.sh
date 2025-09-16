#!/bin/bash

echo "Setting up development environment..."

# Check if we're in the right directory and adjust paths accordingly
if [ -f "requirements-dev.txt" ]; then
    # We're in the src directory
    echo "Running from src/ directory..."
    pip install -r requirements-dev.txt
    cd ..
elif [ -f "src/requirements-dev.txt" ]; then
    # We're in the project root
    echo "Running from project root..."
    pip install -r src/requirements-dev.txt
else
    echo "Error: requirements-dev.txt not found!"
    echo "Please run this script from either:"
    echo "  - Project root: ./src/setup-dev.sh"
    echo "  - src directory: ./setup-dev.sh"
    echo "Current directory: $(pwd)"
    exit 1
fi

echo "Installing pre-commit hooks..."
pre-commit install

echo "Running pre-commit on all files..."
pre-commit run --all-files

echo "Development environment setup complete!"
echo ""
echo "Available commands:"
echo "  pre-commit run --all-files  # Run all hooks"
echo "  pre-commit run black        # Run just black"
echo "  pre-commit autoupdate       # Update hook versions"
echo ""
echo "Happy coding!"
