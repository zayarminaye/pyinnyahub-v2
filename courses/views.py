"""
Views for Courses app.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Course, Category
from .decorators import instructor_required


def course_list_view(request):
    """Course listing page."""
    courses = Course.objects.published()
    categories = Category.objects.filter(is_active=True)

    # Filter by category
    category_slug = request.GET.get('category')
    if category_slug:
        courses = courses.filter(category__slug=category_slug)

    # Search
    query = request.GET.get('q')
    if query:
        courses = courses.filter(title__icontains=query)

    context = {
        'courses': courses,
        'categories': categories,
    }
    return render(request, 'courses/list.html', context)


def course_detail_view(request, slug):
    """Course detail page."""
    course = get_object_or_404(Course, slug=slug, is_published=True)

    # Increment view count
    course.increment_view_count()

    # Check if user is enrolled
    is_enrolled = False
    active_subscription = None
    if request.user.is_authenticated:
        from subscriptions.models import Subscription
        active_subscription = Subscription.objects.filter(
            user=request.user,
            course=course,
            is_active=True
        ).first()
        if active_subscription and not active_subscription.is_expired():
            is_enrolled = True

    context = {
        'course': course,
        'is_enrolled': is_enrolled,
        'active_subscription': active_subscription,
    }
    return render(request, 'courses/detail.html', context)


# ============================================================================
# INSTRUCTOR PORTAL VIEWS
# ============================================================================

@login_required
@instructor_required
def instructor_course_dashboard(request):
    """
    Instructor course management dashboard.
    Shows all instructor's courses with filtering and actions.
    """
    # Get all courses for this instructor
    courses = Course.objects.filter(instructor=request.user).order_by('-created_at')

    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        courses = courses.filter(status=status_filter)

    # Calculate stats
    all_courses = Course.objects.filter(instructor=request.user)
    draft_count = all_courses.filter(status='draft').count()
    pending_count = all_courses.filter(status='pending').count()
    approved_count = all_courses.filter(status='approved').count()
    rejected_count = all_courses.filter(status='rejected').count()

    # Get rejected courses for alert
    rejected_courses = all_courses.filter(status='rejected').order_by('-reviewed_at')[:5]

    # Pagination
    paginator = Paginator(courses, 10)
    page_number = request.GET.get('page')
    courses_page = paginator.get_page(page_number)

    context = {
        'courses': courses_page,
        'draft_count': draft_count,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'rejected_courses': rejected_courses,
        'status_filter': status_filter,
    }
    return render(request, 'instructor/courses/dashboard.html', context)
