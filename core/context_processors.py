"""
Context processors to make settings available in all templates.
"""
from .models import SystemSettings


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
