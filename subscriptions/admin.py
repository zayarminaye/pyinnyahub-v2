from django.contrib import admin
from .models import Subscription


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Admin interface for subscriptions."""
    list_display = ('user', 'course', 'access_type', 'is_active', 'is_global', 'expires_at', 'created_at')
    list_filter = ('access_type', 'is_active', 'is_global', 'created_at', 'expires_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'course__title')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Subscription Details', {
            'fields': ('user', 'course', 'payment', 'access_type', 'is_global')
        }),
        ('Status', {
            'fields': ('is_active', 'expires_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

