"""
Utility functions used across the application.
"""
import os
import uuid
import mimetypes
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from decouple import config
from PIL import Image
from io import BytesIO
import sys


def generate_unique_filename(instance, filename):
    """
    Generate a unique filename for uploaded files.
    Format: uploads/{model_name}/{year}/{month}/{uuid}_{original_filename}
    """
    ext = filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    model_name = instance.__class__.__name__.lower()
    date_path = timezone.now().strftime('%Y/%m')

    return os.path.join('uploads', model_name, date_path, unique_filename)


def validate_file_size(file, max_size_mb=None):
    """
    Validate uploaded file size.

    Args:
        file: The uploaded file object
        max_size_mb: Maximum allowed size in MB

    Raises:
        ValidationError: If file exceeds maximum size
    """
    if max_size_mb is None:
        max_size_mb = 10  # 10MB default

    max_size_bytes = max_size_mb * 1024 * 1024

    if file.size > max_size_bytes:
        raise ValidationError(
            f'File size exceeds maximum allowed size of {max_size_mb}MB. Your file is {file.size / (1024*1024):.1f}MB.'
        )


def validate_file_type(file, allowed_types):
    """
    Validate uploaded file type.

    Args:
        file: The uploaded file object
        allowed_types: List of allowed MIME types

    Raises:
        ValidationError: If file type is not allowed
    """
    if file.content_type not in allowed_types:
        raise ValidationError(
            f'File type {file.content_type} is not allowed. '
            f'Allowed types: {", ".join(allowed_types)}'
        )


def get_subscription_expiry_date(access_type):
    """
    Calculate subscription expiry date based on access type.

    Args:
        access_type: One of 'monthly', 'yearly', 'lifetime'

    Returns:
        datetime or None: Expiry date or None for lifetime
    """
    if access_type == 'lifetime':
        return None

    days_map = {
        'monthly': config('MONTHLY_DAYS', default=30, cast=int),
        'yearly': config('YEARLY_DAYS', default=365, cast=int),
    }

    days = days_map.get(access_type)
    if days:
        return timezone.now() + timedelta(days=days)

    return None


def is_subscription_expired(expiry_date):
    """
    Check if a subscription has expired.

    Args:
        expiry_date: The subscription expiry date

    Returns:
        bool: True if expired, False otherwise
    """
    if expiry_date is None:  # Lifetime access
        return False

    return timezone.now() > expiry_date


def get_expiry_reminder_date(expiry_date):
    """
    Get the date when reminder email should be sent.

    Args:
        expiry_date: The subscription expiry date

    Returns:
        datetime or None: Reminder date or None for lifetime
    """
    if expiry_date is None:  # Lifetime access
        return None

    reminder_days = config('EXPIRY_REMINDER_DAYS', default=3, cast=int)
    return expiry_date - timedelta(days=reminder_days)


class FileValidator:
    """
    Reusable file validator class.
    """
    def __init__(self, allowed_types=None, max_size_mb=None):
        self.allowed_types = allowed_types
        self.max_size_mb = max_size_mb

    def __call__(self, file):
        """Validate the file."""
        if self.max_size_mb:
            validate_file_size(file, self.max_size_mb)

        if self.allowed_types:
            validate_file_type(file, self.allowed_types)


# ============================================================================
# IMAGE PROCESSING AND SECURITY
# ============================================================================

def sanitize_filename(filename):
    """
    Sanitize filename to prevent directory traversal and other attacks.

    Args:
        filename: Original filename

    Returns:
        str: Sanitized filename
    """
    # Get just the filename without path
    filename = os.path.basename(filename)

    # Remove any null bytes
    filename = filename.replace('\x00', '')

    # Replace dangerous characters
    dangerous_chars = ['..', '/', '\\', '<', '>', ':', '"', '|', '?', '*']
    for char in dangerous_chars:
        filename = filename.replace(char, '_')

    # Limit length
    name, ext = os.path.splitext(filename)
    if len(name) > 100:
        name = name[:100]

    return f"{name}{ext}".lower()


