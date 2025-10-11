#!/bin/bash

# This script sets up the project environment for the GCP Modules Organizer.

# Exit immediately if a command exits with a non-zero status.
set -e

# Function to install dependencies
install_dependencies() {
    echo "Installing dependencies..."
    npm install
}

# Function to set up the project structure
setup_project_structure() {
    echo "Setting up project structure..."
    mkdir -p src/services src/models src/utils src/config templates/module-template
}

# Function to initialize Git repository
initialize_git() {
    echo "Initializing Git repository..."
    git init
}

# Main setup function
main() {
    install_dependencies
    setup_project_structure
    initialize_git
    echo "Project setup complete."
}

# Execute the main function
main