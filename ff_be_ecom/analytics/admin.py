from django.contrib import admin
from .models import AnalyticsSnapshot


@admin.register(AnalyticsSnapshot)
class AnalyticsSnapshotAdmin(admin.ModelAdmin):
	list_display = ("id", "metric", "value", "period", "created_at")
	search_fields = ("metric", "period")
	list_filter = ("period",)
