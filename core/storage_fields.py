"""
Custom model fields that use the centralized storage service.
"""
from django.db import models
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile


class ManagedFileField(models.FileField):
    """
    Custom FileField that uses our storage service for organized uploads.
    """

    def __init__(self, *args, storage_category=None, upload_function=None, **kwargs):
        """
        Args:
            storage_category: Category from StorageCategory
            upload_function: Function from storage_service to handle upload
        """
        self.storage_category = storage_category
        self.upload_function = upload_function
        super().__init__(*args, **kwargs)


class ManagedImageField(models.ImageField):
    """
    Custom ImageField that uses our storage service for organized uploads.
    """

    def __init__(self, *args, storage_category=None, upload_function=None, **kwargs):
        """
        Args:
            storage_category: Category from StorageCategory
            upload_function: Function from storage_service to handle upload
        """
        self.storage_category = storage_category
        self.upload_function = upload_function
        super().__init__(*args, **kwargs)
