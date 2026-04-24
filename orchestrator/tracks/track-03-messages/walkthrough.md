# Walkthrough — Track 3: User Notifications & Messages

This track implemented a comprehensive notification system and enforced data isolation for users, significantly improving the security and usability of the platform.

## Key Accomplishments

### 1. In-App Notification System
- **`UserMessage` Model**: Created a dedicated model for storing user alerts, linked to specific orders.
- **Automated Triggers**: 
    - **Status Updates**: Users are automatically notified when their order status changes.
    - **Staff Delegated Orders**: Users receive a "Welcome" notification if a staff member creates an order on their behalf.
- **Inbox Interface**: A new message list view allows users to manage their alerts and mark them as read.

### 2. Data Isolation & Security
- **Owner-Only Access**: Non-staff users are now strictly restricted to seeing and managing only their own data.
- **Role-Based Logic**: 
    - Staff members retain global visibility for management purposes.
    - Security implemented at the `QuerySet` level in Class-Based Views to ensure "Blind Spots" for unauthorized data.
- **Audit Tracking**: Added the `created_by` field to the `Order` model to track who initiated migrations or updates.

### 3. Performance & Templates
- **Context Processor**: Implemented an unread message count global variable for the navigation bar.
- **Optimized Queries**: Used `select_related('order')` for message lists to ensure high performance even under heavy notification load.

## Verification Highlights

### Automated Testing
- Verified `UserMessage` creation logic in `test_models.py`.
- Verified isolation logic (User A cannot see User B's orders) in `test_views.py`.
- Verified that Staff can still access all data for support tasks.

### Manual Verification
1. Logged in as `testuser` → successfully saw only `Test Order`.
2. Changed status to `completed` → confirmed a new unread message appeared in the inbox.
3. Marked message as read → confirmed count decreased.

> [!NOTE]
> All mutating views (Create, Update, Delete) now have `LoginRequiredMixin` and ownership checks, making the application production-ready for multi-tenant usage.
