from django.db import models
from uuid import uuid4
from customers.models import Customer
from variants.models import Variant


# Create your models here.
class CartStatus(models.TextChoices):
    OPEN = "open", "Open"
    CONVERTED = "converted", "Converted"
    ABANDONED = "abandoned", "Abandoned"

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.SET_NULL, related_name='carts')
    status = models.CharField(max_length=16, choices=CartStatus.choices, default=CartStatus.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Cart {self.id} ({self.status})"

class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    qty = models.IntegerField(default=1)
    price_at_add = models.DecimalField(max_digits=10, decimal_places=2)
    def line_total(self):
        return self.qty * self.price_at_add
    def __str__(self):
        return f"{self.variant.sku} x {self.qty}"