"""
Utility functions used across the application.
"""
import os
import uuid
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from decouple import config


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
        max_size_mb: Maximum allowed size in MB (defaults to MAX_UPLOAD_SIZE from settings)

    Raises:
        ValidationError: If file exceeds maximum size
    """
    if max_size_mb is None:
        max_size_mb = config('MAX_UPLOAD_SIZE', default=10485760, cast=int)  # 10MB default

    if file.size > max_size_mb:
        raise ValidationError(
            f'File size exceeds maximum allowed size of {max_size_mb / (1024*1024):.1f}MB'
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
