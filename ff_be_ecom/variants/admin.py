from django.contrib import admin
from .models import Variant


@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
	list_display = ("id", "sku", "product", "price", "sale_price", "stock")
	search_fields = ("sku", "product__name")
	list_filter = ("currency",)
