"""
Centralized file storage service with provider abstraction.
Supports Cloudinary and AWS S3 with easy migration between them.
"""
import os
import logging
from typing import Optional, Tuple
from django.core.files.uploadedfile import UploadedFile
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError
from decouple import config


logger = logging.getLogger(__name__)


class StorageCategory:
    """
    Organized storage paths for different file types.
    Maps to Cloudinary folders or S3 buckets/prefixes.

    Best practices followed:
    - Separate folders by content type for easy management
    - Environment-specific prefixes (dev/staging/prod)
    - Clear naming conventions
    - Public vs private content separation
    """

    # Environment prefix (auto-detected)
    @staticmethod
    def _get_env_prefix():
        """Get environment-specific prefix."""
        env = config('ENVIRONMENT', default='dev')  # dev/staging/prod
        return f"{env}/" if env != 'prod' else ''

    # PUBLIC CONTENT (accessible without authentication)

    # User-related public files
    PROFILE_PICTURES = 'public/users/profiles'

    # Course-related public files (browsable by anyone)
    COURSE_THUMBNAILS = 'public/courses/thumbnails'
    COURSE_PROMO_VIDEOS = 'public/courses/promo-videos'

    # PRIVATE CONTENT (requires authentication/authorization)

    # Instructor application files (admin-only access)
    INSTRUCTOR_RESUMES = 'private/instructors/resumes'
    INSTRUCTOR_CERTIFICATES = 'private/instructors/certificates'

    # Lesson content (student-only after enrollment)
    LESSON_VIDEOS = 'private/lessons/videos'
    LESSON_ATTACHMENTS = 'private/lessons/attachments'
    LESSON_TEXT_FILES = 'private/lessons/text-files'

    # Payment receipts (user+admin access only)
    PAYMENT_RECEIPTS = 'private/payments/receipts'

    # Temporary files (wizard, drafts, etc.) - auto-cleanup
    TEMP_UPLOADS = 'temp/uploads'

    @classmethod
    def get_full_path(cls, category: str) -> str:
        """Get full path with environment prefix."""
        env_prefix = cls._get_env_prefix()
        return f"{env_prefix}{category}"


class FileUploadError(Exception):
    """Custom exception for file upload errors with user-friendly messages."""

    def __init__(self, message: str, user_message: str = None, message_key: str = None, original_error: Exception = None, **context):
        """
        Args:
            message: Technical error message for logging
            user_message: User-friendly message (if not using message_key)
            message_key: Key to SystemMessage for editable messages
            original_error: Original exception if any
            **context: Variables for message substitution
        """
        super().__init__(message)

        # Try to get message from SystemMessage first
        if message_key:
            from core.models import SystemMessage
            self.user_message = SystemMessage.get(message_key, lang='both', **context)
        elif user_message:
            self.user_message = user_message
        else:
            self.user_message = self._get_default_user_message()

        self.original_error = original_error

    def _get_default_user_message(self):
        """Fallback if no message_key or user_message provided."""
        try:
            from core.models import SystemMessage
            return SystemMessage.get('file_upload_generic_error', lang='both')
        except:
            return (
                "ဖိုင်တင်ရာတွင် အမှားအယွင်း ရှိပါသည်။ ကျေးဇူးပြု၍ ထပ်မံကြိုးစားပါ။\n"
                "Error uploading file. Please try again."
            )


