Here is a concise architectural overview of the current codebase, designed to quickly onboard any developer or AI agent.

### **Project Architecture & Context**

**1. Tech Stack & Environment**
* **Runtime:** Python 3.12.
* **Framework:** Django 6.0.3.
* **Database:** SQLite3 (Development default, configured in `settings.py`).
* **Infrastructure:** Containerized via Docker (`python:3.12-slim` base) and managed with `docker-compose`, exposing port 8000. 

**2. Core Domain & Applications**
* **`myproject`:** The standard Django configuration module containing `settings.py`, `urls.py`, and `wsgi.py`.
* **`orders`:** The primary domain application focused on order management.

**3. Data Models (`orders/models.py`)**
* **`Order`:** The central entity. It establishes a Many-to-One relationship (`ForeignKey`) with Django's built-in `User` model.
    * **Fields:** `title`, `amount` (`DecimalField`), `status` (Choices: pending, completed, cancelled), `created_at`, `updated_at`, and an `is_active` boolean flag.

**4. Routing & Views**
* **Endpoints:** The core functionality is routed through `/orders/`.
* **Views:** Utilizes Django's Class-Based Views (CBVs). Specifically, an `OrderListView` retrieves a `QuerySet` of orders. 
* **Optimization:** The view correctly employs `.select_related("user")` to prevent the N+1 query problem when rendering user data alongside orders.

**5. Additional Artifacts**
* **Middleware (`middleware.py`):** * **`SimpleLoggingMiddleware`:** A basic component that logs the request path to the console.
    * **`RequestTelemetryMiddleware`:** A performance monitoring tool that generates a unique `X-Request-ID` (UUID) for every request and calculates the total execution time. It injects these values into the response headers (`X-Request-ID`, `X-Execution-Time-Seconds`) and prints them to the console.
    * **Note:** These are currently omitted from the `MIDDLEWARE` list in `settings.py`.
* **Tooling:** An `.obsidian` directory is present, indicating that markdown-based documentation or note-taking is maintained alongside the codebase.
