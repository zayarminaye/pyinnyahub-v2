from django.contrib import admin
from django.utils.html import format_html
from .models import Notification, EmailLog, NotificationSettings


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for in-app notifications."""
    list_display = ('user', 'title', 'notification_type', 'is_read', 'is_sent_via_email', 'created_at')
    list_filter = ('notification_type', 'is_read', 'is_sent_via_email', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'title', 'message')
    readonly_fields = ('created_at', 'updated_at', 'read_at')
    date_hierarchy = 'created_at'
    actions = ['mark_as_read', 'mark_as_unread']

    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Notification Details', {
            'fields': ('notification_type', 'title', 'message')
        }),
        ('Related Object', {
            'fields': ('related_object_type', 'related_object_id'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_read', 'read_at', 'is_sent_via_email')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def mark_as_read(self, request, queryset):
        """Mark selected notifications as read."""
        count = 0
        for notification in queryset.filter(is_read=False):
            notification.mark_as_read()
            count += 1
        self.message_user(request, f'{count} notification(s) marked as read.')
    mark_as_read.short_description = '✓ Mark selected as read'

    def mark_as_unread(self, request, queryset):
        """Mark selected notifications as unread."""
        count = 0
        for notification in queryset.filter(is_read=True):
            notification.mark_as_unread()
            count += 1
        self.message_user(request, f'{count} notification(s) marked as unread.')
    mark_as_unread.short_description = '✗ Mark selected as unread'


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    """Admin interface for email logs."""
    list_display = ('recipient', 'subject', 'email_type', 'status_badge', 'created_at', 'sent_at')
    list_filter = ('status', 'email_type', 'created_at')
    search_fields = ('recipient', 'subject', 'body', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at', 'sent_at')
    date_hierarchy = 'created_at'
    actions = ['resend_failed_emails']

    fieldsets = (
        ('Recipient', {
            'fields': ('recipient', 'user')
        }),
        ('Email Content', {
            'fields': ('email_type', 'subject', 'body')
        }),
        ('Status', {
            'fields': ('status', 'sent_at', 'error_message')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'pending': '#ffc107',  # yellow
            'sent': '#28a745',     # green
            'failed': '#dc3545',   # red
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def resend_failed_emails(self, request, queryset):
        """Attempt to resend failed emails."""
        from .services import NotificationService
        import logging

        logger = logging.getLogger('pyinnyahub')
        resent_count = 0

        for email_log in queryset.filter(status='failed'):
            try:
                NotificationService._send_email(
                    recipient=email_log.recipient,
                    subject=email_log.subject,
                    message=email_log.body,
                    email_type=email_log.email_type,
                    user=email_log.user
                )
                resent_count += 1
            except Exception as e:
                logger.error(f"Failed to resend email to {email_log.recipient}: {e}")

        self.message_user(request, f'Attempted to resend {resent_count} email(s).')
    resend_failed_emails.short_description = '📧 Resend failed emails'


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