class StorageService:
    """
    Centralized storage service with provider abstraction.
    Handles file uploads, deletions, and URL generation.
    """

    def __init__(self):
        self.use_cloudinary = config('USE_CLOUDINARY', default=False, cast=bool)
        self.use_s3 = config('USE_S3', default=False, cast=bool)

    def _generate_unique_filename(self, original_filename: str, category: str) -> str:
        """
        Generate unique filename with category prefix.
        Best practice: env/category/YYYY/MM/uniqueid_filename.ext

        Args:
            original_filename: Original file name
            category: Storage category (from StorageCategory)

        Returns:
            str: Full path with unique filename
        """
        import uuid
        from django.utils import timezone
        from core.utils import sanitize_filename

        # Get full path with environment prefix
        full_category = StorageCategory.get_full_path(category)

        # Sanitize the filename
        safe_filename = sanitize_filename(original_filename)

        # Generate unique identifier
        unique_id = uuid.uuid4().hex[:12]

        # Add timestamp for better organization (separate by year and month)
        year = timezone.now().strftime('%Y')
        month = timezone.now().strftime('%m')

        # Split name and extension
        name, ext = os.path.splitext(safe_filename)

        # Construct path: env/category/YYYY/MM/uniqueid_filename.ext
        # Example: prod/public/courses/thumbnails/2025/11/a1b2c3d4e5f6_my-course.jpg
        return f"{full_category}/{year}/{month}/{unique_id}_{name}{ext}"

    def upload_file(
        self,
        file: UploadedFile,
        category: str,
        validator_func: callable = None,
        metadata: dict = None
    ) -> Tuple[str, str]:
        """
        Upload file to storage with validation and error handling.

        Args:
            file: Uploaded file object
            category: Storage category (from StorageCategory)
            validator_func: Optional validation function
            metadata: Optional metadata dict (tags, context, etc.)

        Returns:
            Tuple[str, str]: (file_path, file_url)

        Raises:
            FileUploadError: If upload fails
        """
        try:
            # Validate file if validator provided
            if validator_func:
                try:
                    validator_func(file)
                except ValidationError as e:
                    raise FileUploadError(
                        f"Validation failed: {str(e)}",
                        user_message=f"ဖိုင် စစ်ဆေးမှု မအောင်မြင်ပါ။\n{str(e)}",
                        original_error=e
                    )

            # Generate unique filename
            file_path = self._generate_unique_filename(file.name, category)

            # Upload based on provider
            if self.use_cloudinary:
                file_url = self._upload_to_cloudinary(file, file_path, metadata)
            elif self.use_s3:
                file_url = self._upload_to_s3(file, file_path, metadata)
            else:
                file_url = self._upload_to_local(file, file_path)

            logger.info(f"File uploaded successfully: {file_path}")
            return file_path, file_url

        except FileUploadError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error uploading file: {str(e)}", exc_info=True)
            raise FileUploadError(
                f"Upload failed: {str(e)}",
                user_message=(
                    "ဖိုင်တင်ရာတွင် အမှားအယွင်း ရှိပါသည်။ "
                    "ကျေးဇူးပြု၍ အင်တာနက် ချိတ်ဆက်မှုကို စစ်ဆေးပြီး ထပ်မံကြိုးစားပါ။\n"
                    "Error uploading file. Please check your internet connection and try again."
                ),
                original_error=e
            )

    def _upload_to_cloudinary(self, file, file_path: str, metadata: dict = None) -> str:
        """Upload file to Cloudinary with organized folders."""
        try:
            import cloudinary
            import cloudinary.uploader

            # Extract folder and public_id from file_path
            # e.g., "courses/thumbnails/202511/abc123_image.jpg"
            folder = os.path.dirname(file_path)
            filename = os.path.basename(file_path)
            public_id = os.path.splitext(filename)[0]

            # Prepare upload options
            options = {
                'folder': folder,
                'public_id': public_id,
                'resource_type': 'auto',  # Auto-detect image/video/raw
                'use_filename': True,
                'unique_filename': False,  # We already made it unique
                'overwrite': False,
            }

            # Add metadata/tags if provided
            if metadata:
                if 'tags' in metadata:
                    options['tags'] = metadata['tags']
                if 'context' in metadata:
                    options['context'] = metadata['context']

            # Upload to Cloudinary
            result = cloudinary.uploader.upload(file, **options)

            return result['secure_url']

        except Exception as e:
            logger.error(f"Cloudinary upload error: {str(e)}", exc_info=True)
            raise FileUploadError(
                f"Cloudinary upload failed: {str(e)}",
                user_message=(
                    "ဖိုင်တင်ရာတွင် အမှားအယွင်း ရှိပါသည်။ ကျေးဇူးပြု၍ ထပ်မံကြိုးစားပါ။\n"
                    "Error uploading to cloud storage. Please try again."
                ),
                original_error=e
            )

    def _upload_to_s3(self, file, file_path: str, metadata: dict = None) -> str:
        """Upload file to AWS S3."""
        try:
            from storages.backends.s3boto3 import S3Boto3Storage

            storage = S3Boto3Storage()

            # Upload file
            saved_path = storage.save(file_path, file)
            file_url = storage.url(saved_path)

            return file_url

        except Exception as e:
            logger.error(f"S3 upload error: {str(e)}", exc_info=True)
            raise FileUploadError(
                f"S3 upload failed: {str(e)}",
                user_message=(
                    "ဖိုင်တင်ရာတွင် အမှားအယွင်း ရှိပါသည်။ ကျေးဇူးပြု၍ ထပ်မံကြိုးစားပါ။\n"
                    "Error uploading to cloud storage. Please try again."
                ),
                original_error=e
            )

    def _upload_to_local(self, file, file_path: str) -> str:
        """Upload file to local filesystem."""
        try:
            # Use default_storage (works with local and cloud)
            saved_path = default_storage.save(file_path, file)
            file_url = default_storage.url(saved_path)

            return file_url

        except Exception as e:
            logger.error(f"Local storage upload error: {str(e)}", exc_info=True)
            raise FileUploadError(
                f"Local upload failed: {str(e)}",
                user_message=(
                    "ဖိုင်သိမ်းဆည်းရာတွင် အမှားအယွင်း ရှိပါသည်။ ကျေးဇူးပြု၍ ထပ်မံကြိုးစားပါ။\n"
                    "Error saving file. Please try again."
                ),
                original_error=e
            )

    def delete_file(self, file_path: str) -> bool:
        """
        Delete file from storage.

        Args:
            file_path: Path to file to delete

        Returns:
            bool: True if deleted successfully
        """
        try:
            if self.use_cloudinary:
                return self._delete_from_cloudinary(file_path)
            elif self.use_s3:
                return self._delete_from_s3(file_path)
            else:
                return self._delete_from_local(file_path)

        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {str(e)}", exc_info=True)
            return False

    def _delete_from_cloudinary(self, file_path: str) -> bool:
        """Delete file from Cloudinary."""
        try:
            import cloudinary.uploader

            # Extract public_id from file_path
            # Remove extension and convert path separators
            public_id = os.path.splitext(file_path)[0]

            result = cloudinary.uploader.destroy(public_id)
            return result.get('result') == 'ok'

        except Exception as e:
            logger.error(f"Cloudinary delete error: {str(e)}", exc_info=True)
            return False

    def _delete_from_s3(self, file_path: str) -> bool:
        """Delete file from S3."""
        try:
            from storages.backends.s3boto3 import S3Boto3Storage

            storage = S3Boto3Storage()
            storage.delete(file_path)
            return True

        except Exception as e:
            logger.error(f"S3 delete error: {str(e)}", exc_info=True)
            return False

    def _delete_from_local(self, file_path: str) -> bool:
        """Delete file from local storage."""
        try:
            if default_storage.exists(file_path):
                default_storage.delete(file_path)
                return True
            return False

        except Exception as e:
            logger.error(f"Local delete error: {str(e)}", exc_info=True)
            return False

    def get_file_url(self, file_path: str, transformations: dict = None) -> Optional[str]:
        """
        Get public URL for a file with optional transformations.

        Args:
            file_path: Path to file
            transformations: Optional dict of transformations (Cloudinary/S3 CDN)
                Examples:
                - {'width': 300, 'height': 200, 'crop': 'fill'}
                - {'quality': 'auto', 'fetch_format': 'auto'}

        Returns:
            str: Public URL or None
        """
        try:
            if self.use_cloudinary:
                import cloudinary

                public_id = os.path.splitext(file_path)[0]

                if transformations:
                    return cloudinary.CloudinaryImage(public_id).build_url(**transformations)
                else:
                    return cloudinary.CloudinaryImage(public_id).build_url()
            else:
                # For S3/local, return direct URL (transformations require CDN setup)
                return default_storage.url(file_path)
        except Exception as e:
            logger.error(f"Error getting file URL: {str(e)}", exc_info=True)
            return None

    def get_thumbnail_url(self, file_path: str, width: int = 300, height: int = 200) -> Optional[str]:
        """
        Get optimized thumbnail URL for an image.

        Args:
            file_path: Path to image file
            width: Thumbnail width
            height: Thumbnail height

        Returns:
            str: Thumbnail URL
        """
        return self.get_file_url(file_path, {
            'width': width,
            'height': height,
            'crop': 'fill',
            'quality': 'auto',
            'fetch_format': 'auto'  # Auto WebP for browsers that support it
        })

    def get_responsive_image_urls(self, file_path: str) -> dict:
        """
        Get multiple image sizes for responsive design.
        Real-world LMS best practice.

        Args:
            file_path: Path to image file

        Returns:
            dict: Dictionary with different sizes
                {'thumbnail': url, 'small': url, 'medium': url, 'large': url, 'original': url}
        """
        return {
            'thumbnail': self.get_thumbnail_url(file_path, 150, 150),
            'small': self.get_file_url(file_path, {'width': 400, 'quality': 'auto'}),
            'medium': self.get_file_url(file_path, {'width': 800, 'quality': 'auto'}),
            'large': self.get_file_url(file_path, {'width': 1200, 'quality': 'auto'}),
            'original': self.get_file_url(file_path)
        }


