from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'phone', 'is_verified', 'is_staff', 'date_joined')
    list_filter = ('is_verified', 'is_staff')
    search_fields = ('email', 'phone')
    ordering = ('-date_joined',)