# Track 05: Mobile Order Synchronization with Celery

## Objectives
- Implement Celery task to monitor mobile order drafts
- Create user lookup endpoint
- Create order creation endpoint from streaming JSONL
- Implement error notification mechanism

## Key Components
1. Celery Task
   - Monitor orders/streaming/stream_orders.jsonl
   - Process records one by one
   - Handle successful and failed order creations

2. Django Endpoints
   - User Lookup Endpoint: Retrieve username by user ID
   - Order Creation Endpoint: Create orders from mobile drafts

3. Error Handling
   - Create UserMessage for failed order processing
   - Notify created_by user with error details

## Implementation Notes
- Use OrderStatus.DRAFT for new orders
- Generate dynamic order title
- Remove processed records from JSONL