# Singleton instance
storage_service = StorageService()


# Convenience functions for common upload scenarios

def upload_profile_picture(file: UploadedFile) -> Tuple[str, str]:
    """Upload user profile picture."""
    from core.utils import validate_profile_picture

    return storage_service.upload_file(
        file,
        StorageCategory.PROFILE_PICTURES,
        validator_func=validate_profile_picture,
        metadata={'tags': ['profile', 'user']}
    )


def upload_instructor_resume(file: UploadedFile, instructor_id: int) -> Tuple[str, str]:
    """Upload instructor resume."""
    from core.utils import validate_instructor_resume

    return storage_service.upload_file(
        file,
        StorageCategory.INSTRUCTOR_RESUMES,
        validator_func=validate_instructor_resume,
        metadata={
            'tags': ['instructor', 'resume'],
            'context': {'instructor_id': str(instructor_id)}
        }
    )


def upload_instructor_certificates(file: UploadedFile, instructor_id: int) -> Tuple[str, str]:
    """Upload instructor certificates."""
    from core.utils import validate_instructor_certificate

    return storage_service.upload_file(
        file,
        StorageCategory.INSTRUCTOR_CERTIFICATES,
        validator_func=validate_instructor_certificate,
        metadata={
            'tags': ['instructor', 'certificate'],
            'context': {'instructor_id': str(instructor_id)}
        }
    )


