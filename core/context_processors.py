"""
Context processors to make settings and messages available in all templates.
"""
from .models import SystemSettings, SystemMessage


def system_settings(request):
    """Make system settings available in all templates."""
    try:
        settings = SystemSettings.get_settings()
    except Exception:
        # Fallback to defaults if settings don't exist yet
        settings = None

    return {
        'system_settings': settings,
    }


def system_messages(request):
    """Add commonly used system messages to template context."""
    # Get current language (defaulting to Burmese)
    lang = request.session.get('language', 'burmese')

    # Helper function to get message
    def get_msg(key):
        try:
            return SystemMessage.get(key, lang=lang, default='')
        except Exception:
            return ''

    return {
        # Button labels
        'msg_btn_start_learning': get_msg('btn_start_learning'),
        'msg_btn_continue_learning': get_msg('btn_continue_learning'),
        'msg_btn_mark_complete': get_msg('btn_mark_complete'),
        'msg_btn_completed': get_msg('btn_completed'),
        'msg_btn_course_details': get_msg('btn_course_details'),
        'msg_btn_review_course': get_msg('btn_review_course'),
        'msg_btn_continue_watching': get_msg('btn_continue_watching'),

        # Common labels
        'msg_label_progress': get_msg('label_progress'),
        'msg_label_lessons_completed': get_msg('label_lessons_completed'),
        'msg_label_my_courses': get_msg('label_my_courses'),
        'msg_label_active_courses': get_msg('label_active_courses'),
        'msg_label_in_progress': get_msg('label_in_progress'),
        'msg_label_completed': get_msg('label_completed'),

        # Empty states
        'msg_empty_no_courses': get_msg('empty_no_courses'),
        'msg_empty_no_courses_msg': get_msg('empty_no_courses_msg'),
        'msg_empty_no_lessons': get_msg('empty_no_lessons'),

        # Function to get any message by key
        'get_system_message': lambda key: get_msg(key),
    }
