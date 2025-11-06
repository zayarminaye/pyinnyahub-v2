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
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()

        # Preserve form data for re-rendering on error
        form_data = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
        }

        # Validation
        errors = []

        # Check required fields
        if not all([email, password, password2, first_name, last_name]):
            errors.append("ကျေးဇူးပြု၍ အချက်အလက်အားလုံး ဖြည့်ပေးပါ။")

        # Validate email format
        if email and '@' not in email:
            errors.append("အီးမေးလ် မှန်ကန်မှု မရှိပါ။")

        # Check email already exists
        if email and User.objects.filter(email=email).exists():
            errors.append("ဤအီးမေးလ်ကို အသုံးပြုပြီးဖြစ်ပါသည်။")

        # Validate password length
        if password and len(password) < 8:
            errors.append("လျှို့ဝှက်နံပါတ် အနည်းဆုံး ၈ လုံး ရှိရမည်။")

        # Check passwords match
        if password and password2 and password != password2:
            errors.append("လျှို့ဝှက်နံပါတ် မတူညီပါ။")

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'auth/register.html', {'form_data': form_data})

        # Create user
        try:
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            # Send welcome email
            from notifications.services import NotificationService
            NotificationService.send_registration_confirmation(user)

            messages.success(request, "စာရင်းသွင်းမှု အောင်မြင်ပါသည်။ ကျေးဇူးပြု၍ အကောင့်ဝင်ပါ။")
            return redirect('login')
        except Exception as e:
            messages.error(request, f"စာရင်းသွင်းရာတွင် အမှားရှိပါသည်: {str(e)}")
            return render(request, 'auth/register.html', {'form_data': form_data})

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


# ============================================================================
# ROLE-SPECIFIC DASHBOARDS
# ============================================================================

@login_required
def student_dashboard_view(request):
    """Student dashboard - shows enrolled courses."""
    from subscriptions.models import Subscription

    active_subscriptions = Subscription.objects.filter(
        user=request.user,
        is_active=True
    ).select_related('course', 'course__instructor')[:6]

    context = {
        'active_subscriptions': active_subscriptions,
    }
    return render(request, 'dashboards/student.html', context)


@login_required
def instructor_dashboard_view(request):
    """Instructor dashboard - shows instructor's courses and stats."""
    if not request.user.is_instructor:
        messages.error(request, "Access denied. Instructors only.")
        return redirect('dashboard')

    from courses.models import Course

    courses = Course.objects.filter(instructor=request.user).order_by('-created_at')
    draft_courses = courses.filter(status='draft')
    pending_courses = courses.filter(status='pending')
    published_courses = courses.filter(status='approved', is_published=True)

    context = {
        'courses': courses[:10],
        'draft_count': draft_courses.count(),
        'pending_count': pending_courses.count(),
        'published_count': published_courses.count(),
    }
    return render(request, 'dashboards/instructor.html', context)


@login_required
def admin_dashboard_view(request):
    """Admin dashboard - shows pending items for approval."""
    if not request.user.is_admin_user:
        messages.error(request, "Access denied. Admins only.")
        return redirect('dashboard')

    from courses.models import Course
    from payments.models import Payment

    pending_payments = Payment.objects.filter(status='pending').select_related('user', 'course')
    pending_courses = Course.objects.filter(status='pending').select_related('instructor')
    pending_applications = InstructorApplication.objects.filter(status='pending').select_related('user')

    context = {
        'pending_payments_count': pending_payments.count(),
        'pending_courses_count': pending_courses.count(),
        'pending_applications_count': pending_applications.count(),
        'pending_payments': pending_payments[:10],
        'pending_courses': pending_courses[:10],
        'pending_applications': pending_applications[:10],
    }
    return render(request, 'dashboards/admin.html', context)


# ============================================================================
# ADMIN APPROVAL VIEWS
# ============================================================================

@login_required
def admin_approve_payment_view(request, payment_id):
    """Admin approves a payment."""
    if not request.user.is_admin_user:
        messages.error(request, "Access denied.")
        return redirect('dashboard')

    from payments.models import Payment
    from django.shortcuts import get_object_or_404

    payment = get_object_or_404(Payment, id=payment_id)

    if request.method == 'POST':
        try:
            payment.approve(request.user)
            messages.success(request, f"ငွေပေးချေမှု အတည်ပြုပြီးပါပြီ။ {payment.student.get_full_name()} သည် {payment.course.title} ကို စတင်နိုင်ပါပြီ။")
        except Exception as e:
            messages.error(request, f"အမှား: {str(e)}")

        return redirect('admin_dashboard')

    context = {'payment': payment}
    return render(request, 'admin/approve_payment.html', context)


@login_required
def admin_reject_payment_view(request, payment_id):
    """Admin rejects a payment."""
    if not request.user.is_admin_user:
        messages.error(request, "Access denied.")
        return redirect('dashboard')

    from payments.models import Payment
    from django.shortcuts import get_object_or_404

    payment = get_object_or_404(Payment, id=payment_id)

    if request.method == 'POST':
        reason = request.POST.get('reason', 'Invalid payment details')
        try:
            payment.reject(request.user, reason)
            messages.success(request, "ငွေပေးချေမှု ငြင်းပယ်ပြီးပါပြီ။")
        except Exception as e:
            messages.error(request, f"အမှား: {str(e)}")

        return redirect('admin_dashboard')

    context = {'payment': payment}
    return render(request, 'admin/reject_payment.html', context)


