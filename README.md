
## 🏗 Architecture Overview
The project follows the standard Django "Project vs. App" philosophy, utilizing Class-Based Views (CBVs) and optimized database queries.

* **Tech Stack:** Python 3.12, Django 6.0.3, and SQLite3.
* **Core App:** `orders` — handles order entities and their relationships with users.
* **Optimization:** Uses `select_related('user')` in views to solve the N+1 query problem by performing SQL JOINs.
* **Telemetry:** Includes custom `RequestTelemetryMiddleware` to track request IDs and execution time via response headers.

---

## 🚀 Getting Started with Docker

This project is fully containerized using Docker and Docker Compose for a consistent development environment.

### Prerequisites
* Docker and Docker Compose installed on your machine.

### Services
The `docker-compose.yml` file defines a `web` service that builds from the local `Dockerfile`, mounts the project directory as a volume for live-reloading, and exposes port 8000.

### Commands
From the project root directory, use the following commands:

1.  **Build and Start the Containers:**
    ```bash
    docker-compose up --build
    ```
2.  **Run in Detached Mode:**
    ```bash
    docker-compose up -d
    ```
3.  **Stop the Containers:**
    ```bash
    docker-compose down
    ```

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
* `Dockerfile` & `docker-compose.yml`: Infrastructure as code for containerization.

---

## 📝 Development Notes
* **Starting Page:** `http://127.0.0.1:8000/` -- redirect to order list.
* **Admin Panel:** `http://127.0.0.1:8000/admin/` once a superuser is created.
* **Order List:** `http://127.0.0.1:8000/orders/`.
* **Environment Variables:** Currently, the `SECRET_KEY` is hardcoded for teaching purposes; it should be moved to a `.env` file for production.
