from django.db import models
from uuid import uuid4
from pricing_rules.models import PricingRule
# Create your models here.
class Promotion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    code = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=160)
    description = models.TextField(null=True, blank=True)
    rule = models.ForeignKey(PricingRule, on_delete=models.CASCADE, related_name='promotions')
    active = models.BooleanField(default=True)
    usage_limit = models.IntegerField(null=True, blank=True)
    used_count = models.IntegerField(default=0)
    def __str__(self):
        return f"{self.code} - {self.name}"