
from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
	list_display = ("id", "email", "name", "username", "is_staff", "is_active", "date_joined")
	search_fields = ("email", "name", "username")