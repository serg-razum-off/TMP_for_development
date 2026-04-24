# Testing Strategy

The `Order Management` project utilizes Django's built-in testing framework (`django.test.TestCase`) to ensure model integrity, view performance, and telemetry accuracy.

## Tiers of Testing

### 1. Model Tests (`orders/tests/test_models.py`)
Focuses on data integrity and validation.
- **Entity Creation**: Ensures `Order` instances are correctly saved with valid statuses.
- **Relationships**: Verifies the ForeignKey link to the `User` model.
- **Constraints**: Checks that mandatory fields (title, amount) trigger validation errors when missing.

### 2. View & UI Tests (`orders/tests/test_views.py`)
Utilizes Django's `Client` to simulate web interactions with Class-Based Views.
- **List Consistency**: Ensures `OrderListView` renders all available orders correctly.
- **Authentication**: Verifies that protected views redirect unauthorized users.
- **N+1 Prevention**: Uses `assertNumQueries` to verify that `select_related` is functioning and queries remain constant regardless of the number of orders.

### 3. Middleware & Telemetry Tests
Tests the `RequestTelemetryMiddleware` logic.
- **Header Injection**: Verifies that `X-Request-ID` and `X-Execution-Time` are present in response headers.
- **Performance Logging**: Ensures execution time is calculated and logged correctly.

## Mandatory Patterns

### 🏛️ Entity Isolation
Each test should ideally create its own data using `setUp()` or `setUpTestData()` to ensure isolation. Tests must verify that users can only see their own orders (if such logic is implemented) or that data is correctly scoped.

### 🧪 Query Optimization Checks
Every view test involving lists MUST include a query count check.
```python
def test_order_list_performance(self):
    # Setup multiple orders
    with self.assertNumQueries(1): # Should be 1 query for all orders due to select_related
        response = self.client.get(reverse('order-list'))
        self.assertEqual(response.status_code, 200)
```

## Execution
Run all tests using the Docker environment:
```bash
docker-compose exec web python manage.py test
```

Or locally (if configured):
```bash
python manage.py test
```

Required coverage: **>90%** for core logic in `orders` app.
