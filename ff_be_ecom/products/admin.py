from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ("id", "name", "slug", "category", "status", "created_at")
	search_fields = ("name", "slug")
	list_filter = ("status", "category")
	prepopulated_fields = {"slug": ("name",)}
