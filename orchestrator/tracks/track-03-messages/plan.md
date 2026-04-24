# Plan: track-03-messages

## Objective
Implement a `UserMessage` (Notification) system to inform users about important events in their account, specifically focusing on updates to their orders (e.g., status changes or order creation).

## Domain Model
### `UserMessage` (New Model)
- `user`: ForeignKey(User, related_name="messages")
- `order`: ForeignKey(Order, related_name="messages", null=True, blank=True)
- `message_body`: TextField()
- `is_read`: BooleanField(default=False)
- `created_at`: DateTimeField(auto_now_add=True)

### `Order` (Model Update)
- `created_by`: ForeignKey(User, related_name="created_orders", null=True, blank=True, on_delete=models.SET_NULL)

## Architecture & Logic
- **Data Integrity**: Messages belong to a User. Deleting an Order can cascade and delete specific order-related messages, but User deletion will definitely cascade.
- **Message Generation**: 
  - **Status Change**: Upon `save()`, if the status has changed, create a `UserMessage` for `self.user`.
  - **Cross-User Creation**: Upon `save()`, if it's a new order (`is_new`) AND `self.user != self.created_by`, create a `UserMessage` for `self.user` notifying them that an order was created for them.
- **Query Optimization**: Fetching user messages should run a simple query. If displaying related orders, `select_related('order')` should be used.

## UI & Templates
- **Messages Inbox View**: Create a new Class-Based View (`MessageListView`) to display all messages for the `request.user`.
- **Navigation/Header**: Add an unread message indicator (e.g., a badge) in the base template/navigation bar, requiring a custom context processor or a simple template tag to fetch `unread_count`.
- **Read Action**: Provide an explicit button on each unread message to mark it as read. This will hit a dedicated endpoint (`/messages/<id>/read/`) that updates the status and redirects back to the inbox.
## Verification
- **Automated Tests**:
    - Test that creating an order creates a message.
    - Test that changing an order's status triggers a new message.
    - Test query limits when loading the messages list (N+1 query checks).
- **Manual**:
    - Check the messages inbox UI.
    - Change order status via the UI and verify a new unread message appears.
