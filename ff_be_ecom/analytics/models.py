from django.db import models
from uuid import uuid4

# Create your models here.
class AnalyticsSnapshot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    metric = models.CharField(max_length=40)
    value = models.DecimalField(max_digits=12, decimal_places=2)
    breakdown = models.JSONField(default=dict, blank=True)
    period = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.metric} - {self.period}"