from django.contrib import admin
from .models import PricingRule


@admin.register(PricingRule)
class PricingRuleAdmin(admin.ModelAdmin):
	list_display = ("id", "name", "type", "value", "active", "starts_at", "ends_at")
	search_fields = ("name",)
	list_filter = ("type", "active")
