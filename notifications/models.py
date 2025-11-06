"""
Notification models for Pyinnya Hub LMS.
Handles both email and in-app notifications.
"""
from django.db import models
from django.conf import settings
from core.models import TimeStampedModel


class NotificationManager(models.Manager):
    """Custom manager for Notification model."""

    def unread(self):
        """Return unread notifications."""
        return self.filter(is_read=False)

    def read(self):
        """Return read notifications."""
        return self.filter(is_read=True)

    def for_user(self, user):
        """Return notifications for specific user."""
        return self.filter(user=user)

    def mark_all_read(self, user):
        """Mark all notifications as read for a user."""
        return self.filter(user=user, is_read=False).update(is_read=True)


class Notification(TimeStampedModel):
    """
    In-app notification model.
    Stores notifications that appear in user's notification panel.
    """
    NOTIFICATION_TYPES = (
        ('registration', 'Registration'),
        ('instructor_application', 'Instructor Application'),
        ('payment', 'Payment'),
        ('course', 'Course'),
        ('subscription', 'Subscription'),
        ('payout', 'Payout'),
        ('system', 'System'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, db_index=True)
    title = models.CharField(max_length=255)
    message = models.TextField()

    # Optional fields for linking to related objects
    related_object_type = models.CharField(max_length=50, blank=True, null=True)
    related_object_id = models.PositiveIntegerField(blank=True, null=True)

    # Metadata
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    is_sent_via_email = models.BooleanField(default=False)

    objects = NotificationManager()

    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['notification_type', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.title}"

    def mark_as_read(self):
        """Mark notification as read."""
        from django.utils import timezone

        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])

    def mark_as_unread(self):
        """Mark notification as unread."""
        if self.is_read:
            self.is_read = False
            self.read_at = None
            self.save(update_fields=['is_read', 'read_at'])


class EmailLog(TimeStampedModel):
    """
    Log of all emails sent by the system.
    Useful for debugging and tracking email delivery.
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    )

    recipient = models.EmailField()
    subject = models.CharField(max_length=255)
    body = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    error_message = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    # Optional: link to user
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='email_logs'
    )

    # Email type for categorization
    email_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text='Type of email (registration, payment_approved, etc.)'
    )

    class Meta:
        db_table = 'email_logs'
        verbose_name = 'Email Log'
        verbose_name_plural = 'Email Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['email_type', 'created_at']),
        ]

    def __str__(self):
        return f"{self.recipient} - {self.subject} ({self.status})"

    def mark_as_sent(self):
        """Mark email as successfully sent."""
        from django.utils import timezone

        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save(update_fields=['status', 'sent_at'])

    def mark_as_failed(self, error_message):
        """Mark email as failed with error message."""
        self.status = 'failed'
        self.error_message = error_message
        self.save(update_fields=['status', 'error_message'])


class NotificationSettings(TimeStampedModel):
    """
    Admin-configurable notification settings.
    Controls which notifications are sent and through which channels.
    """
    NOTIFICATION_EVENTS = (
        ('registration', 'User Registration'),
        ('instructor_approved', 'Instructor Application Approved'),
        ('instructor_rejected', 'Instructor Application Rejected'),
        ('payment_approved', 'Payment Approved'),
        ('payment_rejected', 'Payment Rejected'),
        ('course_approved', 'Course Approved'),
        ('course_rejected', 'Course Rejected'),
        ('subscription_expiry_reminder', 'Subscription Expiry Reminder'),
        ('subscription_expired', 'Subscription Expired'),
        ('payout_completed', 'Payout Completed'),
        ('payout_cancelled', 'Payout Cancelled'),
        ('password_reset', 'Password Reset'),
    )

    event = models.CharField(
        max_length=50,
        choices=NOTIFICATION_EVENTS,
        unique=True,
        help_text='Notification event type'
    )
    is_enabled = models.BooleanField(
        default=True,
        help_text='Enable/disable this notification'
    )
    send_email = models.BooleanField(
        default=True,
        help_text='Send notification via email'
    )
    send_in_app = models.BooleanField(
        default=True,
        help_text='Send notification as in-app notification'
    )

    class Meta:
        db_table = 'notification_settings'
        verbose_name = 'Notification Setting'
        verbose_name_plural = 'Notification Settings'

    def __str__(self):
        return f"{self.get_event_display()} - {'Enabled' if self.is_enabled else 'Disabled'}"

    @classmethod
    def should_send_email(cls, event):
        """Check if email should be sent for this event."""
        try:
            setting = cls.objects.get(event=event)
            return setting.is_enabled and setting.send_email
        except cls.DoesNotExist:
            # Default to True if no setting exists
            return True

    @classmethod
    def should_send_in_app(cls, event):
        """Check if in-app notification should be sent for this event."""
        try:
            setting = cls.objects.get(event=event)
            return setting.is_enabled and setting.send_in_app
        except cls.DoesNotExist:
            # Default to True if no setting exists
            return True

    @classmethod
    def initialize_defaults(cls):
        """Create default notification settings for all events."""
        for event, label in cls.NOTIFICATION_EVENTS:
            cls.objects.get_or_create(
                event=event,
                defaults={
                    'is_enabled': True,
                    'send_email': True,
                    'send_in_app': True,
                }
            )
