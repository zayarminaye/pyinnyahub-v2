"""
Payout models for Pyinnya Hub LMS.
Manages instructor earnings and payout processing.
"""
from django.db import models
from django.conf import settings
from core.models import TimeStampedModel


class PayoutManager(models.Manager):
    """Custom manager for Payout model."""

    def pending(self):
        """Return pending payouts."""
        return self.filter(status='pending')

    def paid(self):
        """Return paid payouts."""
        return self.filter(status='paid')

    def by_instructor(self, instructor):
        """Return payouts for specific instructor."""
        return self.filter(instructor=instructor)

    def total_earnings(self, instructor):
        """Calculate total earnings for instructor."""
        return self.filter(
            instructor=instructor,
            status='paid'
        ).aggregate(models.Sum('amount'))['amount__sum'] or 0

    def pending_earnings(self, instructor):
        """Calculate pending earnings for instructor."""
        return self.filter(
            instructor=instructor,
            status='pending'
        ).aggregate(models.Sum('amount'))['amount__sum'] or 0


class Payout(TimeStampedModel):
    """
    Payout model for tracking instructor earnings.
    Created when a payment is approved for an instructor's course.
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    )

    # Payout details
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payouts',
        limit_choices_to={'role': 'instructor'}
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='payouts'
    )
    payment = models.ForeignKey(
        'payments.Payment',
        on_delete=models.SET_NULL,
        null=True,
        related_name='payouts'
    )

    # Amount
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Amount to be paid to instructor'
    )
    commission = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Platform commission (deducted from amount)'
    )
    net_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Net amount after commission'
    )

    # Status and processing
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_payouts'
    )
    processed_at = models.DateTimeField(null=True, blank=True)

    # Payment method details
    payment_method = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Method used to pay instructor (bank transfer, etc.)'
    )
    transaction_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Transaction reference ID'
    )

    # Notes
    admin_notes = models.TextField(
        blank=True,
        null=True,
        help_text='Internal admin notes'
    )
    notes_to_instructor = models.TextField(
        blank=True,
        null=True,
        help_text='Notes visible to instructor'
    )

    objects = PayoutManager()

    class Meta:
        db_table = 'payouts'
        verbose_name = 'Payout'
        verbose_name_plural = 'Payouts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['instructor', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['course', 'status']),
        ]

    def __str__(self):
        return f"{self.instructor.get_full_name()} - {self.course.title} - {self.amount}"

    def save(self, *args, **kwargs):
        """Calculate net amount if not set."""
        if not self.net_amount:
            self.net_amount = self.amount - self.commission
        super().save(*args, **kwargs)

    def mark_as_processing(self, admin_user):
        """Mark payout as processing."""
        self.status = 'processing'
        self.processed_by = admin_user
        self.save(update_fields=['status', 'processed_by'])

    def mark_as_paid(self, admin_user, transaction_id=None, payment_method=None, notes=None):
        """Mark payout as paid."""
        from django.utils import timezone

        self.status = 'paid'
        self.processed_by = admin_user
        self.processed_at = timezone.now()

        if transaction_id:
            self.transaction_id = transaction_id
        if payment_method:
            self.payment_method = payment_method
        if notes:
            self.notes_to_instructor = notes

        self.save()

        # Send notification to instructor
        from notifications.services import NotificationService
        NotificationService.send_payout_completed(self)

        return True

    def cancel(self, admin_user, reason=None):
        """Cancel the payout."""
        self.status = 'cancelled'
        self.processed_by = admin_user
        if reason:
            self.admin_notes = reason
        self.save()

        # Send notification to instructor
        from notifications.services import NotificationService
        NotificationService.send_payout_cancelled(self, reason)

        return True

    @property
    def is_pending(self):
        """Check if payout is pending."""
        return self.status == 'pending'

    @property
    def is_paid(self):
        """Check if payout is paid."""
        return self.status == 'paid'

    @property
    def is_processing(self):
        """Check if payout is processing."""
        return self.status == 'processing'


class PayoutBatch(TimeStampedModel):
    """
    Batch processing of multiple payouts together.
    Useful for processing monthly payouts.
    """
    name = models.CharField(max_length=255, help_text='Batch name (e.g., January 2025 Payouts)')
    payouts = models.ManyToManyField(Payout, related_name='batches')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    processed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'payout_batches'
        verbose_name = 'Payout Batch'
        verbose_name_plural = 'Payout Batches'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def calculate_total(self):
        """Calculate total amount for all payouts in batch."""
        self.total_amount = self.payouts.aggregate(
            models.Sum('net_amount')
        )['net_amount__sum'] or 0
        self.save(update_fields=['total_amount'])