def validate_image_content(file):
    """
    Validate that the file is actually an image and not malicious.

    Args:
        file: Uploaded file object

    Raises:
        ValidationError: If file is not a valid image
    """
    try:
        # Try to open and verify the image
        img = Image.open(file)
        img.verify()

        # Reset file pointer after verify
        file.seek(0)

        # Check if format is allowed
        allowed_formats = ['JPEG', 'PNG', 'GIF', 'WEBP']
        if img.format not in allowed_formats:
            raise ValidationError(f'Image format {img.format} is not allowed. Use JPEG, PNG, GIF, or WEBP.')

        # Check image dimensions (max 8000x8000)
        max_dimension = 8000
        if img.width > max_dimension or img.height > max_dimension:
            raise ValidationError(f'Image dimensions too large. Maximum {max_dimension}x{max_dimension} pixels.')

    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f'Invalid image file: {str(e)}')


def process_uploaded_image(image_file, max_width=None, max_height=None, quality=85, format='JPEG'):
    """
    Process and optimize uploaded image.
    - Resize to max dimensions
    - Remove EXIF data (security)
    - Optimize file size
    - Convert to specified format

    Args:
        image_file: Uploaded image file
        max_width: Maximum width in pixels
        max_height: Maximum height in pixels
        quality: JPEG quality (1-100)
        format: Output format (JPEG, PNG, WEBP)

    Returns:
        InMemoryUploadedFile: Processed image file
    """
    try:
        # Open the image
        img = Image.open(image_file)

        # Convert RGBA to RGB if saving as JPEG
        if format == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
            # Create a white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background

        # Resize if needed
        if max_width or max_height:
            # Calculate new dimensions maintaining aspect ratio
            ratio = img.width / img.height

            if max_width and max_height:
                # Fit within both constraints
                if img.width > max_width or img.height > max_height:
                    if ratio > max_width / max_height:
                        new_width = max_width
                        new_height = int(max_width / ratio)
                    else:
                        new_height = max_height
                        new_width = int(max_height * ratio)
                else:
                    new_width, new_height = img.width, img.height
            elif max_width:
                new_width = min(max_width, img.width)
                new_height = int(new_width / ratio)
            else:
                new_height = min(max_height, img.height)
                new_width = int(new_height * ratio)

            if new_width != img.width or new_height != img.height:
                img = img.resize((new_width, new_height), Image.LANCZOS)

        # Save to BytesIO
        output = BytesIO()

        # Remove EXIF data by not passing it
        if format == 'JPEG':
            img.save(output, format='JPEG', quality=quality, optimize=True)
            content_type = 'image/jpeg'
            extension = 'jpg'
        elif format == 'PNG':
            img.save(output, format='PNG', optimize=True)
            content_type = 'image/png'
            extension = 'png'
        elif format == 'WEBP':
            img.save(output, format='WEBP', quality=quality)
            content_type = 'image/webp'
            extension = 'webp'
        else:
            raise ValueError(f'Unsupported format: {format}')

        output.seek(0)

        # Get original filename and change extension
        original_name = os.path.splitext(image_file.name)[0]
        new_filename = f"{sanitize_filename(original_name)}.{extension}"

        # Create InMemoryUploadedFile
        return InMemoryUploadedFile(
            output,
            'ImageField',
            new_filename,
            content_type,
            sys.getsizeof(output),
            None
        )

    except Exception as e:
        raise ValidationError(f'Error processing image: {str(e)}')


def validate_video_file(file, max_size_mb=500):
    """
    Validate video file.

    Args:
        file: Uploaded video file
        max_size_mb: Maximum size in MB (default 500MB for videos)

    Raises:
        ValidationError: If validation fails
    """
    # Validate size
    validate_file_size(file, max_size_mb)

    # Validate MIME type
    allowed_video_types = [
        'video/mp4',
        'video/webm',
        'video/quicktime',  # .mov
        'video/x-msvideo',  # .avi
    ]

    # Check file extension
    ext = os.path.splitext(file.name)[1].lower()
    allowed_extensions = ['.mp4', '.webm', '.mov']

    if ext not in allowed_extensions:
        raise ValidationError(
            f'Video file extension {ext} not allowed. Use: {", ".join(allowed_extensions)}'
        )

    # Guess MIME type from filename
    guessed_type, _ = mimetypes.guess_type(file.name)
    if guessed_type and guessed_type not in allowed_video_types:
        raise ValidationError(f'Video file type not allowed.')


