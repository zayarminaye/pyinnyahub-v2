"""
Health check endpoint for deployment platforms.
"""
from django.http import JsonResponse


def health_check(request):
    """Simple health check endpoint that returns 200 OK."""
    return JsonResponse({'status': 'healthy', 'service': 'pyinnyahub-lms'})
