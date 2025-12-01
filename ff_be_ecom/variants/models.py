from django.db import models
from uuid import uuid4
from products.models import Product

# Create your models here.
class Variant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    sku = models.CharField(max_length=80, unique=True)
    name = models.CharField(max_length=160, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    stock = models.IntegerField(default=0)
    attributes = models.JSONField(default=dict, blank=True)
    def __str__(self):
        return f"{self.sku} - {self.name or self.product.name}"