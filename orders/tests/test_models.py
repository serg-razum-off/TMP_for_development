from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Order, Inventory, OrderItem, UserMessage, OrderStatus

class InventoryOrderModelTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username='testuser', password='password')
        self.inventory_item = Inventory.objects.create(name='Gadget', price=10.00)
        self.order = Order.objects.create(user=self.user, title='Test Order')
        self.order_item = OrderItem.objects.create(order=self.order, inventory=self.inventory_item, quantity=2)

    def test_item_line_total(self) -> None:
        """Tests that line total is correctly calculated as price * quantity."""
        self.assertEqual(self.order_item.line_total, 20.00)

    def test_order_amount_calculation(self) -> None:
        """Tests that Order.recalculate_total accurately sums all order items."""
        self.order.recalculate_total()
        self.assertEqual(self.order.amount, 20.00)
        
        # Add another item
        item2 = Inventory.objects.create(name='Widget', price=5.00)
        OrderItem.objects.create(order=self.order, inventory=item2, quantity=1)
        self.order.recalculate_total()
        self.assertEqual(self.order.amount, 25.00)

    def test_prefetch_related_items(self) -> None:
        """Tests that prefetch_related reduces queries for items and inventory."""
        # Accessing items should not trigger extra queries if prefetched
        # Expect 3 queries: 1 for Order, 1 for Items, 1 for Inventory
        with self.assertNumQueries(3):
            order = Order.objects.prefetch_related('items__inventory').get(pk=self.order.pk)
            for item in order.items.all():
                _ = item.inventory.name
                _ = item.inventory.price

class UserMessageModelTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username='msguser', password='password')
        self.order = Order.objects.create(user=self.user, title='Monitor Order')

    def test_message_created_on_status_change(self) -> None:
        """Tests that a UserMessage is created when an order status is updated."""
        initial_count = UserMessage.objects.filter(user=self.user).count()
        self.assertEqual(initial_count, 0)

        # Update status
        self.order.status = OrderStatus.COMPLETED
        self.order.save()

        self.assertEqual(UserMessage.objects.filter(user=self.user).count(), 1)
        msg = UserMessage.objects.filter(user=self.user).first()
        self.assertIn(OrderStatus.COMPLETED.label, msg.message_body)
        self.assertEqual(msg.order, self.order)

    def test_no_message_on_save_without_status_change(self) -> None:
        """Tests that saving without status change doesn't create a message."""
        self.order.title = 'Updated Title'
        self.order.save()
        self.assertEqual(UserMessage.objects.filter(user=self.user).count(), 0)

    def test_no_message_on_order_creation(self) -> None:
        """Tests that initial creation doesn't trigger a 'status change' message."""
        new_order = Order.objects.create(user=self.user, title='New Order', created_by=self.user)
        # Check that no message was created for THIS order creation (logic handles status transitions only)
        self.assertEqual(UserMessage.objects.filter(user=self.user, order=new_order).count(), 0)

    def test_message_on_cross_user_order_creation(self) -> None:
        """Tests that a notification is created when User A creates an order for User B."""
        user_a = User.objects.create_user(username='usera', password='password')
        initial_count = UserMessage.objects.filter(user=self.user).count()
        
        Order.objects.create(user=self.user, title='Surprise Gift', created_by=user_a)
        
        self.assertEqual(UserMessage.objects.filter(user=self.user).count(), initial_count + 1)
        msg = UserMessage.objects.filter(user=self.user).order_by('-created_at').first()
        self.assertIn('for you by usera', msg.message_body)
