# Glossary

## Core Project Terminology
*   **Order Entity**: The central unit of data in the system, representing a customer request with a title, amount, and status.
*   **CBV (Class-Based View)**: A Django pattern for defining views as classes rather than functions, allowing for better code reuse through inheritance and mixins.
*   **N+1 Problem**: A performance bottleneck where a single request triggers a cascade of database queries (e.g., 1 query for a list of orders, then N additional queries to fetch the user for each order).
*   **Query Optimization**: The practice of using `select_related()` (SQL JOIN) or `prefetch_related()` (Python-side join) to eliminate additional database round-trips.
*   **Request-ID**: A unique UUID assigned to every incoming request for tracing throughout the application lifecycle.
*   **Telemetry Middleware**: Custom logic (`RequestTelemetryMiddleware`) that measures request performance and injects metadata into HTTP headers.

## Architectural Governance
*   **Orchestrator Protocol (OP)**: The documentation-driven development and governance model used to manage this project. It enforces constraints through the `/orchestrator/` directory files.
*   **Context Temperature Matrix**: A classification of files into **HOT** (active execution), **WARM** (mental model/safety), and **COLD** (deep reference), determining how the AI agent reads and updates project context.
*   **WARM Context**: Foundational documents like `security.md`, `tech-stack.md`, and `ARCHITECHT_GUIDE.md` that establish boundaries and development rules.
*   **HOT Context**: The immediate task state held in `todo.json` and the architectural blueprint in `plan.md`.
*   **Milestone Track**: A focused unit of work (e.g., "Migration to Celery") tracked in `tracks.md` and containing its own plan and tasks.

## Security Terminology
*   **Zero-Trust Input**: The mandate to treat all external data (User input, external API results) as untrusted and potentially malicious strings.
*   **Directive Detection**: The security practice of scanning external content for imperative commands intended to override the agent's system prompt or boundaries.
*   **CSRF (Cross-Site Request Forgery)**: A type of attack where a malicious site tricks a user's browser into performing actions on a different site where the user is authenticated.
