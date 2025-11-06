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
