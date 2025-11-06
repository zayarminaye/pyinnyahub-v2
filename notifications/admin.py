from django.contrib import admin
from .models import NotificationSettings


@admin.register(NotificationSettings)
class NotificationSettingsAdmin(admin.ModelAdmin):
    """Admin interface for notification settings."""
    list_display = ('email_enabled', 'payment_approved', 'payment_rejected', 'course_approved')

    fieldsets = (
        ('Email Settings', {
            'fields': ('email_enabled', 'email_host', 'email_port', 'email_host_user',
                      'email_host_password', 'email_use_tls', 'default_from_email')
        }),
        ('Payment Notifications', {
            'fields': ('payment_approved', 'payment_rejected')
        }),
        ('Course Notifications', {
            'fields': ('course_approved', 'course_rejected')
        }),
        ('User Notifications', {
            'fields': ('registration_confirmation', 'instructor_application_approved', 'instructor_application_rejected')
        }),
        ('Subscription Notifications', {
            'fields': ('subscription_expiring', 'subscription_expired')
        }),
    )

    def has_add_permission(self, request):
        """Only allow one settings instance."""
        return not NotificationSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of settings."""
        return False

