"""
URL configuration for Pyinnya Hub LMS.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .health import health_check

urlpatterns = [
    # Health check for deployment platforms
    path('health/', health_check, name='health_check'),

    # Django Admin
    path('admin/', admin.site.urls),

    # Main App URLs
    path('', include('users.urls')),
    path('courses/', include('courses.urls')),
    path('payments/', include('payments.urls')),
    path('subscriptions/', include('subscriptions.urls')),
    path('payouts/', include('payouts.urls')),
    path('notifications/', include('notifications.urls')),
]

# Serve media files (user uploads)
# In production, you should use cloud storage (S3, CloudFlare R2, etc.)
# For now, serving locally for simplicity
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve static files in development (production uses WhiteNoise)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