def validate_document_file(file, max_size_mb=20):
    """
    Validate document file (PDF, DOC, etc.).

    Args:
        file: Uploaded document file
        max_size_mb: Maximum size in MB (default 20MB)

    Raises:
        ValidationError: If validation fails
    """
    # Validate size
    validate_file_size(file, max_size_mb)

    # Check file extension
    ext = os.path.splitext(file.name)[1].lower()
    allowed_extensions = ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.txt', '.zip', '.rar']

    if ext not in allowed_extensions:
        raise ValidationError(
            f'Document file extension {ext} not allowed. Use: {", ".join(allowed_extensions)}'
        )

    # Additional PDF validation
    if ext == '.pdf':
        # Read first few bytes to check PDF signature
        file.seek(0)
        header = file.read(5)
        file.seek(0)

        if header != b'%PDF-':
            raise ValidationError('Invalid PDF file.')


# ============================================================================
# SPECIFIC VALIDATORS FOR DIFFERENT FILE TYPES
# ============================================================================

def validate_profile_picture(file):
    """Validate profile picture uploads."""
    validate_file_size(file, max_size_mb=5)  # 5MB max for profile pictures
    validate_image_content(file)


def validate_course_thumbnail(file):
    """Validate course thumbnail uploads."""
    validate_file_size(file, max_size_mb=5)  # 5MB max
    validate_image_content(file)

    # Check minimum dimensions
    img = Image.open(file)
    file.seek(0)

    min_width, min_height = 800, 450  # 16:9 aspect ratio minimum
    if img.width < min_width or img.height < min_height:
        raise ValidationError(
            f'Course thumbnail must be at least {min_width}x{min_height} pixels. '
            f'Your image is {img.width}x{img.height}.'
        )


def validate_payment_receipt(file):
    """Validate payment receipt uploads."""
    validate_file_size(file, max_size_mb=10)  # 10MB max

    ext = os.path.splitext(file.name)[1].lower()

    if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
        validate_image_content(file)
    elif ext == '.pdf':
        validate_document_file(file, max_size_mb=10)
    else:
        raise ValidationError('Payment receipt must be an image (JPG, PNG) or PDF.')


def validate_lesson_video(file):
    """Validate lesson video uploads."""
    validate_video_file(file, max_size_mb=500)  # 500MB max for lesson videos


def validate_lesson_attachment(file):
    """Validate lesson attachment uploads."""
    validate_document_file(file, max_size_mb=50)  # 50MB max for attachments


def validate_instructor_resume(file):
    """Validate instructor resume uploads."""
    validate_document_file(file, max_size_mb=5)  # 5MB max


def validate_instructor_certificate(file):
    """Validate instructor certificate uploads - PDF only for combined documents."""
    ext = os.path.splitext(file.name)[1].lower()

    if ext != '.pdf':
        raise ValidationError('ကျေးဇူးပြု၍ PDF ဖိုင်သာ တင်ပါ။ (Please upload PDF file only)')

    # Validate PDF with larger size limit for combined documents
    validate_document_file(file, max_size_mb=10)  # 10MB for combined certificates


def format_currency(amount, currency='MMK'):
    """
    Format amount as currency.

    Args:
        amount: The amount to format
        currency: Currency code (default: MMK for Myanmar Kyat)

    Returns:
        str: Formatted currency string
    """
    return f"{amount:,.0f} {currency}"


def get_client_ip(request):
    """
    Get the client's IP address from the request.

    Args:
        request: Django request object

    Returns:
        str: Client IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
