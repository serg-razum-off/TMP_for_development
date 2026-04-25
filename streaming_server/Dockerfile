FROM python:3.12-slim

WORKDIR /app

# Copy root requirements.txt from parent directory
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure the streaming directory exists and is owned by the user
RUN mkdir -p /app/orders/streaming && \
    useradd -m appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose port 8001 (to avoid conflict with Django's 8000)
EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
