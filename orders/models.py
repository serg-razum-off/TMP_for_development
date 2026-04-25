from django.contrib.auth.models import User
from django.db import models


class Inventory(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    commentary = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.name} (${self.price})"

    class Meta:
        verbose_name_plural = "Inventory"


class OrderStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PENDING = "pending", "Pending"
    ASSEMBLING = "assembling", "Assembling"
    SHIPPING = "shipping", "Shipping"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"


class Order(models.Model):
    user = models.ForeignKey(User, related_name="orders", on_delete=models.CASCADE)
    created_by = models.ForeignKey(
        User,
        related_name="created_orders",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20, choices=OrderStatus.choices, default=OrderStatus.DRAFT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    comment = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_status = self.status

    def __str__(self) -> str:
        return f"{self.title} ({self.user.username})"

    def recalculate_total(self) -> None:
        """
        Calculates the total amount based on associated items and saves the order.
        Uses select_related to minimize database hits.
        """
        total = sum(
            item.line_total for item in self.items.select_related("inventory").all()
        )
        self.amount = total
        self.save(update_fields=["amount"])

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if not is_new and getattr(self, "_original_status", None) != self.status:
            UserMessage.objects.create(
                user=self.user,
                order=self,
                message_body=f"Order '{self.title}' status changed to {self.get_status_display()}.",
            )

        if is_new and self.created_by and self.user != self.created_by:
            UserMessage.objects.create(
                user=self.user,
                order=self,
                message_body=f"A new order '{self.title}' has been created for you by {self.created_by.username}.",
            )

        self._original_status = self.status


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    inventory = models.ForeignKey(
        Inventory, related_name="order_usages", on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self) -> str:
        return f"{self.inventory.name} x {self.quantity} (Order: {self.order.id})"

    @property
    def line_total(self):
        """Calculates the line total for this item (price * quantity)."""
        return self.inventory.price * self.quantity


class UserMessage(models.Model):
    user = models.ForeignKey(User, related_name="messages", on_delete=models.CASCADE)
    order = models.ForeignKey(
        Order, related_name="messages", on_delete=models.CASCADE, null=True, blank=True
    )
    message_body = models.TextField()
    is_error = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Message for {self.user.username} - Read: {self.is_read}"

    class Meta:
        ordering = ["-created_at"]
