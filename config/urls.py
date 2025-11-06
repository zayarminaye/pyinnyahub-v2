"""
URL configuration for Pyinnya Hub LMS.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
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

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
