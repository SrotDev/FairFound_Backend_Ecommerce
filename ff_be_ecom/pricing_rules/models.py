from django.db import models
from django.utils import timezone
from uuid import uuid4
# Create your models here.
class PricingRuleType(models.TextChoices):
    PERCENTAGE = "percentage", "Percentage"
    FIXED = "fixed", "Fixed"

class PricingRule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=160)
    type = models.CharField(max_length=16, choices=PricingRuleType.choices)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    applies_to = models.JSONField(default=dict, blank=True)  
    active = models.BooleanField(default=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    def is_active(self):
        now = timezone.now()
        if not self.active:
            return False
        if self.starts_at and now < self.starts_at:
            return False
        if self.ends_at and now > self.ends_at:
            return False
        return True
    def __str__(self):
        return self.name