@login_required
def admin_approve_course_view(request, course_id):
    """Admin approves a course."""
    if not request.user.is_admin_user:
        messages.error(request, "Access denied.")
        return redirect('dashboard')

    from courses.models import Course
    from django.shortcuts import get_object_or_404

    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        try:
            course.approve(request.user)
            messages.success(request, f"သင်ခန်းစာ '{course.title}' ကို အတည်ပြုပြီးပါပြီ။")
        except Exception as e:
            messages.error(request, f"အမှား: {str(e)}")

        return redirect('admin_dashboard')

    context = {'course': course}
    return render(request, 'admin/approve_course.html', context)


@login_required
def admin_reject_course_view(request, course_id):
    """Admin rejects a course."""
    if not request.user.is_admin_user:
        messages.error(request, "Access denied.")
        return redirect('dashboard')

    from courses.models import Course
    from django.shortcuts import get_object_or_404

    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        reason = request.POST.get('reason', 'Does not meet quality standards')
        try:
            course.reject(request.user, reason)
            messages.success(request, "သင်ခန်းစာ ငြင်းပယ်ပြီးပါပြီ။")
        except Exception as e:
            messages.error(request, f"အမှား: {str(e)}")

        return redirect('admin_dashboard')

    context = {'course': course}
    return render(request, 'admin/reject_course.html', context)


@login_required
def admin_approve_instructor_view(request, application_id):
    """Admin approves instructor application."""
    if not request.user.is_admin_user:
        messages.error(request, "Access denied.")
        return redirect('dashboard')

    from django.shortcuts import get_object_or_404

    application = get_object_or_404(InstructorApplication, id=application_id)

    if request.method == 'POST':
        try:
            application.approve(request.user)
            messages.success(request, f"{application.user.get_full_name()} ကို ဆရာ/ဆရာမအဖြစ် အတည်ပြုပြီးပါပြီ။")
        except Exception as e:
            messages.error(request, f"အမှား: {str(e)}")

        return redirect('admin_dashboard')

    context = {'application': application}
    return render(request, 'admin/approve_instructor.html', context)


@login_required
def admin_reject_instructor_view(request, application_id):
    """Admin rejects instructor application."""
    if not request.user.is_admin_user:
        messages.error(request, "Access denied.")
        return redirect('dashboard')

    from django.shortcuts import get_object_or_404

    application = get_object_or_404(InstructorApplication, id=application_id)

    if request.method == 'POST':
        reason = request.POST.get('reason', 'Application does not meet requirements')
        try:
            application.reject(request.user, reason)
            messages.success(request, "ဆရာ/ဆရာမ လျှောက်ထားမှု ငြင်းပယ်ပြီးပါပြီ။")
        except Exception as e:
            messages.error(request, f"အမှား: {str(e)}")

        return redirect('admin_dashboard')

    context = {'application': application}
    return render(request, 'admin/reject_instructor.html', context)


@login_required
def apply_instructor_view(request):
    """Student applies to become an instructor."""
    # Check if user already has an application
    existing_application = InstructorApplication.objects.filter(
        user=request.user,
        status__in=['pending', 'approved']
    ).first()

    if existing_application:
        if existing_application.status == 'approved':
            messages.info(request, "သင်သည် ဆရာ/ဆရာမအဖြစ် အတည်ပြုပြီးဖြစ်ပါသည်။")
            return redirect('dashboard')
        else:
            messages.info(request, "သင့်လျှောက်ထားမှုကို စိစစ်နေဆဲဖြစ်ပါသည်။")
            return redirect('dashboard')

    if request.method == 'POST':
        # Get form data matching actual model fields
        expertise = request.POST.get('expertise', '').strip()
        experience = request.POST.get('experience', '').strip()
        education = request.POST.get('education', '').strip()
        motivation = request.POST.get('motivation', '').strip()
        resume = request.FILES.get('resume')
        certificates = request.FILES.get('certificates')

        # Preserve form data
        form_data = {
            'expertise': expertise,
            'experience': experience,
            'education': education,
            'motivation': motivation,
        }

        # Validation
        errors = []
        if not all([expertise, experience, motivation]):
            errors.append("ကျေးဇူးပြု၍ လိုအပ်သော အချက်အလက်များကို ဖြည့်ပေးပါ။")

        if experience and len(experience) < 50:
            errors.append("အတွေ့အကြုံဖော်ပြချက် အနည်းဆုံး ၅၀ စာလုံး ရှိရပါမည်။")

        if motivation and len(motivation) < 50:
            errors.append("လျှောက်ထားရခြင်း အကြောင်းပြချက် အနည်းဆုံး ၅၀ စာလုံး ရှိရပါမည်။")

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'users/apply_instructor.html', {'form_data': form_data})

        # Create application
        try:
            application = InstructorApplication.objects.create(
                user=request.user,
                expertise=expertise,
                experience=experience,
                education=education if education else '',
                motivation=motivation,
            )

            # Save optional file uploads
            if resume:
                application.resume = resume
            if certificates:
                application.certificates = certificates

            if resume or certificates:
                application.save()

            messages.success(request, "လျှောက်ထားမှု အောင်မြင်ပါသည်။ Admin မှ စိစစ်ပြီး အကြောင်းကြားပါမည်။")
            return redirect('dashboard')
        except Exception as e:
            # User-friendly error message
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Instructor application error: {e}")
            messages.error(request, "လျှောက်ထားမှု မအောင်မြင်ပါ။ ကျေးဇူးပြု၍ ထပ်မံကြိုးစားပါ။")
            return render(request, 'users/apply_instructor.html', {'form_data': form_data})

    return render(request, 'users/apply_instructor.html')
