"""
URLs for Subscriptions app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('my/', views.my_subscriptions_view, name='my_subscriptions'),
    path('enroll/<slug:course_slug>/', views.enroll_course_view, name='enroll_course'),
    path('<int:subscription_id>/', views.subscription_detail_view, name='subscription_detail'),
]
