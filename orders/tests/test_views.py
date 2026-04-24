from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from ..models import Order, Inventory, OrderItem, UserMessage

class OrderViewTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username='testuser', password='password')
        self.inventory_item = Inventory.objects.create(name='Gadget', price=10.00)
        self.order = Order.objects.create(user=self.user, title='Test Order')
        self.order_item = OrderItem.objects.create(order=self.order, inventory=self.inventory_item, quantity=2)

    def test_order_detail_view_queries(self) -> None:
        """Tests that OrderDetailView uses prefetch_related and stays within query budget."""
        self.client.login(username='testuser', password='password')
        
        # 1. Order + User (select_related)
        # 2. OrderItem (prefetch_related)
        # 3. Inventory (prefetch_related)
        # 4. Session lookup
        # 5. User auth lookup
        # 6. UserMessage unread count (context processor)
        with self.assertNumQueries(6):
            response = self.client.get(reverse('order_detail', args=[self.order.pk]))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Gadget')
            self.assertContains(response, '10.00$')
            self.assertContains(response, '20.00$')

    def test_create_view_requires_login(self) -> None:
        """Tests that anonymous users are redirected from the create view."""
        response = self.client.get(reverse('order_create'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_order_list_view(self) -> None:
        """Tests the order list view filtering and display."""
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('order_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Order')

    def test_order_create_context(self) -> None:
        """Tests that OrderCreateView provides product_prices as a dict in context."""
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('order_create'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('product_prices', response.context)
        self.assertIsInstance(response.context['product_prices'], dict)
        self.assertEqual(response.context['product_prices'][self.inventory_item.id], 10.0)

class UserMessageViewTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username='msguser', password='password')
        self.client.login(username='msguser', password='password')
        self.msg = UserMessage.objects.create(user=self.user, message_body="Test Message")

    def test_message_list_view(self) -> None:
        """Tests that the message list view correctly displays user messages."""
        response = self.client.get(reverse('message_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Message")
        self.assertIn('unread_messages_count', response.context)
        self.assertEqual(response.context['unread_messages_count'], 1)

    def test_message_read_view(self) -> None:
        """Tests that posting to the message_read view marks the message as read."""
        response = self.client.post(reverse('message_read', args=[self.msg.pk]))
        self.assertRedirects(response, reverse('message_list'))
        self.msg.refresh_from_db()
        self.assertTrue(self.msg.is_read)

    def test_unread_count_context_processor(self) -> None:
        """Tests that the context processor correctly calculates the unread count."""
        # Create another unread message
        UserMessage.objects.create(user=self.user, message_body="Another Message")
        response = self.client.get(reverse('order_list'))
        self.assertEqual(response.context['unread_messages_count'], 2)

    def test_message_delete_view(self) -> None:
        """Tests that the message delete view performs a soft delete."""
        response = self.client.post(reverse('message_delete', args=[self.msg.pk]))
        self.assertRedirects(response, reverse('message_list'))
        
        # Verify message still exists in DB but is marked as deleted
        self.msg.refresh_from_db()
        self.assertTrue(self.msg.is_deleted)
        
        # Verify it is no longer visible in the list
        response = self.client.get(reverse('message_list'))
        self.assertNotContains(response, "Test Message")

    def test_deleted_messages_do_not_affect_unread_count(self) -> None:
        """Tests that soft-deleted messages are ignored by the context processor."""
        # Current unread count is 1 (msg)
        self.msg.is_deleted = True
        self.msg.save()
        
        response = self.client.get(reverse('order_list'))
        # This will depend on the context processor implementation. 
        # If it doesn't filter is_deleted=False, this test will fail, indicating we need to fix it.
        self.assertEqual(response.context['unread_messages_count'], 0)

    def test_message_list_sorting(self) -> None:
        """Tests that unread messages appear at the top and read messages at the bottom."""
        # Setup: Mark the first one (msg) as read
        self.msg.is_read = True
        self.msg.save()
        
        # Create a newer, unread message
        new_unread_msg = UserMessage.objects.create(user=self.user, message_body="New Unread")
        
        # Login is already done in setUp of UserMessageViewTest
        response = self.client.get(reverse('message_list'))
        messages = list(response.context['user_messages'])
        
        # Unread message should be first, even if newer
        self.assertEqual(messages[0], new_unread_msg)
        self.assertEqual(messages[1], self.msg)
        self.assertFalse(messages[0].is_read)
        self.assertTrue(messages[1].is_read)

class MessageIsolationTest(TestCase):
    def setUp(self) -> None:
        self.user_a = User.objects.create_user(username='usera', password='password')
        self.user_b = User.objects.create_user(username='userb', password='password')
        self.msg_a = UserMessage.objects.create(user=self.user_a, message_body="Msg A")
        self.msg_b = UserMessage.objects.create(user=self.user_b, message_body="Msg B")

    def test_message_delete_isolation(self) -> None:
        """Verify User A cannot soft-delete User B's message."""
        self.client.login(username='usera', password='password')
        response = self.client.get(reverse('message_delete', args=[self.msg_b.pk]))
        self.assertEqual(response.status_code, 404)
        
        response = self.client.post(reverse('message_delete', args=[self.msg_b.pk]))
        self.assertEqual(response.status_code, 404)
        
        self.msg_b.refresh_from_db()
        self.assertFalse(self.msg_b.is_deleted)

class OrderIsolationTest(TestCase):
    def setUp(self) -> None:
        self.user_a = User.objects.create_user(username='usera', password='password')
        self.user_b = User.objects.create_user(username='userb', password='password')
        self.staff_user = User.objects.create_user(username='staff', password='password', is_staff=True)
        
        self.order_a = Order.objects.create(user=self.user_a, title='Order A')
        self.order_b = Order.objects.create(user=self.user_b, title='Order B')

    def test_user_sees_only_own_orders_in_list(self) -> None:
        """Verify User A cannot see User B's orders in the list view."""
        self.client.login(username='usera', password='password')
        response = self.client.get(reverse('order_list'))
        self.assertContains(response, 'Order A')
        self.assertNotContains(response, 'Order B')

    def test_user_cannot_access_other_order_detail(self) -> None:
        """Verify User A gets 404 when trying to access User B's order detail."""
        self.client.login(username='usera', password='password')
        response = self.client.get(reverse('order_detail', args=[self.order_b.pk]))
        self.assertEqual(response.status_code, 404)

    def test_staff_user_sees_all_orders(self) -> None:
        """Verify Staff user can see both User A and User B's orders."""
        self.client.login(username='staff', password='password')
        response = self.client.get(reverse('order_list'))
        self.assertContains(response, 'Order A')
        self.assertContains(response, 'Order B')

    def test_staff_user_can_access_any_order_detail(self) -> None:
        """Verify Staff user can access any user's order detail view."""
        self.client.login(username='staff', password='password')
        response = self.client.get(reverse('order_detail', args=[self.order_a.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Order A')
