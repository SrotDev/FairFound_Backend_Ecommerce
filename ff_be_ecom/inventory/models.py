from django.db import models
from uuid import uuid4
from variants.models import Variant
# Create your models here.
class InventoryMovement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name='movements')
    change = models.IntegerField()
    reason = models.CharField(max_length=80)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.variant.sku} {self.change}"