from django.contrib import admin
from .models import NotificationSettings


@admin.register(NotificationSettings)
class NotificationSettingsAdmin(admin.ModelAdmin):
    """Admin interface for notification settings."""
    list_display = ('event', 'is_enabled', 'send_email', 'send_in_app')
    list_filter = ('is_enabled', 'send_email', 'send_in_app')
    search_fields = ('event',)

    fieldsets = (
        ('Notification Event', {
            'fields': ('event',)
        }),
        ('Settings', {
            'fields': ('is_enabled', 'send_email', 'send_in_app')
        }),
    )

