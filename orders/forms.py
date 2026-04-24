from django import forms
from django.forms import inlineformset_factory
from .models import Order, OrderItem

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['user', 'title', 'status', 'comment']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Optional notes about this order...'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        if self.request and not self.request.user.is_staff:
            # If not staff, they can only create for themselves. 
            # We can either hide the field or restrict the queryset.
            self.fields['user'].queryset = Order.objects.none() # This is a bit harsh, let's just make it read-only or hidden
            # Actually, the requirement is "should see his own orders only". 
            # In creation, they should only be able to create for themselves.
            del self.fields['user']

OrderItemFormSet = inlineformset_factory(
    Order, OrderItem,
    fields=['inventory', 'quantity'],
    extra=1,
    can_delete=True,
    widgets={
        'inventory': forms.Select(attrs={'class': 'form-select'}),
        'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
    }
)
