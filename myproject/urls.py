from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "orders/", include("orders.urls")
    ),  # SR[20260322]: added prefix for orders app as to keep it separate from other apps
]
