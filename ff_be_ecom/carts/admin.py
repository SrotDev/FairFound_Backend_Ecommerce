from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
	model = CartItem
	extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
	list_display = ("id", "customer", "status", "created_at", "updated_at")
	search_fields = ("id", "customer__email", "customer__name")
	list_filter = ("status",)
	inlines = (CartItemInline,)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
	list_display = ("id", "cart", "variant", "qty", "price_at_add")
	search_fields = ("variant__sku",)
