from django.contrib import admin
from .models import Promotion


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
	list_display = ("id", "code", "name", "active", "usage_limit", "used_count")
	search_fields = ("code", "name")
	list_filter = ("active",)
