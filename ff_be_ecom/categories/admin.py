from django.contrib import admin
from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ("id", "name", "slug", "parent", "created_at")
	search_fields = ("name", "slug")
	prepopulated_fields = {"slug": ("name",)}
