"""
Core abstract base models for reusability across the application.
These models provide common functionality and promote DRY principles.
"""
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Abstract base class that provides self-updating 'created_at' and 'updated_at' fields.
    All models should inherit from this for audit trail.
    """
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class SoftDeleteManager(models.Manager):
    """
    Manager that filters out soft-deleted objects by default.
    Use Model.all_objects to include deleted objects.
    """
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class SoftDeleteModel(TimeStampedModel):
    """
    Abstract base class that provides soft delete functionality.
    Objects are marked as deleted instead of being removed from the database.
    """
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()  # Includes deleted objects

    class Meta:
        abstract = True

    def soft_delete(self):
        """Mark object as deleted without removing from database."""
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    def restore(self):
        """Restore a soft-deleted object."""
        self.deleted_at = None
        self.save(update_fields=['deleted_at'])

    @property
    def is_deleted(self):
        """Check if object is soft-deleted."""
        return self.deleted_at is not None


class PublishableModel(TimeStampedModel):
    """
    Abstract base class for models that can be published/unpublished.
    Useful for courses, announcements, etc.
    """
    is_published = models.BooleanField(default=False, db_index=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def publish(self):
        """Publish the object."""
        if not self.is_published:
            self.is_published = True
            self.published_at = timezone.now()
            self.save(update_fields=['is_published', 'published_at'])

    def unpublish(self):
        """Unpublish the object."""
        if self.is_published:
            self.is_published = False
            self.save(update_fields=['is_published'])


class SystemSettings(models.Model):
    """
    System-wide settings that can be configured from admin panel.
    Singleton model - only one instance should exist.
    """

    # Site Information
    site_name = models.CharField(max_length=100, default="Pyinnya Hub")
    site_name_burmese = models.CharField(max_length=100, default="ပညာဟပ်", verbose_name="Site Name (Burmese)")

    # Menu Labels
    menu_dashboard = models.CharField(max_length=50, default="Dashboard")
    menu_courses = models.CharField(max_length=50, default="Courses")
    menu_my_courses = models.CharField(max_length=50, default="My Courses")
    menu_payments = models.CharField(max_length=50, default="Payments")
    menu_profile = models.CharField(max_length=50, default="Profile")
    menu_logout = models.CharField(max_length=50, default="Log out")
    menu_login = models.CharField(max_length=50, default="Login")
    menu_register = models.CharField(max_length=50, default="Register")

    # Notification Message Templates (Burmese)
    notif_payment_pending = models.TextField(
        default="ငွေပေးချေမှု အောင်မြင်စွာ တင်သွင်းပြီးပါပြီ။ Admin မှ အတည်ပြုပေးမည်ဖြစ်ပါသည်။",
        verbose_name="Payment Pending Message",
        help_text="Message shown when payment is submitted"
    )
    notif_payment_approved = models.TextField(
        default="ငွေပေးချေမှု အတည်ပြုပြီးပါပြီ။ သင်ခန်းစာကို စတင်နိုင်ပါပြီ။",
        verbose_name="Payment Approved Message",
        help_text="Message shown when payment is approved"
    )
    notif_payment_rejected = models.TextField(
        default="ငွေပေးချေမှု ငြင်းပယ်ခံရပါသည်။ ကျေးဇူးပြု၍ ပြန်လည်စစ်ဆေးပြီး ထပ်မံတင်သွင်းပေးပါ။",
        verbose_name="Payment Rejected Message",
        help_text="Message shown when payment is rejected"
    )
    notif_course_enrolled = models.TextField(
        default="သင်ခန်းစာတွင် အောင်မြင်စွာ စာရင်းသွင်းပြီးပါပြီ။",
        verbose_name="Course Enrolled Message",
        help_text="Message shown when successfully enrolled in course"
    )
    notif_course_approved = models.TextField(
        default="သင်ခန်းစာကို အတည်ပြုပြီးပါပြီ။ ယခု ထုတ်ဝေနိုင်ပါပြီ။",
        verbose_name="Course Approved Message",
        help_text="Message shown when course is approved by admin"
    )
    notif_course_rejected = models.TextField(
        default="သင်ခန်းစာ ငြင်းပယ်ခံရပါသည်။ ကျေးဇူးပြု၍ ပြင်ဆင်ပြီး ထပ်မံတင်သွင်းပေးပါ။",
        verbose_name="Course Rejected Message",
        help_text="Message shown when course is rejected"
    )
    notif_welcome = models.TextField(
        default="Pyinnya Hub မှ ကြိုဆိုပါသည်။ စာရင်းသွင်းမှု အောင်မြင်ပါသည်။",
        verbose_name="Welcome Message",
        help_text="Message shown after successful registration"
    )
    notif_already_enrolled = models.TextField(
        default="သင့်တွင် ဤသင်ခန်းစာ ရှိပြီးဖြစ်ပါသည်။",
        verbose_name="Already Enrolled Message",
        help_text="Message shown when user already enrolled"
    )
    notif_access_denied = models.TextField(
        default="ဝင်ခွင့်မရှိပါ။",
        verbose_name="Access Denied Message",
        help_text="Message shown when access is denied"
    )

    # Theme Settings
    default_theme = models.CharField(
        max_length=10,
        choices=[
            ('light', 'Light Mode'),
            ('dark', 'Dark Mode'),
        ],
        default='light',
        help_text="Default theme for new users"
    )
    allow_theme_toggle = models.BooleanField(
        default=True,
        help_text="Allow users to toggle between light and dark mode"
    )

    # Email Settings
    admin_email = models.EmailField(
        default="admin@pyinnyahub.com",
        help_text="Email address for admin notifications"
    )
    support_email = models.EmailField(
        default="support@pyinnyahub.com",
        help_text="Email address for user support"
    )

    # Feature Flags
    enable_payment_upload = models.BooleanField(default=True, help_text="Enable manual payment upload")
    enable_course_reviews = models.BooleanField(default=True, help_text="Enable course reviews and ratings")
    enable_instructor_applications = models.BooleanField(default=True, help_text="Enable instructor applications")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "System Settings"
        verbose_name_plural = "System Settings"

    def __str__(self):
        return f"System Settings (Updated: {self.updated_at.strftime('%Y-%m-%d %H:%M')})"

    def save(self, *args, **kwargs):
        """Ensure only one instance exists (singleton pattern)."""
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        """Get the singleton settings instance."""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
