from __future__ import annotations
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
)
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.urls import reverse_lazy
from django.db import transaction
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from .models import Order, Inventory, UserMessage
from .forms import OrderForm, OrderItemFormSet










class OrderPriceMixin:
    def _get_product_prices_data(self) -> dict:
        """Generates a dictionary of product IDs and their prices for client-side total calculation."""
        return {item.id: float(item.price) for item in Inventory.objects.all()}


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "orders/order_list.html"
    context_object_name = "orders"

    def get_queryset(self) -> QuerySet[Order]:
        queryset = Order.objects.select_related("user").all().order_by("-created_at")

        # Data Isolation: Non-staff users only see their own orders
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")

        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        return queryset


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "orders/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .select_related("user")
            .prefetch_related("items__inventory")
        )
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        return queryset


class OrderCreateView(LoginRequiredMixin, CreateView, OrderPriceMixin):
    model = Order
    form_class = OrderForm
    template_name = "orders/order_form.html"
    success_url = reverse_lazy("order_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        initial["user"] = self.request.user
        return initial

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if "items" not in data:
            if self.request.POST:
                data["items"] = OrderItemFormSet(self.request.POST)
            else:
                data["items"] = OrderItemFormSet()
        data["product_prices"] = self._get_product_prices_data()
        return data

    def form_valid(self, form):
        items = OrderItemFormSet(self.request.POST)

        if not items.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, items=items)
            )

        with transaction.atomic():
            if not self.request.user.is_staff:
                form.instance.user = self.request.user

            form.instance.created_by = self.request.user
            self.object = form.save()
            items.instance = self.object
            items.save()
            self.object.recalculate_total()

        from django.http import HttpResponseRedirect

        return HttpResponseRedirect(self.get_success_url())


class OrderUpdateView(LoginRequiredMixin, UpdateView, OrderPriceMixin):
    model = Order
    form_class = OrderForm
    template_name = "orders/order_form.html"
    success_url = reverse_lazy("order_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        return queryset

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if "items" not in data:
            if self.request.POST:
                data["items"] = OrderItemFormSet(
                    self.request.POST, instance=self.object
                )
            else:
                data["items"] = OrderItemFormSet(instance=self.object)
        data["product_prices"] = self._get_product_prices_data()
        return data

    def form_valid(self, form):
        items = OrderItemFormSet(self.request.POST, instance=self.object)

        if not items.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, items=items)
            )

        with transaction.atomic():
            self.object = form.save()
            items.save()
            self.object.recalculate_total()

        from django.http import HttpResponseRedirect

        return HttpResponseRedirect(self.get_success_url())



class OrderDeleteView(LoginRequiredMixin, DeleteView):

    model = Order
    template_name = "orders/order_confirm_delete.html"
    success_url = reverse_lazy("order_list")

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        return queryset


class SupportView(TemplateView):
    template_name = "orders/support.html"


class AboutUsView(TemplateView):
    template_name = "orders/about_us.html"


class MessageListView(LoginRequiredMixin, ListView):
    model = UserMessage
    template_name = "orders/message_list.html"
    context_object_name = "user_messages"

    def get_queryset(self) -> QuerySet[UserMessage]:
        return (
            UserMessage.objects.filter(user=self.request.user, is_deleted=False)
            .select_related("order")
            .order_by("is_read", "-created_at")
        )


class MessageReadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        message = get_object_or_404(UserMessage, pk=pk, user=request.user)
        message.is_read = True
        message.save()
        return redirect("message_list")


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = UserMessage
    template_name = "orders/message_confirm_delete.html"
    success_url = reverse_lazy("message_list")

    def get_queryset(self) -> QuerySet[UserMessage]:
        return UserMessage.objects.filter(user=self.request.user, is_deleted=False)

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.is_deleted = True
        self.object.save()
        return redirect(success_url)


from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

# ... (existing imports)

@login_required
def user_lookup(request):
    """
    Lookup users by their IDs, used for mobile order streaming integration.
    Internal API endpoint - restricted to staff.
    """
    if not request.user.is_staff:
        return JsonResponse({"error": "Forbidden"}, status=403)

    user_ids = request.GET.get("user_ids", "").split(",")
    try:
        user_ids = list(map(int, user_ids))
    except ValueError:
        return JsonResponse({"error": "Invalid user IDs"}, status=400)

    # Fetch usernames for given user IDs
    users = User.objects.filter(id__in=user_ids).values("id", "username")
    users_dict = {user["id"]: user["username"] for user in users}

    return JsonResponse(users_dict)