def upload_course_thumbnail(file: UploadedFile, course_id: int = None) -> Tuple[str, str]:
    """Upload course thumbnail."""
    from core.utils import validate_course_thumbnail, process_uploaded_image

    # Process and optimize the image
    try:
        processed_file = process_uploaded_image(file, max_width=1200, max_height=675, quality=85)
    except Exception as e:
        raise FileUploadError(
            f"Error processing image: {str(e)}",
            user_message=f"ပုံ process လုပ်ရာတွင် အမှားရှိပါသည်။\n{str(e)}",
            original_error=e
        )

    metadata = {'tags': ['course', 'thumbnail']}
    if course_id:
        metadata['context'] = {'course_id': str(course_id)}

    return storage_service.upload_file(
        processed_file,
        StorageCategory.COURSE_THUMBNAILS,
        validator_func=validate_course_thumbnail,
        metadata=metadata
    )


def upload_course_promo_video(file: UploadedFile, course_id: int = None) -> Tuple[str, str]:
    """Upload course promotional video."""
    from core.utils import validate_lesson_video

    metadata = {'tags': ['course', 'promo', 'video']}
    if course_id:
        metadata['context'] = {'course_id': str(course_id)}

    return storage_service.upload_file(
        file,
        StorageCategory.COURSE_PROMO_VIDEOS,
        validator_func=validate_lesson_video,
        metadata=metadata
    )


def upload_lesson_video(file: UploadedFile, lesson_id: int = None) -> Tuple[str, str]:
    """Upload lesson video."""
    from core.utils import validate_lesson_video

    metadata = {'tags': ['lesson', 'video']}
    if lesson_id:
        metadata['context'] = {'lesson_id': str(lesson_id)}

    return storage_service.upload_file(
        file,
        StorageCategory.LESSON_VIDEOS,
        validator_func=validate_lesson_video,
        metadata=metadata
    )


def upload_lesson_attachment(file: UploadedFile, lesson_id: int = None) -> Tuple[str, str]:
    """Upload lesson attachment."""
    from core.utils import validate_lesson_attachment

    metadata = {'tags': ['lesson', 'attachment']}
    if lesson_id:
        metadata['context'] = {'lesson_id': str(lesson_id)}

    return storage_service.upload_file(
        file,
        StorageCategory.LESSON_ATTACHMENTS,
        validator_func=validate_lesson_attachment,
        metadata=metadata
    )


def upload_payment_receipt(file: UploadedFile, payment_id: int = None) -> Tuple[str, str]:
    """Upload payment receipt."""
    from core.utils import validate_payment_receipt

    metadata = {'tags': ['payment', 'receipt']}
    if payment_id:
        metadata['context'] = {'payment_id': str(payment_id)}

    return storage_service.upload_file(
        file,
        StorageCategory.PAYMENT_RECEIPTS,
        validator_func=validate_payment_receipt,
        metadata=metadata
    )


def delete_file(file_path: str) -> bool:
    """Delete file from storage."""
    return storage_service.delete_file(file_path)


# View helper functions with enhanced error handling

def handle_file_upload(upload_function, file, **kwargs):
    """
    Wrapper for file uploads in views with user-friendly error handling.

    Args:
        upload_function: The upload function to use (e.g., upload_profile_picture)
        file: The uploaded file
        **kwargs: Additional arguments for the upload function

    Returns:
        Tuple[bool, str, str]: (success, file_path_or_error_message, file_url)

    Usage in views:
        success, result, url = handle_file_upload(upload_profile_picture, request.FILES['avatar'])
        if success:
            user.profile_picture = result  # result is file_path
            user.save()
        else:
            messages.error(request, result)  # result is error message
    """
    try:
        file_path, file_url = upload_function(file, **kwargs)
        return True, file_path, file_url
    except FileUploadError as e:
        logger.error(f"File upload error: {e.message}", exc_info=True)
        return False, e.user_message, None
    except Exception as e:
        logger.error(f"Unexpected file upload error: {str(e)}", exc_info=True)
        error_msg = (
            "ဖိုင်တင်ရာတွင် အမှားအယွင်း ရှိပါသည်။ ကျေးဇူးပြု၍ ထပ်မံကြိုးစားပါ။\n"
            "Error uploading file. Please try again."
        )
        return False, error_msg, None
