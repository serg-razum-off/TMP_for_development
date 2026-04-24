#!/bin/bash
# Start Redis
redis-server &

# Start Celery Worker
celery -A myproject worker --loglevel=info &

# Start Celery Beat
celery -A myproject beat --loglevel=info