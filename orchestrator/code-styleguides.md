# Code Styleguides

Code changes must comply with the following structural and stylistic constraints for the Order Management Django project.

## 1. Django Best Practices
*   **Class-Based Views (CBV)**: Prefer CBVs for standard CRUD operations to maintain consistency and leverage Django's built-in mixins.
*   **Thin Views, Fat Models**: Keep business logic within model methods or service layers, keeping views primarily responsible for request/response handling and context preparation.
*   **Query Optimization**: Every query involving related objects MUST use `select_related()` (for ForeignKeys/OneToOne) or `prefetch_related()` (for ManyToMany/Reverse ForeignKeys) to prevent N+1 performance degradation.

## 2. Type Hinting & Documentation
*   **Public Methods**: All public methods and functions must have thorough Python docstrings and complete parameter/return Type Hints.
*   **Template Consistency**: Use namespaced templates (e.g., `orders/templates/orders/order_list.html`) to avoid collision with other apps.

## 3. File Organization
*   **App Logic**: Business logic remains inside the `orders/` application folder.
*   **Project Config**: Global settings and root URLs reside in the `myproject/` folder.
*   **Orchestration**: System governance and documentation reside in the `orchestrator/` folder.

## 4. Testing & Reliability
*   **Location**: Tests must reside within the `tests/` subdirectory of each app (e.g., `orders/tests/`).
*   **Coverage**: Maintain **>90%** coverage for core business logic.
*   **Query Count Checks**: Mandatory use of `assertNumQueries` in view tests.

## 5. Security Practices
*   **Environment Variables**: Never hardcode secrets like `SECRET_KEY`, database credentials, or third-party API keys.
*   **Template Safety**: Avoid using the `|safe` filter unless the content is strictly sanitized and its use is technically necessary. Use built-in Django form rendering for CSRF protection.
