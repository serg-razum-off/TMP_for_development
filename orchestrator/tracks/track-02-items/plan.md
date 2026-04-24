# Plan: track-02-items

## Objective
Implement a simplified `Inventory` model to serve as a catalog of available products, and an `OrderItem` entity that acts as a bridge, allowing each `Order` to contain multiple distinct items from the Inventory.

## Domain Model
### `Inventory` (New Model)
- `name`: CharField (max_length=255)
- `price`: DecimalField (max_digits=10, decimal_places=2)
- `commentary`: TextField (blank=True, null=True)

### `OrderItem` (New Model)
- `order`: ForeignKey(Order, related_name="items")
- `inventory`: ForeignKey(Inventory, related_name="order_usages")
- `quantity`: PositiveIntegerField (default=1)

## Architecture & Logic
- **Relationship**: Many-to-Many between Order and Inventory, facilitated by the `OrderItem` bridge which includes quantities.
- **Data Integrity**: Deleting an Order will cascade delete its OrderItems (but NOT the Inventory).
- **Optimization**: All Order list and detail views displaying items must be updated to use `prefetch_related('items__inventory')` to avoid N+1 queries.
- **Business Logic**: 
    - At this stage, pricing is fetched dynamically via the `inventory` relationship (i.e., `item.inventory.price`). The total `Order.amount` can be derived dynamically.
    - We will keep this as close to standard Django MVT behavior as possible without introducing complex JS logic to formsets.

## UI & Templates
- **Order Detail**: Add a table showing all `OrderItem`s associated with the order. Include references to the `Inventory` prices and line totals.
- **Order Creation/Update**: 
    - **Strategy**: Standard Django Inline Formsets for a unified MVT experience without JS frontend scripts.
- **Order List**: Optionally display the count of items in the list view.

## Verification
- **Automated Tests**:
    - Creation tests ensuring Inventory and OrderItems are linked.
    - Query count validation tests emphasizing `prefetch_related`.
- **Manual**:
    - Verify Inventory objects can be added via Django Admin.
    - Test end-to-end functionality of order creation with multiple items via the standard UI Formset.
