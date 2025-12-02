from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
	model = OrderItem
	extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = ("id", "order_number", "customer", "status", "grand_total", "created_at")
	search_fields = ("order_number", "customer__email", "customer__name")
	list_filter = ("status",)
	inlines = (OrderItemInline,)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
	list_display = ("id", "order", "variant", "qty", "unit_price", "line_total")
	search_fields = ("variant__sku",)
