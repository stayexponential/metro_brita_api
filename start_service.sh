#!/bin/bash

# Script to start the FastAPI application with Gunicorn

# Activate the virtual environment (if applicable)
# Uncomment the following line and adjust the path if using a virtual environment
# source venv/bin/activate

# Set default values for host and port if not provided
HOST="${1:-0.0.0.0}"
PORT="${2:-8000}"

# Run Gunicorn with the specified configuration file
echo "Starting Gunicorn server on ${HOST}:${PORT}..."

gunicorn app.main:app -c gunicorn_config.py --bind ${HOST}:${PORT}

# End of script