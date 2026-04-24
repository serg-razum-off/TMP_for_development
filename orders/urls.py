from django.urls import path
from .views import (
    OrderListView,
    OrderDetailView,
    OrderCreateView,
    OrderUpdateView,
    OrderDeleteView,
    SupportView,
    AboutUsView,
    MessageListView,
    MessageReadView,
    MessageDeleteView,
    user_lookup,
)

urlpatterns = [
    path("", OrderListView.as_view(), name="order_list"),
    path("<int:pk>/", OrderDetailView.as_view(), name="order_detail"),
    path("create/", OrderCreateView.as_view(), name="order_create"),
    path("<int:pk>/update/", OrderUpdateView.as_view(), name="order_update"),
    path("<int:pk>/delete/", OrderDeleteView.as_view(), name="order_delete"),
    path("support/", SupportView.as_view(), name="support"),
    path("about-us/", AboutUsView.as_view(), name="about_us"),
    path("messages/", MessageListView.as_view(), name="message_list"),
    path("messages/<int:pk>/read/", MessageReadView.as_view(), name="message_read"),
    path(
        "messages/<int:pk>/delete/", MessageDeleteView.as_view(), name="message_delete"
    ),
    path("users/lookup/", user_lookup, name="user_lookup"),
]
