"""
Course models for Pyinnya Hub LMS.
Comprehensive course structure with categories, sections, and lessons.
"""
from django.db import models
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.conf import settings
from core.models import TimeStampedModel, SoftDeleteModel, PublishableModel
from core.utils import generate_unique_filename


class Category(TimeStampedModel):
    """
    Course categories for organizing courses.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True, help_text='Icon class or emoji')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text='Display order')

    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_course_count(self):
        """Get total number of published courses in this category."""
        return self.courses.filter(status='approved', is_published=True).count()


class Tag(TimeStampedModel):
    """
    Tags for courses to improve searchability.
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        db_table = 'tags'
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['name']

    def __str__(self):
        return self.name


class CourseManager(models.Manager):
    """Custom manager for Course model."""

    def published(self):
        """Return only published and approved courses."""
        return self.filter(status='approved', is_published=True)

    def featured(self):
        """Return only featured courses."""
        return self.published().filter(is_featured=True)

    def by_instructor(self, instructor):
        """Return courses by specific instructor."""
        return self.filter(instructor=instructor)

    def pending_approval(self):
        """Return courses pending admin approval."""
        return self.filter(status='pending')


class Course(SoftDeleteModel, PublishableModel):
    """
    Main course model with approval workflow and pricing.
    """
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    ACCESS_TYPE_CHOICES = (
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('lifetime', 'Lifetime'),
    )

    # Basic information
    title = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=500, help_text='Brief course summary')

    # Instructor and categorization
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses',
        limit_choices_to={'role': 'instructor'}
    )
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='courses')
    tags = models.ManyToManyField(Tag, blank=True, related_name='courses')

    # Media
    thumbnail = models.ImageField(
        upload_to=generate_unique_filename,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        help_text='Course thumbnail image'
    )
    promo_video = models.FileField(
        upload_to=generate_unique_filename,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'webm'])],
        help_text='Promotional video'
    )

    # Pricing and access
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    access_type = models.CharField(
        max_length=20,
        choices=ACCESS_TYPE_CHOICES,
        default='monthly',
        help_text='Subscription access type'
    )

    # Course metadata
    level = models.CharField(
        max_length=20,
        choices=(
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
        ),
        default='beginner'
    )
    language = models.CharField(max_length=50, default='Burmese')
    duration_hours = models.PositiveIntegerField(
        default=0,
        help_text='Estimated course duration in hours'
    )

    # Requirements and outcomes
    requirements = models.JSONField(
        default=list,
        blank=True,
        help_text='Prerequisites for the course'
    )
    what_you_will_learn = models.JSONField(
        default=list,
        blank=True,
        help_text='Learning outcomes'
    )

    # Status and approval
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        db_index=True
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_courses'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)

    # Additional features
    is_featured = models.BooleanField(default=False, db_index=True)
    enrollment_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    rating_average = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    rating_count = models.PositiveIntegerField(default=0)

    objects = CourseManager()

    class Meta:
        db_table = 'courses'
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['instructor', 'status']),
            models.Index(fields=['status', 'is_published']),
            models.Index(fields=['category', 'is_published']),
            models.Index(fields=['-enrollment_count']),
            models.Index(fields=['-rating_average']),
        ]

    def __str__(self):
        return self.title

    def submit_for_review(self):
        """Submit course for admin review."""
        if self.status == 'draft':
            self.status = 'pending'
            self.save(update_fields=['status'])
            return True
        return False

    def approve(self, admin_user):
        """Approve the course."""
        from django.utils import timezone

        self.status = 'approved'
        self.reviewed_by = admin_user
        self.reviewed_at = timezone.now()
        self.save(update_fields=['status', 'reviewed_by', 'reviewed_at'])

        # Send notification to instructor
        from notifications.services import NotificationService
        NotificationService.send_course_approved(self)

        return True

    def reject(self, admin_user, reason):
        """Reject the course."""
        from django.utils import timezone

        self.status = 'rejected'
        self.reviewed_by = admin_user
        self.reviewed_at = timezone.now()
        self.rejection_reason = reason
        self.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'rejection_reason'])

        # Send notification to instructor
        from notifications.services import NotificationService
        NotificationService.send_course_rejected(self, reason)

        return True

    def increment_view_count(self):
        """Increment the view count."""
        self.view_count += 1
        self.save(update_fields=['view_count'])

    def increment_enrollment_count(self):
        """Increment the enrollment count."""
        self.enrollment_count += 1
        self.save(update_fields=['enrollment_count'])

    def update_rating(self):
        """Recalculate average rating from reviews."""
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            self.rating_average = reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0
            self.rating_count = reviews.count()
        else:
            self.rating_average = 0
            self.rating_count = 0
        self.save(update_fields=['rating_average', 'rating_count'])

    @property
    def is_approved(self):
        """Check if course is approved."""
        return self.status == 'approved'

    @property
    def is_pending(self):
        """Check if course is pending review."""
        return self.status == 'pending'

    @property
    def total_lessons(self):
        """Get total number of lessons."""
        return Lesson.objects.filter(section__course=self).count()

    @property
    def total_duration_minutes(self):
        """Get total duration in minutes."""
        return Lesson.objects.filter(section__course=self).aggregate(
            models.Sum('duration_minutes')
        )['duration_minutes__sum'] or 0


