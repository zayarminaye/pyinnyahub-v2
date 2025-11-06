"""
Gunicorn configuration for production deployment.
Optimized for Render.com free tier (512MB RAM).
"""
import multiprocessing

# Bind to the port Render provides
bind = "0.0.0.0:10000"

# Worker configuration
# For 512MB RAM, 2 workers is safe (each worker uses ~100-150MB)
workers = 2
worker_class = "sync"
worker_connections = 1000
max_requests = 1000  # Restart workers after 1000 requests to prevent memory leaks
max_requests_jitter = 50  # Add randomness to prevent all workers restarting at once

# Timeout settings
timeout = 120  # 2 minutes - increase from default 30s
graceful_timeout = 30
keepalive = 5

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "info"

# Process naming
proc_name = "pyinnyahub-lms"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (not needed on Render, they handle it)
keyfile = None
certfile = None
