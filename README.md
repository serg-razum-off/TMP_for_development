
## 🏗 Architecture Overview
The project follows the standard Django "Project vs. App" philosophy, utilizing Class-Based Views (CBVs) and optimized database queries.

* **Tech Stack:** Python 3.12, Django 6.0.3, SQLite3, and **FastAPI**.
* **Core App:** `orders` — handles order entities and their relationships with users.
* **Optimization:** Uses `select_related('user')` in views to solve the N+1 query problem by performing SQL JOINs.
* **Telemetry:** Includes custom `RequestTelemetryMiddleware` to track request IDs and execution time via response headers.

---

## 🚀 Getting Started with Docker

This project is fully containerized using Docker and Docker Compose for a consistent development environment.

### Prerequisites
* Docker and Docker Compose installed on your machine.

### Services
The `docker-compose.yml` file defines two primary services:
* **`web`**: Build from the local `Dockerfile`, runs the Django application, and exposes port **8000**.
* **`streaming_api`**: Builds the FastAPI application and exposes port **8002** for receiving remote order drafts.

### Commands
From the project root directory, use the following commands:

1.  **Build and Start the Containers:**
    ```bash
    docker compose up --build
    ```
2.  **Run in Detached Mode:**
    ```bash
    docker compose up -d
    ```
3.  **Stop the Containers:**
    ```bash
    docker compose down
    ```

---

## 📱 Mobile Order Streaming API (FastAPI)

To emulate remote agents (e.g., mobile apps) sending order drafts, the project includes a simplified FastAPI microservice.

### Endpoint: `POST /create_order`
**URL:** `http://localhost:8002/create_order`

### Usage Example (curl):
```bash
curl -X POST "http://localhost:8002/create_order" \
     -H "Content-Type: application/json" \
     -d '{"user_id": 1, "created_by_id": 2, "comment": "Order draft from mobile agent"}'
```

### Interactive Documentation (Browser)
FastAPI provides an interactive UI for testing the API directly in your browser:
- **Swagger UI**: `http://127.0.0.1:8002/docs` — Click on **POST /create_order**, then **Try it out** to send requests without using `curl`.
- **Redoc**: `http://127.0.0.1:8002/redoc` — For more structured documentation.

### Persistence
Received orders are automatically appended to the `./orders/streaming/stream_orders.jsonl` file in the JSON Lines format for later ingestion into the main Django database.

---

## 🛠 Database & Migrations

The project uses SQLite3 as its primary database for development. Before the application can function correctly, you must apply the initial database schema.

### Applying Migrations
To create the necessary database tables (including the `Order` model and Django's built-in `User` system), run:

```bash
# Using Docker
docker-compose exec web python manage.py migrate

# Local environment (if not using Docker)
python manage.py migrate
```

### Creating a Superuser
To access the Django Admin panel at `/admin/`, create an administrative account:
```bash
docker-compose exec web python manage.py createsuperuser
```

---

## 📂 Project Structure
The following reflects the current organization of the codebase:

* `manage.py`: Command-line utility for administrative tasks.
* `myproject/`: Configuration folder containing `settings.py` and root `urls.py`.
* `orders/`: The primary feature application.
    * `models.py`: Defines the `Order` entity with fields like `title`, `amount`, and `status`.
    * `views.py`: Logic for rendering order lists using CBVs.
    * `middleware.py`: Custom logging and telemetry logic.
    * `templates/orders/`: Namespaced HTML templates.
    * `streaming/`: FastAPI microservice for order ingestion.
        * `main.py`: FastAPI app and routes.
        * `schemas.py`: Pydantic validation models.
        * `stream_orders.jsonl`: Local storage for ingested drafts.
* `Dockerfile` & `docker-compose.yml`: Infrastructure as code for containerization.

---

## 🚀 Mobile Order Synchronization with Celery

### Background
The project uses Celery to process mobile order drafts from the streaming service. This provides an asynchronous, scalable solution for handling order ingestion from remote sources.

### Components
* **Task:** `process_mobile_orders` in `orders/tasks.py`
* **Frequency:** Runs every 30 seconds
* **Storage:** `orders/streaming/stream_orders.jsonl`

### Running Celery Services
To start the Celery worker and beat scheduler:

```bash
# Using Docker (Recommended)
docker-compose exec web celery -A myproject worker --loglevel=info &
docker-compose exec web celery -A myproject beat --loglevel=info &

# Local Development
celery -A myproject worker --loglevel=info &
celery -A myproject beat --loglevel=info &
```

### Monitoring Order Processing
* **User Lookup Endpoint:** `http://127.0.0.1:8000/orders/users/lookup/`
* **Processing Logs:** Check `orders_processing.log`
* **Error Notifications:** View in Django User Messages (`/orders/messages/`)

### Order Draft Workflow
1. Send order draft via FastAPI streaming service
2. Draft stored in `stream_orders.jsonl`
3. Celery task picks up draft every 30 seconds
4. Converts draft to Django Order with status `DRAFT`
5. Generates dynamic order title using usernames
6. Sends error notifications if processing fails

---

## 📝 Development Notes
* **Starting Page:** `http://127.0.0.1:8000/` -- redirect to order list.
* **Admin Panel:** `http://127.0.0.1:8000/admin/` once a superuser is created.
* **Order List:** `http://127.0.0.1:8000/orders/`.
* **FastAPI Docs:** `http://127.0.0.1:8002/docs`.
* **Environment Variables:** Currently, the `SECRET_KEY` is hardcoded for teaching purposes; it should be moved to a `.env` file for production.
