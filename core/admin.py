from django.contrib import admin
from .models import SystemSettings, SystemMessage


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


@admin.register(SystemMessage)
class SystemMessageAdmin(admin.ModelAdmin):
    """Admin interface for editable system messages."""

    list_display = ('key', 'category', 'message_type', 'preview_burmese', 'preview_english', 'is_active')
    list_filter = ('category', 'message_type', 'is_active')
    search_fields = ('key', 'message_burmese', 'message_english', 'description')
    ordering = ('category', 'key')

    fieldsets = (
        ('Message Identification', {
            'fields': ('key', 'category', 'message_type', 'is_active'),
            'description': 'Unique key is used in code to reference this message'
        }),
        ('Message Content', {
            'fields': ('message_burmese', 'message_english'),
            'description': 'Edit messages to match your audience tone (not too formal or informal, natural and smooth)'
        }),
        ('Variables & Documentation', {
            'fields': ('variables', 'description', 'admin_notes'),
            'description': 'Variables can be used in messages with {variable_name} syntax',
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')

    def preview_burmese(self, obj):
        """Show preview of Burmese message."""
        msg = obj.message_burmese[:50]
        return f"{msg}..." if len(obj.message_burmese) > 50 else msg
    preview_burmese.short_description = 'Burmese Preview'

    def preview_english(self, obj):
        """Show preview of English message."""
        msg = obj.message_english[:50]
        return f"{msg}..." if len(obj.message_english) > 50 else msg
    preview_english.short_description = 'English Preview'
