# gunicorn_config.py

# Server socket
bind = "0.0.0.0:8011"  # Bind to all interfaces on port 8000

# Worker Options
workers = 4  # Number of worker processes, adjust based on your CPU cores
worker_class = "uvicorn.workers.UvicornWorker"  # Use Uvicorn's worker class for ASGI support

# Logging
loglevel = "debug"  # Log level can be adjusted as needed (info, warning, error)
accesslog = "-"  # Log access requests to stdout
errorlog = "-"   # Log errors to stdout