"""
URLs for Subscriptions app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('my/', views.my_courses_view, name='my_courses'),
    path('enroll/<slug:course_slug>/', views.enroll_course_view, name='enroll_course'),
    path('<int:subscription_id>/', views.subscription_detail_view, name='subscription_detail'),
]
