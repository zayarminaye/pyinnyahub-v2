"""
Custom template tags and filters for courses app.
"""
from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key."""
    if dictionary and key:
        return dictionary.get(key)
    return None


@register.filter
def attr(obj, attribute):
    """Get attribute from object."""
    if obj and attribute:
        return getattr(obj, attribute, None)
    return None
