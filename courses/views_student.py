"""
Student learning views for Pyinnya Hub LMS.
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Prefetch
from .models import Course, Section, Lesson, LessonProgress


@login_required
def course_learn_view(request, course_id, lesson_id=None):
    """
    Main student learning interface with sidebar and content area.
    """
    # Allow instructors to preview their own courses regardless of publish status
    if request.user.role == 'instructor':
        course = get_object_or_404(Course, id=course_id, instructor=request.user)
        is_preview = True
    else:
        course = get_object_or_404(Course, id=course_id, is_published=True)
        is_preview = False

    # Check if user is enrolled (skip for instructors previewing their own course)
    from subscriptions.models import Subscription
    subscription = None
    if not is_preview:
        subscription = Subscription.objects.filter(
            user=request.user,
            course=course,
            is_active=True
        ).first()

        if not subscription or subscription.is_expired():
            return render(request, 'courses/not_enrolled.html', {'course': course})

    # Get all sections with lessons
    sections = course.sections.prefetch_related('lessons').order_by('order')

    # Get all lesson progress for this user and course
    lesson_ids = []
    for section in sections:
        lesson_ids.extend([lesson.id for lesson in section.lessons.all()])

    progress_dict = {}
    if lesson_ids:
        progresses = LessonProgress.objects.filter(
            user=request.user,
            lesson_id__in=lesson_ids
        )
        progress_dict = {p.lesson_id: p for p in progresses}

    # Calculate course progress
    total_lessons = len(lesson_ids)
    completed_lessons = sum(1 for p in progress_dict.values() if p.is_completed)
    progress_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0

    # Determine which lesson to show
    current_lesson = None
    if lesson_id:
        # Show specific lesson
        current_lesson = get_object_or_404(Lesson, id=lesson_id, section__course=course)
    else:
        # Find last accessed lesson or first incomplete lesson
        last_progress = LessonProgress.objects.filter(
            user=request.user,
            lesson__section__course=course
        ).order_by('-last_viewed_at').first()

        if last_progress:
            current_lesson = last_progress.lesson
        else:
            # Get first lesson
            first_section = sections.first()
            if first_section:
                current_lesson = first_section.lessons.order_by('order').first()

    # Record view for current lesson
    if current_lesson:
        lesson_progress, created = LessonProgress.objects.get_or_create(
            user=request.user,
            lesson=current_lesson
        )
        lesson_progress.record_view()

    context = {
        'course': course,
        'sections': sections,
        'current_lesson': current_lesson,
        'progress_dict': progress_dict,
        'progress_percentage': round(progress_percentage, 1),
        'total_lessons': total_lessons,
        'completed_lessons': completed_lessons,
        'is_preview': is_preview,
    }

    return render(request, 'courses/learn.html', context)


@login_required
def lesson_get_content_ajax(request, lesson_id):
    """Get lesson content via AJAX for sidebar navigation."""
    lesson = get_object_or_404(Lesson, id=lesson_id)

    # Check enrollment
    from subscriptions.models import Subscription
    subscription = Subscription.objects.filter(
        user=request.user,
        course=lesson.section.course,
        is_active=True
    ).first()

    if not subscription or subscription.is_expired():
        return JsonResponse({'success': False, 'error': 'Not enrolled'}, status=403)

    # Get or create progress
    lesson_progress, created = LessonProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson
    )
    lesson_progress.record_view()

    # Prepare content based on type
    content_html = ''
    if lesson.content_type == 'video':
        if lesson.video_file:
            content_html = f'''
                <video controls class="w-100" style="max-height: 500px;" id="lessonVideo">
                    <source src="{lesson.video_file.url}" type="video/mp4">
                    Your browser does not support video playback.
                </video>
            '''
        elif lesson.video_url:
            # Convert YouTube URL to embed
            video_url = lesson.video_url
            if 'youtube.com/watch?v=' in video_url:
                video_id = video_url.split('watch?v=')[1].split('&')[0]
                video_url = f'https://www.youtube.com/embed/{video_id}'
            elif 'youtu.be/' in video_url:
                video_id = video_url.split('youtu.be/')[1].split('?')[0]
                video_url = f'https://www.youtube.com/embed/{video_id}'

            content_html = f'''
                <div class="ratio ratio-16x9">
                    <iframe src="{video_url}" allowfullscreen></iframe>
                </div>
            '''
    elif lesson.content_type in ['text', 'quiz', 'assignment']:
        content_html = f'<div class="lesson-text-content">{lesson.text_content or ""}</div>'

    return JsonResponse({
        'success': True,
        'lesson': {
            'id': lesson.id,
            'title': lesson.title,
            'description': lesson.description or '',
            'content_type': lesson.content_type,
            'content_html': content_html,
            'duration_minutes': lesson.duration_minutes or 0,
            'is_completed': lesson_progress.is_completed,
            'last_position_seconds': lesson_progress.last_position_seconds,
        }
    })


@login_required
@require_POST
def mark_lesson_complete_ajax(request, lesson_id):
    """Mark a lesson as complete."""
    lesson = get_object_or_404(Lesson, id=lesson_id)

    # Check enrollment
    from subscriptions.models import Subscription
    subscription = Subscription.objects.filter(
        user=request.user,
        course=lesson.section.course,
        is_active=True
    ).first()

    if not subscription or subscription.is_expired():
        return JsonResponse({'success': False, 'error': 'Not enrolled'}, status=403)

    # Get or create progress
    lesson_progress, created = LessonProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson
    )

    # Mark as complete
    if not lesson_progress.is_completed:
        lesson_progress.mark_complete()

    # Calculate updated course progress
    course = lesson.section.course
    all_lessons = Lesson.objects.filter(section__course=course)
    total = all_lessons.count()
    completed = LessonProgress.objects.filter(
        user=request.user,
        lesson__section__course=course,
        is_completed=True
    ).count()

    progress_percentage = (completed / total * 100) if total > 0 else 0

    return JsonResponse({
        'success': True,
        'is_completed': True,
        'completed_at': lesson_progress.completed_at.isoformat() if lesson_progress.completed_at else None,
        'progress_percentage': round(progress_percentage, 1),
        'completed_lessons': completed,
        'total_lessons': total,
    })


@login_required
@require_POST
def update_video_position_ajax(request, lesson_id):
    """Update video playback position for resume."""
    import json

    lesson = get_object_or_404(Lesson, id=lesson_id)

    try:
        data = json.loads(request.body)
        position_seconds = int(data.get('position_seconds', 0))

        # Get or create progress
        lesson_progress, created = LessonProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson
        )

        lesson_progress.update_position(position_seconds)

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
