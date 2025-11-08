"""
Helper functions for using SystemMessage model in views.
Provides convenient access to editable system messages.
"""
from django.contrib import messages
from .models import SystemMessage


def show_message(request, key, message_type=None, lang='both', **context):
    """
    Show a system message to the user using Django messages framework.

    Args:
        request: Django request object
        key: Message key from SystemMessage
        message_type: Optional override for message type (success, error, warning, info)
        lang: 'burmese', 'english', or 'both'
        **context: Variables to substitute in the message

    Example:
        show_message(request, 'course_created_success', course_title="Python 101")
    """
    msg = SystemMessage.get(key, lang=lang, **context)

    # Get message type from SystemMessage if not provided
    if not message_type:
        try:
            msg_obj = SystemMessage.objects.get(key=key, is_active=True)
            message_type = msg_obj.message_type
        except SystemMessage.DoesNotExist:
            message_type = 'info'

    # Map to Django messages framework
    message_func = {
        'success': messages.success,
        'error': messages.error,
        'warning': messages.warning,
        'info': messages.info,
    }.get(message_type, messages.info)

    message_func(request, msg)


def get_message(key, lang='both', **context):
    """
    Get a system message without showing it (useful for custom rendering).

    Args:
        key: Message key from SystemMessage
        lang: 'burmese', 'english', or 'both'
        **context: Variables to substitute in the message

    Returns:
        str: Formatted message

    Example:
        error_msg = get_message('file_too_large', max_size=5)
    """
    return SystemMessage.get(key, lang=lang, **context)


def get_message_burmese(key, **context):
    """Get Burmese message only."""
    return SystemMessage.get(key, lang='burmese', **context)


def get_message_english(key, **context):
    """Get English message only."""
    return SystemMessage.get(key, lang='english', **context)


def get_file_upload_error(error_type='generic', **context):
    """
    Get file upload error message.

    Args:
        error_type: Type of error (generic, too_large, invalid_type, etc.)
        **context: Variables like max_size, allowed_types, etc.

    Returns:
        str: Bilingual error message
    """
    key = f'file_upload_{error_type}'
    return get_message(key, **context)
