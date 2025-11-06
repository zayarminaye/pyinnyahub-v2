"""
Views for Courses app.
"""
from django.shortcuts import render, get_object_or_404
from .models import Course, Category


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
