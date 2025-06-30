from django.contrib import admin
from apps.shop.models import Product

# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name','slug', 'price_current','in_stock']
    fields = ['name', 'price_old','price_current','category','in_stock']
    readonly_fields = ['slug']