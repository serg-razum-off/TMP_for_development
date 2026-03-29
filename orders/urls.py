from django.urls import path
from .views import (
    OrderListView, 
    OrderDetailView, 
    OrderCreateView, 
    OrderUpdateView, 
    OrderDeleteView,
    SupportView,
    AboutUsView
)

urlpatterns = [
    path("", OrderListView.as_view(), name="order_list"),
    path("<int:pk>/", OrderDetailView.as_view(), name="order_detail"),
    path("create/", OrderCreateView.as_view(), name="order_create"),
    path("<int:pk>/update/", OrderUpdateView.as_view(), name="order_update"),
    path("<int:pk>/delete/", OrderDeleteView.as_view(), name="order_delete"),
    path("support/", SupportView.as_view(), name="support"),
    path("about-us/", AboutUsView.as_view(), name="about_us"),
]
