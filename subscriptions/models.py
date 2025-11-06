"""
Subscription models for Pyinnya Hub LMS.
Manages course access with expiry dates and automatic renewal checks.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from core.models import TimeStampedModel
from core.utils import get_subscription_expiry_date, is_subscription_expired


class SubscriptionManager(models.Manager):
    """Custom manager for Subscription model."""

    def active(self):
        """Return only active subscriptions."""
        return self.filter(is_active=True)

    def expired(self):
        """Return expired subscriptions."""
        return self.filter(
            is_active=True,
            expires_at__isnull=False,
            expires_at__lt=timezone.now()
        )

    def expiring_soon(self, days=3):
        """Return subscriptions expiring within specified days."""
        from datetime import timedelta
        threshold = timezone.now() + timedelta(days=days)
        return self.filter(
            is_active=True,
            expires_at__isnull=False,
            expires_at__lte=threshold,
            expires_at__gt=timezone.now()
        )

    def by_user(self, user):
        """Return subscriptions for specific user."""
        return self.filter(user=user)

    def by_course(self, course):
        """Return subscriptions for specific course."""
        return self.filter(course=course)

    def global_subscriptions(self):
        """Return global subscriptions (access all courses)."""
        return self.filter(is_global=True, is_active=True)


class Subscription(TimeStampedModel):
    """
    Subscription model for managing course access.
    Supports course-specific and global subscriptions.
    """
    ACCESS_TYPE_CHOICES = (
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('lifetime', 'Lifetime'),
    )

    # Subscription details
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='subscriptions',
        null=True,
        blank=True,
        help_text='Specific course or null for global subscription'
    )
    payment = models.ForeignKey(
        'payments.Payment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subscriptions'
    )

    # Access control
    access_type = models.CharField(
        max_length=20,
        choices=ACCESS_TYPE_CHOICES,
        default='monthly'
    )
    is_active = models.BooleanField(default=True, db_index=True)
    is_global = models.BooleanField(
        default=False,
        db_index=True,
        help_text='True if subscription grants access to all courses'
    )

    # Dates
    starts_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text='Null for lifetime access'
    )
    cancelled_at = models.DateTimeField(null=True, blank=True)

    objects = SubscriptionManager()

    class Meta:
        db_table = 'subscriptions'
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['course', 'is_active']),
            models.Index(fields=['is_active', 'expires_at']),
            models.Index(fields=['is_global', 'is_active']),
        ]

    def __str__(self):
        course_name = self.course.title if self.course else 'Global Subscription'
        status = 'Active' if self.is_active else 'Inactive'
        return f"{self.user.get_full_name()} - {course_name} ({status})"

    def save(self, *args, **kwargs):
        """Set expiry date on creation if not set."""
        if not self.pk and not self.expires_at:
            self.expires_at = get_subscription_expiry_date(self.access_type)
        super().save(*args, **kwargs)

    def is_expired(self):
        """Check if subscription has expired."""
        if not self.is_active:
            return True
        return is_subscription_expired(self.expires_at)

    def deactivate(self):
        """Deactivate the subscription."""
        self.is_active = False
        self.save(update_fields=['is_active'])

    def reactivate(self):
        """Reactivate the subscription."""
        self.is_active = True
        self.save(update_fields=['is_active'])

    def extend(self, days):
        """Extend subscription by specified number of days."""
        from datetime import timedelta

        if self.expires_at:
            # If expired, extend from now, otherwise from current expiry
            base_date = max(self.expires_at, timezone.now())
            self.expires_at = base_date + timedelta(days=days)
        else:
            # Lifetime subscription, set expiry
            self.expires_at = timezone.now() + timedelta(days=days)

        self.is_active = True
        self.save(update_fields=['expires_at', 'is_active'])

    def cancel(self):
        """Cancel the subscription."""
        self.cancelled_at = timezone.now()
        self.is_active = False
        self.save(update_fields=['cancelled_at', 'is_active'])

    def has_access_to_course(self, course):
        """Check if subscription grants access to specific course."""
        if not self.is_active or self.is_expired():
            return False

        # Global subscription grants access to all courses
        if self.is_global:
            return True

        # Course-specific subscription
        return self.course == course

    @property
    def days_remaining(self):
        """Get number of days remaining before expiry."""
        if not self.expires_at:
            return None  # Lifetime access

        if self.is_expired():
            return 0

        delta = self.expires_at - timezone.now()
        return delta.days

    @property
    def is_lifetime(self):
        """Check if subscription is lifetime."""
        return self.expires_at is None


class SubscriptionHistory(TimeStampedModel):
    """
    Audit trail for subscription changes.
    """
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='history'
    )
    action = models.CharField(
        max_length=50,
        choices=(
            ('created', 'Created'),
            ('extended', 'Extended'),
            ('cancelled', 'Cancelled'),
            ('expired', 'Expired'),
            ('reactivated', 'Reactivated'),
        )
    )
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    notes = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'subscription_history'
        verbose_name = 'Subscription History'
        verbose_name_plural = 'Subscription Histories'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subscription} - {self.action}"
