"""
URLs for Courses app.
"""
from django.urls import path
from . import views
from . import views_student

urlpatterns = [
    # Public course browsing
    path('', views.course_list_view, name='course_list'),
    path('<slug:slug>/', views.course_detail_view, name='course_detail'),

    # Student learning interface
    path('learn/<int:course_id>/', views_student.course_learn_view, name='course_learn'),
    path('learn/<int:course_id>/<int:lesson_id>/', views_student.course_learn_view, name='course_learn_lesson'),
    path('lessons/<int:lesson_id>/content/', views_student.lesson_get_content_ajax, name='lesson_content_ajax'),
    path('lessons/<int:lesson_id>/complete/', views_student.mark_lesson_complete_ajax, name='mark_lesson_complete'),
    path('lessons/<int:lesson_id>/position/', views_student.update_video_position_ajax, name='update_video_position'),

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
    path('instructor/<int:course_id>/preview/', views.course_preview, name='course_preview'),
    path('instructor/<int:course_id>/lessons/<int:lesson_id>/content/', views.lesson_content_edit, name='lesson_content_edit'),

    # Curriculum Management AJAX
    path('instructor/<int:course_id>/sections/create/', views.section_create_ajax, name='section_create_ajax'),
    path('instructor/<int:course_id>/sections/<int:section_id>/update/', views.section_update_ajax, name='section_update_ajax'),
    path('instructor/<int:course_id>/sections/<int:section_id>/delete/', views.section_delete_ajax, name='section_delete_ajax'),
    path('instructor/<int:course_id>/sections/reorder/', views.section_reorder_ajax, name='section_reorder_ajax'),
    path('instructor/<int:course_id>/sections/<int:section_id>/lessons/create/', views.lesson_create_ajax, name='lesson_create_ajax'),
    path('instructor/<int:course_id>/lessons/<int:lesson_id>/get/', views.lesson_get_ajax, name='lesson_get_ajax'),
    path('instructor/<int:course_id>/lessons/<int:lesson_id>/update/', views.lesson_update_ajax, name='lesson_update_ajax'),
    path('instructor/<int:course_id>/lessons/<int:lesson_id>/delete/', views.lesson_delete_ajax, name='lesson_delete_ajax'),
    path('instructor/<int:course_id>/sections/<int:section_id>/lessons/reorder/', views.lesson_reorder_ajax, name='lesson_reorder_ajax'),
]
