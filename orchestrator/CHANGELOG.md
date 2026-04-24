# Changelog

All notable changes to the Order Management project will be documented in this file.

## [Unreleased]
### Added
- **Track 2: Inventory & Order Items Bridge**
    - `Inventory` model for product catalog management.
    - `OrderItem` bridge model allowing multiple items per order with quantity tracking.
    - Inline formsets for unified Order/Item creation/editing.
- **Track 3: User Notifications & Messages**
    - `UserMessage` model for in-app notifications.
    - Notification triggers in `Order.save()` for status changes and cross-user order creation.
    - **Data Isolation**: Entity-level access control ensuring regular users only see their own orders/messages.
    - Staff-only capabilities to create orders for other users.
- Functional Orchestrator Protocol governance in the `/orchestrator/` directory.
- Detailed technical stack documentation reflecting Django 6.0.3 and Python 3.12.
- Security and code-style guidelines tailored for Django performance and safety.
- Roadmap for upcoming Celery/Redis background task implementation.

### Fixed
- N+1 query issue in Order list and detail views using `select_related` and `prefetch_related`.
- JavaScript `NaN$` calculation bug in the order form by fixing `json_script` data types.
- Request telemetry and ID tracking middleware.
