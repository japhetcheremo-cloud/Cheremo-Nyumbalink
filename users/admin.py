from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_verified', 'is_staff')
    list_filter = ('role', 'is_verified', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    ordering = ('-date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        ('NyumbaLink Profile', {
            'fields': ('role', 'phone', 'profile_picture', 'bio', 'is_verified', 'verification_document'),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('NyumbaLink Profile', {
            'fields': ('role', 'phone'),
        }),
    )
