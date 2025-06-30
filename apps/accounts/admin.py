from django.contrib import admin
from apps.accounts.models import User

# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = ['first_name', 'last_name', 'email','account_type']
    fields = ['first_name', 'last_name', 'email','avatar','is_staff','is_active','account_type']
