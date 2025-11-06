"""
Custom permission classes for role-based access control.
These are reusable across all API views.
"""
from rest_framework import permissions


class IsStudent(permissions.BasePermission):
    """
    Permission class to check if user is a student.
    """
    message = "Only students can perform this action."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'student'


class IsInstructor(permissions.BasePermission):
    """
    Permission class to check if user is an instructor.
    """
    message = "Only instructors can perform this action."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'instructor'


class IsAdmin(permissions.BasePermission):
    """
    Permission class to check if user is an admin.
    """
    message = "Only admins can perform this action."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.role == 'admin' or request.user.is_staff or request.user.is_superuser
        )


class IsStudentOrReadOnly(permissions.BasePermission):
    """
    Permission class to allow students to perform actions, others can only read.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.role == 'student'


class IsInstructorOrReadOnly(permissions.BasePermission):
    """
    Permission class to allow instructors to perform actions, others can only read.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.role == 'instructor'


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission class to allow owners to edit their own objects, or admins to edit any.
    """
    message = "You can only edit your own content."

    def has_object_permission(self, request, view, obj):
        # Admins can do anything
        if request.user.role == 'admin' or request.user.is_staff:
            return True

        # Check if object has 'user' or 'owner' attribute
        owner = getattr(obj, 'user', getattr(obj, 'owner', getattr(obj, 'instructor', None)))
        return owner == request.user


class IsInstructorOwnerOrAdmin(permissions.BasePermission):
    """
    Permission class specifically for instructors to manage their own courses.
    Admins can manage any course.
    """
    message = "You can only manage your own courses."

    def has_object_permission(self, request, view, obj):
        # Admins can do anything
        if request.user.role == 'admin' or request.user.is_staff:
            return True

        # Instructors can only manage their own courses
        if request.user.role == 'instructor':
            instructor = getattr(obj, 'instructor', None)
            return instructor == request.user

        return False


class IsEnrolledStudent(permissions.BasePermission):
    """
    Permission class to check if student is enrolled in a course.
    Used for accessing course content.
    """
    message = "You must be enrolled in this course to access its content."

    def has_object_permission(self, request, view, obj):
        # Admins and instructors (course owner) can always access
        if request.user.role == 'admin' or request.user.is_staff:
            return True

        # Course instructor can access
        if hasattr(obj, 'instructor') and obj.instructor == request.user:
            return True

        # Check if student is enrolled with active subscription
        if request.user.role == 'student':
            from subscriptions.models import Subscription
            # Check for course-specific or global subscription
            return Subscription.objects.filter(
                user=request.user,
                is_active=True
            ).filter(
                models.Q(course=obj) | models.Q(is_global=True)
            ).exists()

        return False


class CanApplyAsInstructor(permissions.BasePermission):
    """
    Permission class to check if user can apply as instructor.
    Only students who haven't applied or been approved can apply.
    """
    message = "You cannot apply as an instructor."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Only students can apply
        if request.user.role != 'student':
            return False

        # Check if they haven't already applied
        from users.models import InstructorApplication
        existing_application = InstructorApplication.objects.filter(
            user=request.user,
            status__in=['pending', 'approved']
        ).exists()

        return not existing_application