class Section(TimeStampedModel):
    """
    Course sections for organizing lessons.
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'sections'
        verbose_name = 'Section'
        verbose_name_plural = 'Sections'
        ordering = ['course', 'order']
        unique_together = ['course', 'order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    @property
    def lesson_count(self):
        """Get number of lessons in this section."""
        return self.lessons.count()

    @property
    def total_duration(self):
        """Get total duration of all lessons in minutes."""
        return self.lessons.aggregate(
            models.Sum('duration_minutes')
        )['duration_minutes__sum'] or 0


class Lesson(TimeStampedModel):
    """
    Individual lessons within a section.
    Supports video, text, attachments, and quizzes.
    """
    CONTENT_TYPE_CHOICES = (
        ('video', 'Video'),
        ('text', 'Text'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
    )

    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default='video')
    order = models.PositiveIntegerField(default=0)

    # Content
    description = models.TextField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True, help_text='Video file or external URL')
    video_file = models.FileField(
        upload_to=generate_unique_filename,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'webm', 'mov'])]
    )
    text_content = models.TextField(blank=True, null=True, help_text='Markdown or HTML content')
    duration_minutes = models.PositiveIntegerField(default=0, help_text='Lesson duration in minutes')

    # Attachments
    attachments = models.JSONField(
        default=list,
        blank=True,
        help_text='List of attachment file paths'
    )

    # Access control
    is_preview = models.BooleanField(
        default=False,
        help_text='Allow preview without enrollment'
    )

    class Meta:
        db_table = 'lessons'
        verbose_name = 'Lesson'
        verbose_name_plural = 'Lessons'
        ordering = ['section', 'order']
        unique_together = ['section', 'order']

    def __str__(self):
        return f"{self.section.course.title} - {self.section.title} - {self.title}"

    @property
    def course(self):
        """Get the course this lesson belongs to."""
        return self.section.course


class LessonAttachment(TimeStampedModel):
    """
    File attachments for lessons (PDFs, documents, resources).
    """
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='lesson_attachments')
    title = models.CharField(max_length=255)
    file = models.FileField(
        upload_to=generate_unique_filename,
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'doc', 'docx', 'ppt', 'pptx', 'zip', 'rar']
        )]
    )
    file_size = models.PositiveIntegerField(help_text='File size in bytes')

    class Meta:
        db_table = 'lesson_attachments'
        verbose_name = 'Lesson Attachment'
        verbose_name_plural = 'Lesson Attachments'

    def __str__(self):
        return f"{self.lesson.title} - {self.title}"


class CourseReview(TimeStampedModel):
    """
    Student reviews and ratings for courses.
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='course_reviews')
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Rating from 1 to 5'
    )
    review = models.TextField()
    is_approved = models.BooleanField(default=True)

    class Meta:
        db_table = 'course_reviews'
        verbose_name = 'Course Review'
        verbose_name_plural = 'Course Reviews'
        unique_together = ['course', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.course.title} ({self.rating}/5)"

    def save(self, *args, **kwargs):
        """Update course rating when review is saved."""
        super().save(*args, **kwargs)
        self.course.update_rating()


class Wishlist(TimeStampedModel):
    """
    Student wishlists for courses they're interested in.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlists')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='wishlisted_by')

    class Meta:
        db_table = 'wishlists'
        verbose_name = 'Wishlist'
        verbose_name_plural = 'Wishlists'
        unique_together = ['user', 'course']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.course.title}"
