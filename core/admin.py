from django.contrib import admin
from .models import SystemSettings


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    """Admin interface for system-wide settings."""

    fieldsets = (
        ('Site Information', {
            'fields': ('site_name', 'site_name_burmese')
        }),
        ('Menu Labels', {
            'fields': ('menu_dashboard', 'menu_courses', 'menu_my_courses',
                      'menu_payments', 'menu_profile', 'menu_logout',
                      'menu_login', 'menu_register'),
            'description': 'Customize menu text labels'
        }),
        ('Notification Messages (Burmese)', {
            'fields': ('notif_payment_pending', 'notif_payment_approved',
                      'notif_payment_rejected', 'notif_course_enrolled',
                      'notif_course_approved', 'notif_course_rejected',
                      'notif_welcome', 'notif_already_enrolled', 'notif_access_denied'),
            'description': 'Customize system notification messages in Burmese'
        }),
        ('Theme Settings', {
            'fields': ('default_theme', 'allow_theme_toggle'),
            'description': 'Configure light/dark mode settings'
        }),
        ('Email Settings', {
            'fields': ('admin_email', 'support_email')
        }),
        ('Feature Flags', {
            'fields': ('enable_payment_upload', 'enable_course_reviews',
                      'enable_instructor_applications'),
            'description': 'Enable or disable features'
        }),
    )

    def has_add_permission(self, request):
        """Only allow one settings instance."""
        return not SystemSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of settings."""
        return False
