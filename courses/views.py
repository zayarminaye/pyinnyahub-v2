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

    context = {
        'course': course,
    }
    return render(request, 'courses/detail.html', context)
