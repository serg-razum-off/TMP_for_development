# Tech Stack

## Core Language & Runtime
* **Python**: 3.12
* **Environment**: `venv` / Docker

## Frameworks & Databases
* **Django**: 6.0.3 (Core monolith)
* **FastAPI**: Lightweight microservice for order streaming
* **Database**: SQLite3 (development)
* **Validation**: Pydantic (used in FastAPI service)

## Background Processing (Planned)
* **Celery**: For executing asynchronous background tasks
* **Redis**: As the message broker for Celery and caching layer

## Infrastructure & Deployment
* **Docker**: Containerization using `Dockerfile`
* **Docker Compose**: Service orchestration via `docker-compose.yml`

## Testing & Quality
* **Testing Framework**: Django built-in `TestCase`
* **Focus**: Model and View test coverage, database hit limits, API/UI boundary tests.

## Key Middlewares
* **RequestTelemetryMiddleware**: Custom middleware that injects execution time and request ID into response headers.
