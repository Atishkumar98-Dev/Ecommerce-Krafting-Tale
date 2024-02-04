from django.contrib import admin
from .models import Category, Product, Customer, Order, OrderItem,Brand
from .models import Delivery, Refund

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['order', 'user', 'status', 'delivery_date', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at', 'updated_at']
    search_fields = ['order__id', 'user__username', 'address']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ['order', 'reason', 'accepted', 'email']
    list_filter = ['accepted']
    search_fields = ['order__id', 'email']
    readonly_fields = ['pk']

    
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price']
    list_filter = ['category']
    search_fields = ['name']

class OrderAdmin(admin.ModelAdmin):
    list_display = ['customer', 'order_date', 'total_price','status','delivery_status']
    inlines = [OrderItemInline]

class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'shipping_address']

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']


class BrandAdmin(admin.ModelAdmin):
    list_display = ['name']


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Brand, BrandAdmin)
