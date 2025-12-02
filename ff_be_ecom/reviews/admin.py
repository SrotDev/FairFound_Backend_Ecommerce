from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
	list_display = ("id", "product", "customer", "rating", "created_at")
	search_fields = ("product__name", "customer__email", "customer__name")
	list_filter = ("rating",)
