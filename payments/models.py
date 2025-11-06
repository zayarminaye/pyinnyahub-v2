"""
Payment models for Pyinnya Hub LMS.
Handles manual payment submissions with receipt uploads and admin approval.
"""
from django.db import models
from django.core.validators import FileExtensionValidator
from django.conf import settings
from core.models import TimeStampedModel
from core.utils import generate_unique_filename, validate_payment_receipt


class PaymentManager(models.Manager):
    """Custom manager for Payment model."""

    def pending(self):
        """Return pending payments."""
        return self.filter(status='pending')

    def approved(self):
        """Return approved payments."""
        return self.filter(status='approved')

    def rejected(self):
        """Return rejected payments."""
        return self.filter(status='rejected')

    def by_user(self, user):
        """Return payments by specific user."""
        return self.filter(user=user)

    def by_course(self, course):
        """Return payments for specific course."""
        return self.filter(course=course)


class Payment(TimeStampedModel):
    """
    Manual payment model with receipt upload and admin approval workflow.
    """
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    # Payment information
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='payments',
        null=True,
        blank=True,
        help_text='Specific course or null for global subscription'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    access_type = models.CharField(
        max_length=20,
        choices=(
            ('monthly', 'Monthly'),
            ('yearly', 'Yearly'),
            ('lifetime', 'Lifetime'),
        ),
        default='monthly'
    )

    # Receipt upload
    receipt = models.FileField(
        upload_to=generate_unique_filename,
        validators=[validate_payment_receipt],
        help_text='Payment receipt (max 10MB, JPG/PNG/PDF)'
    )

    # Transaction details (optional)
    transaction_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Bank transaction ID or reference'
    )
    payment_method = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Payment method (e.g., KBZPay, Wave Money, Bank Transfer)'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text='Additional notes from student'
    )

    # Review and approval
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_payments'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(
        blank=True,
        null=True,
        help_text='Internal admin notes'
    )
    rejection_reason = models.TextField(blank=True, null=True)

    # Is this for global subscription?
    is_global = models.BooleanField(
        default=False,
        help_text='True if payment is for global subscription (access all courses)'
    )

    objects = PaymentManager()

    class Meta:
        db_table = 'payments'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['course', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        course_name = self.course.title if self.course else 'Global Subscription'
        return f"{self.user.get_full_name()} - {course_name} - {self.status}"

    def approve(self, admin_user):
        """
        Approve the payment and create subscription.
        Creates payout record for instructor.
        """
        from django.utils import timezone
        from subscriptions.models import Subscription
        from payouts.models import Payout

        self.status = 'approved'
        self.reviewed_by = admin_user
        self.reviewed_at = timezone.now()
        self.save()

        # Create subscription
        subscription = Subscription.objects.create(
            user=self.user,
            course=self.course,
            access_type=self.access_type,
            is_global=self.is_global,
            payment=self
        )

        # Create payout for instructor (if course-specific)
        if self.course and not self.is_global:
            Payout.objects.create(
                instructor=self.course.instructor,
                course=self.course,
                payment=self,
                amount=self.amount,
                status='pending'
            )

            # Increment course enrollment count
            self.course.increment_enrollment_count()

        # Send notification to student
        from notifications.services import NotificationService
        NotificationService.send_payment_approved(self.user, self, subscription)

        return subscription

    def reject(self, admin_user, reason):
        """Reject the payment."""
        from django.utils import timezone

        self.status = 'rejected'
        self.reviewed_by = admin_user
        self.reviewed_at = timezone.now()
        self.rejection_reason = reason
        self.save()

        # Send notification to student
        from notifications.services import NotificationService
        NotificationService.send_payment_rejected(self.user, self, reason)

        return True

    @property
    def is_pending(self):
        """Check if payment is pending."""
        return self.status == 'pending'

    @property
    def is_approved(self):
        """Check if payment is approved."""
        return self.status == 'approved'

    @property
    def is_rejected(self):
        """Check if payment is rejected."""
        return self.status == 'rejected'


class PaymentHistory(TimeStampedModel):
    """
    Audit trail for payment status changes.
    """
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='history')
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'payment_history'
        verbose_name = 'Payment History'
        verbose_name_plural = 'Payment Histories'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.payment} - {self.old_status} to {self.new_status}"
