# Core Processes Outline

This document describes the high-level workflow of the Order Management application, from request ingestion to data persistence and telemetry reporting.

## 1. Request Ingestion & Telemetry Startup
1. **HTTP Request**: A user or external system initiates a request (e.g., `GET /orders/`).
2. **Middleware Activation**: The `RequestTelemetryMiddleware` intercepts the request.
    *   **Timer Starts**: It records the exact start time.
    *   **Request ID**: It checks for an existing `X-Request-ID` header or generates a new unique UUID.
3. **Execution Context**: The middleware passes the request to the Django URL dispatcher.

## 2. URL Dispatching & View Processing
1. **Routing**: Django matches the URL path to a specific Class-Based View (e.g., `OrderListView`).
2. **View Execution**: The CBV's `get()` or `dispatch()` method is invoked.
3. **Optimized Data Retrieval**:
    *   The view executes an ORM query: `Order.objects.select_related('user').all()`.
    *   **SQL JOIN**: The database performs a single join between the `Order` and `User` tables.
    *   **Result Set**: Data is returned to the Django application in a single round-trip.

## 3. Template Rendering
1. **Context Preparation**: The view populates the context dictionary with the retrieved order list.
2. **Template Loading**: Django loads the appropriate namespaced template (e.g., `orders/order_list.html`).
3. **DOM Generation**: The template engine renders the HTML, iterating through orders and efficiently accessing `order.user.username` without triggering additional queries.

## 4. Response Finalization & Telemetry Injection
1. **Response Capture**: The rendered HTML response is passed back up through the middleware stack.
2. **Metric Calculation**: The `RequestTelemetryMiddleware` calculates the total execution duration.
3. **Header Injection**:
    *   `X-Execution-Time`: Total time in milliseconds.
    *   `X-Request-ID`: The unique identifier for this transaction.
4. **Delivery**: The finalized HTTP response is delivered to the client browser.

## 5. Persistence Operations (CRUD)
1. **Validation**: When creating or updating (e.g., `POST /orders/create/`), the view validates the `OrderForm`.
2. **Commit**: Upon successful validation, the ORM issues an `INSERT` or `UPDATE` statement to the SQLite3 database.
3. **Redirect**: Standard Django pattern (PRG - Post/Redirect/Get) redirects the user back to the order listing after a successful write.

## 6. Order Streaming Process (FastAPI Microservice)
This process handles remote order ingestion independently of the main Django monolith.
1. **Remote Request**: A remote agent (e.g., mobile app) sends a `POST /create_order` request to the FastAPI service on port `8002`.
2. **Pydantic Validation**: The FastAPI service validates the incoming JSON payload against the `OrderDraft` Pydantic schema.
    *   On **invalid** payload: Returns a `422 Unprocessable Entity` response immediately.
3. **JSONL Persistence**: On successful validation, the service appends the order draft as a single JSON line to `orders/streaming/stream_orders.jsonl`.
4. **Acknowledgement**: Returns a `200 OK` response to the requesting agent confirming the draft was saved.
5. **Future Ingestion**: The `.jsonl` file acts as a recoverable queue; a separate process or manual step can later import these drafts into the primary SQLite3 database.
