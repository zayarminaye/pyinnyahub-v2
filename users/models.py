"""
User models for Pyinnya Hub LMS.
Implements custom user model with role-based access control.
"""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import FileExtensionValidator
from core.models import TimeStampedModel
from core.utils import (
    generate_unique_filename,
    validate_profile_picture,
    validate_instructor_resume,
    validate_instructor_certificate,
    process_uploaded_image
)


class UserManager(BaseUserManager):
    """
    Custom user manager for email-based authentication.
    """
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user."""
        if not email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

    def students(self):
        """Return only students."""
        return self.filter(role='student', is_active=True)

    def instructors(self):
        """Return only instructors."""
        return self.filter(role='instructor', is_active=True)

    def admins(self):
        """Return only admins."""
        return self.filter(role='admin', is_active=True)


class User(AbstractUser):
    """
    Custom user model with role-based access control.
    Supports three roles: student, instructor, admin.
    """
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('instructor', 'Instructor'),
        ('admin', 'Admin'),
    )

    # Remove username, use email for authentication
    username = None
    email = models.EmailField(unique=True, db_index=True)

    # Role and profile fields
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student', db_index=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(blank=True, null=True, help_text='Short biography (for instructors)')
    profile_picture = models.ImageField(
        upload_to=generate_unique_filename,
        blank=True,
        null=True,
        validators=[validate_profile_picture],
        help_text='Profile picture (max 5MB, JPG/PNG, will be optimized)'
    )

    # Additional fields
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)

    # Instructor-specific fields
    expertise = models.CharField(max_length=255, blank=True, null=True, help_text='Areas of expertise')
    years_of_experience = models.PositiveIntegerField(blank=True, null=True)
    education = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    social_links = models.JSONField(default=dict, blank=True, help_text='Social media links')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email', 'role']),
            models.Index(fields=['is_active', 'role']),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip() or self.email

    @property
    def is_student(self):
        """Check if user is a student."""
        return self.role == 'student'

    @property
    def is_instructor(self):
        """Check if user is an instructor."""
        return self.role == 'instructor'

    @property
    def is_admin_user(self):
        """Check if user is an admin."""
        return self.role == 'admin' or self.is_staff or self.is_superuser

    def promote_to_instructor(self):
        """Promote student to instructor role."""
        if self.role == 'student':
            self.role = 'instructor'
            self.save(update_fields=['role'])
            return True
        return False

    def demote_to_student(self):
        """Demote instructor to student role."""
        if self.role == 'instructor':
            self.role = 'student'
            self.save(update_fields=['role'])
            return True
        return False

    def save(self, *args, **kwargs):
        """Override save to process profile picture."""
        # Process profile picture if it's being uploaded
        if self.profile_picture and hasattr(self.profile_picture, 'file'):
            try:
                # Check if this is a new upload (not already processed)
                if not self.pk or (self.pk and self._state.adding is False):
                    # Try to get the old instance
                    try:
                        old_instance = User.objects.get(pk=self.pk)
                        # Only process if the file has changed
                        if old_instance.profile_picture != self.profile_picture:
                            self.profile_picture = process_uploaded_image(
                                self.profile_picture,
                                max_width=800,
                                max_height=800,
                                quality=85,
                                format='JPEG'
                            )
                    except User.DoesNotExist:
                        # New user, process the image
                        self.profile_picture = process_uploaded_image(
                            self.profile_picture,
                            max_width=800,
                            max_height=800,
                            quality=85,
                            format='JPEG'
                        )
            except Exception as e:
                # Log error but don't prevent save
                print(f"Error processing profile picture: {e}")

        super().save(*args, **kwargs)

    def get_instructor_stats(self):
        """Get instructor statistics (courses, students, earnings)."""
        if not self.is_instructor:
            return None

        from courses.models import Course
        from subscriptions.models import Subscription
        from payouts.models import Payout

        courses = Course.objects.filter(instructor=self)
        total_courses = courses.count()
        published_courses = courses.filter(status='approved', is_published=True).count()

        # Get total students enrolled in instructor's courses
        total_students = Subscription.objects.filter(
            course__instructor=self,
            is_active=True
        ).values('user').distinct().count()

        # Get total earnings
        total_earnings = Payout.objects.filter(
            instructor=self
        ).aggregate(models.Sum('amount'))['amount__sum'] or 0

        pending_earnings = Payout.objects.filter(
            instructor=self,
            status='pending'
        ).aggregate(models.Sum('amount'))['amount__sum'] or 0

        return {
            'total_courses': total_courses,
            'published_courses': published_courses,
            'total_students': total_students,
            'total_earnings': total_earnings,
            'pending_earnings': pending_earnings,
        }


class InstructorApplication(TimeStampedModel):
    """
    Model for instructor applications.
    Students can apply to become instructors, and admins can approve/reject.
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='instructor_applications')
    experience = models.TextField(help_text='Teaching or professional experience')
    expertise = models.CharField(max_length=255, help_text='Areas of expertise')
    education = models.TextField(blank=True, null=True)
    motivation = models.TextField(help_text='Why do you want to become an instructor?')

    # Optional document uploads
    resume = models.FileField(
        upload_to=generate_unique_filename,
        blank=True,
        null=True,
        validators=[validate_instructor_resume],
        help_text='Resume/CV (max 5MB, PDF/DOC/DOCX)'
    )
    certificates = models.FileField(
        upload_to=generate_unique_filename,
        blank=True,
        null=True,
        validators=[validate_instructor_certificate],
        help_text='Certificates (max 5MB, PDF/JPG/PNG)'
    )

    # Review fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_applications'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True, null=True, help_text='Internal admin notes')
    rejection_reason = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'instructor_applications'
        verbose_name = 'Instructor Application'
        verbose_name_plural = 'Instructor Applications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.status}"

    def approve(self, admin_user):
        """Approve the application and promote user to instructor."""
        from django.utils import timezone

        self.status = 'approved'
        self.reviewed_by = admin_user
        self.reviewed_at = timezone.now()
        self.save()

        # Promote user to instructor
        self.user.promote_to_instructor()

        # Send notification
        from notifications.services import NotificationService
        NotificationService.send_instructor_application_approved(self.user)

        return True

    def reject(self, admin_user, reason):
        """Reject the application."""
        from django.utils import timezone

        self.status = 'rejected'
        self.reviewed_by = admin_user
        self.reviewed_at = timezone.now()
        self.rejection_reason = reason
        self.save()

        # Send notification
        from notifications.services import NotificationService
        NotificationService.send_instructor_application_rejected(self.user, reason)

        return True

    @property
    def is_pending(self):
        """Check if application is pending."""
        return self.status == 'pending'

    @property
    def is_approved(self):
        """Check if application is approved."""
        return self.status == 'approved'

    @property
    def is_rejected(self):
        """Check if application is rejected."""
        return self.status == 'rejected'
