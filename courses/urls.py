"""
URLs for Courses app.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Public course browsing
    path('', views.course_list_view, name='course_list'),
    path('<slug:slug>/', views.course_detail_view, name='course_detail'),

    # Instructor portal
    path('instructor/my-courses/', views.instructor_course_dashboard, name='instructor_courses'),
]
