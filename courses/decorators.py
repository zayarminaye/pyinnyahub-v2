"""
Decorators for instructor portal permissions.
"""
from functools import wraps
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from .models import Course, Section, Lesson


def instructor_required(view_func):
    """
    Decorator that checks if user is an instructor.
    Redirects non-instructors to dashboard with error message.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'ကျေးဇူးပြု၍ အကောင့်ဝင်ပါ။')
            return redirect('login')

        if not request.user.is_instructor:
            messages.error(request, 'ဤစာမျက်နှာကို Instructor များသာ ဝင်ရောက်နိုင်ပါသည်။')
            return redirect('dashboard')

        return view_func(request, *args, **kwargs)
    return wrapper


def owns_course(view_func):
    """
    Decorator that checks if the instructor owns the course.
    Expects course_id in URL kwargs.
    """
    @wraps(view_func)
    def wrapper(request, course_id, *args, **kwargs):
        course = get_object_or_404(Course, id=course_id)

        # Admin and superuser can access all courses
        if request.user.is_superuser or request.user.role == 'admin':
            return view_func(request, course_id, *args, **kwargs)

        # Check ownership
        if course.instructor != request.user:
            messages.error(request, 'သင့်တွင် ဤသင်ခန်းစာကို ဝင်ရောက်ပြင်ဆင်ခွင့် မရှိပါ။')
            return redirect('instructor_courses')

        return view_func(request, course_id, *args, **kwargs)
    return wrapper


def owns_section(view_func):
    """
    Decorator that checks if the instructor owns the section's course.
    Expects section_id in URL kwargs.
    """
    @wraps(view_func)
    def wrapper(request, section_id, *args, **kwargs):
        section = get_object_or_404(Section, id=section_id)

        # Admin and superuser can access all
        if request.user.is_superuser or request.user.role == 'admin':
            return view_func(request, section_id, *args, **kwargs)

        # Check ownership through course
        if section.course.instructor != request.user:
            messages.error(request, 'သင့်တွင် ဤ Section ကို ဝင်ရောက်ပြင်ဆင်ခွင့် မရှိပါ။')
            return redirect('instructor_courses')

        return view_func(request, section_id, *args, **kwargs)
    return wrapper


def owns_lesson(view_func):
    """
    Decorator that checks if the instructor owns the lesson's course.
    Expects lesson_id in URL kwargs.
    """
    @wraps(view_func)
    def wrapper(request, lesson_id, *args, **kwargs):
        lesson = get_object_or_404(Lesson, id=lesson_id)

        # Admin and superuser can access all
        if request.user.is_superuser or request.user.role == 'admin':
            return view_func(request, lesson_id, *args, **kwargs)

        # Check ownership through section -> course
        if lesson.section.course.instructor != request.user:
            messages.error(request, 'သင့်တွင် ဤ Lesson ကို ဝင်ရောက်ပြင်ဆင်ခွင့် မရှိပါ။')
            return redirect('instructor_courses')

        return view_func(request, lesson_id, *args, **kwargs)
    return wrapper


class InstructorRequiredMixin(UserPassesTestMixin):
    """
    Mixin for class-based views that checks if user is an instructor.
    """
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_instructor

    def handle_no_permission(self):
        messages.error(self.request, 'ဤစာမျက်နှာကို Instructor များသာ ဝင်ရောက်နိုင်ပါသည်။')
        return redirect('dashboard')


class CourseOwnerMixin(UserPassesTestMixin):
    """
    Mixin for class-based views that checks course ownership.
    Expects self.get_course() to return the course object.
    """
    def test_func(self):
        if not (self.request.user.is_authenticated and self.request.user.is_instructor):
            return False

        # Admin and superuser bypass
        if self.request.user.is_superuser or self.request.user.role == 'admin':
            return True

        course = self.get_course()
        return course.instructor == self.request.user

    def handle_no_permission(self):
        messages.error(self.request, 'သင့်တွင် ဤသင်ခန်းစာကို ဝင်ရောက်ပြင်ဆင်ခွင့် မရှိပါ။')
        return redirect('instructor_courses')

    def get_course(self):
        """Override this to return the course object."""
        raise NotImplementedError("Subclasses must implement get_course()")
