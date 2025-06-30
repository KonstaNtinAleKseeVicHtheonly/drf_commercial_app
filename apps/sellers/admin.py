from django.contrib import admin

# Register your models here.
from apps.sellers.models import Seller

# Register your models here.

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):

    list_display = ['user', 'business_name', 'city','is_approved']
    fields = ('user', 'business_name', 'inn_identification_number','business_description','city','is_approved')
