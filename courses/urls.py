"""
URLs for Courses app.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Public course browsing
    path('', views.course_list_view, name='course_list'),
    path('<slug:slug>/', views.course_detail_view, name='course_detail'),

    # Instructor portal - Dashboard
    path('instructor/my-courses/', views.instructor_course_dashboard, name='instructor_courses'),

    # Instructor portal - Course Creation Wizard
    path('instructor/create/step1/', views.course_create_step1, name='course_create_step1'),
    path('instructor/create/step2/', views.course_create_step2, name='course_create_step2'),
    path('instructor/create/step3/', views.course_create_step3, name='course_create_step3'),
    path('instructor/create/step4/', views.course_create_step4, name='course_create_step4'),
    path('instructor/create/step5/', views.course_create_step5, name='course_create_step5'),

    # Instructor portal - Course Management
    path('instructor/<int:course_id>/edit/', views.course_edit_view, name='course_edit'),
    path('instructor/<int:course_id>/delete/', views.course_delete_view, name='course_delete'),
    path('instructor/<int:course_id>/curriculum/', views.course_curriculum_view, name='course_curriculum'),
]
