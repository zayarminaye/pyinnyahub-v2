"""
Views for Users app - API and Web views.
"""
from rest_framework import viewsets, status, generics, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings

from .models import InstructorApplication
from .serializers import (
    UserSerializer, UserRegistrationSerializer, LoginSerializer,
    InstructorApplicationSerializer, ChangePasswordSerializer
)
from core.permissions import IsStudent, IsInstructor, IsAdmin

User = get_user_model()


# ============================================================================
# API VIEWS
# ============================================================================

class RegisterAPIView(generics.CreateAPIView):
    """API endpoint for user registration."""
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserRegistrationSerializer


class LoginAPIView(APIView):
    """API endpoint for user login."""
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })


class LogoutAPIView(APIView):
    """API endpoint for user logout."""
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    """API endpoint for user profile."""
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class ChangePasswordAPIView(generics.UpdateAPIView):
    """API endpoint for changing password."""
    serializer_class = ChangePasswordSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password changed successfully."})


class InstructorApplicationViewSet(viewsets.ModelViewSet):
    """ViewSet for instructor applications."""
    serializer_class = InstructorApplicationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        if self.request.user.is_admin_user:
            return InstructorApplication.objects.all()
        return InstructorApplication.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Check if feature is enabled
        if not settings.ENABLE_INSTRUCTOR_APPLICATIONS:
            raise serializers.ValidationError("Instructor applications are currently disabled.")

        # Check if user already has pending/approved application
        if InstructorApplication.objects.filter(
            user=self.request.user,
            status__in=['pending', 'approved']
        ).exists():
            raise serializers.ValidationError("You already have a pending or approved application.")

        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def approve(self, request, pk=None):
        """Admin approves instructor application."""
        application = self.get_object()
        application.approve(request.user)
        return Response({"detail": "Application approved successfully."})

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def reject(self, request, pk=None):
        """Admin rejects instructor application."""
        application = self.get_object()
        reason = request.data.get('reason', 'Not specified')
        application.reject(request.user, reason)
        return Response({"detail": "Application rejected."})


# ============================================================================
# WEB VIEWS (Django Templates)
# ============================================================================

def home_view(request):
    """Home page view."""
    from courses.models import Course, Category

    featured_courses = Course.objects.published().filter(is_featured=True)[:6]
    categories = Category.objects.filter(is_active=True)[:6]

    context = {
        'featured_courses': featured_courses,
        'categories': categories,
    }
    return render(request, 'home.html', context)


def register_view(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        # Validation
        if password != password2:
            messages.error(request, "Passwords don't match.")
            return render(request, 'auth/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, 'auth/register.html')

        # Create user
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # Send welcome email
        from notifications.services import NotificationService
        NotificationService.send_registration_confirmation(user)

        messages.success(request, "Registration successful! Please login.")
        return redirect('login')

    return render(request, 'auth/register.html')


def login_view(request):
    """User login view."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name()}!")

            # Redirect based on role
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, 'auth/login.html')


@login_required
def logout_view(request):
    """User logout view."""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')


@login_required
def dashboard_view(request):
    """Main dashboard - redirects to role-specific dashboard."""
    if request.user.is_admin_user:
        return redirect('admin_dashboard')
    elif request.user.is_instructor:
        return redirect('instructor_dashboard')
    else:
        return redirect('student_dashboard')


@login_required
def profile_view(request):
    """User profile view."""
    if request.method == 'POST':
        # Update profile
        request.user.first_name = request.POST.get('first_name', request.user.first_name)
        request.user.last_name = request.POST.get('last_name', request.user.last_name)
        request.user.phone_number = request.POST.get('phone_number', request.user.phone_number)
        request.user.bio = request.POST.get('bio', request.user.bio)

        if 'profile_picture' in request.FILES:
            request.user.profile_picture = request.FILES['profile_picture']

        request.user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('profile')

    return render(request, 'profile.html')
