from django.contrib import admin
from .models import InventoryMovement


@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
	list_display = ("id", "variant", "change", "reason", "created_at")
	search_fields = ("variant__sku", "reason")
	list_filter = ("reason",)
