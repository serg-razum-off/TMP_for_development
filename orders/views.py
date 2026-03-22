from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.urls import reverse_lazy
from .models import Order


class OrderListView(ListView):
    model = Order
    template_name = "orders/order_list.html"
    context_object_name = "orders"

    def get_queryset(self) -> QuerySet[Order]:
        queryset = Order.objects.select_related("user").all().order_by("-created_at")

        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")

        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        return queryset


class OrderDetailView(DetailView):
    model = Order
    template_name = "orders/order_detail.html"
    context_object_name = "order"


class OrderCreateView(CreateView):
    model = Order
    fields = ["user", "title", "amount", "status", "is_active"]
    template_name = "orders/order_form.html"
    success_url = reverse_lazy("order_list")


class OrderUpdateView(UpdateView):
    model = Order
    fields = ["user", "title", "amount", "status", "is_active"]
    template_name = "orders/order_form.html"
    success_url = reverse_lazy("order_list")


class OrderDeleteView(DeleteView):
    model = Order
    template_name = "orders/order_confirm_delete.html"
    success_url = reverse_lazy("order_list")
