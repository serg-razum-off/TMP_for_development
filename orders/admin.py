
from django.contrib import admin
from .models import Order, Inventory, OrderItem, UserMessage

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'user__username')
    inlines = [OrderItemInline]

@admin.register(UserMessage)
class UserMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'order', 'message_body', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'message_body')
