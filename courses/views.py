"""
Views for Courses app.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils.text import slugify
from .models import Course, Category, Section, Lesson
from .decorators import instructor_required, owns_course
from .forms import (
    CourseBasicInfoForm, CourseDetailsForm, CourseMediaForm,
    CoursePricingForm, CourseEditForm
)


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


# ============================================================================
# COURSE CREATION WIZARD
# ============================================================================

@login_required
@instructor_required
def course_create_step1(request):
    """Step 1: Basic course information."""
    if request.method == 'POST':
        form = CourseBasicInfoForm(request.POST)
        if form.is_valid():
            # Generate unique slug
            base_slug = slugify(form.cleaned_data['title'])
            slug = base_slug
            counter = 1
            while Course.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            # Store data in session
            request.session['course_wizard'] = {
                'title': form.cleaned_data['title'],
                'slug': slug,
                'category_id': form.cleaned_data['category'].id,
                'short_description': form.cleaned_data['short_description'],
                'description': form.cleaned_data['description'],
            }
            messages.success(request, 'Step 1 ပြီးဆုံးပါပြီ။ Step 2 သို့ ဆက်လက်လုပ်ဆောင်ပါ။')
            return redirect('course_create_step2')
    else:
        # Pre-fill from session if exists
        initial_data = {}
        if 'course_wizard' in request.session:
            wizard_data = request.session['course_wizard']
            initial_data = {
                'title': wizard_data.get('title'),
                'short_description': wizard_data.get('short_description'),
                'description': wizard_data.get('description'),
            }
            if wizard_data.get('category_id'):
                try:
                    initial_data['category'] = Category.objects.get(id=wizard_data['category_id'])
                except Category.DoesNotExist:
                    pass
        form = CourseBasicInfoForm(initial=initial_data)

    return render(request, 'instructor/courses/create/step1.html', {'form': form})


@login_required
@instructor_required
def course_create_step2(request):
    """Step 2: Course details and learning outcomes."""
    # Check if step1 data exists
    if 'course_wizard' not in request.session:
        messages.error(request, 'ကျေးဇူးပြု၍ Step 1 မှ စတင်ပါ။')
        return redirect('course_create_step1')

    if request.method == 'POST':
        form = CourseDetailsForm(request.POST)
        if form.is_valid():
            # Update session with step2 data
            request.session['course_wizard'].update({
                'level': form.cleaned_data['level'],
                'language': form.cleaned_data['language'],
                'duration_hours': form.cleaned_data['duration_hours'],
                'what_you_will_learn': form.cleaned_data['what_you_will_learn'],
                'requirements': form.cleaned_data['requirements'],
            })
            request.session.modified = True
            messages.success(request, 'Step 2 ပြီးဆုံးပါပြီ။ Step 3 သို့ ဆက်လက်လုပ်ဆောင်ပါ။')
            return redirect('course_create_step3')
    else:
        # Pre-fill from session
        initial_data = {}
        wizard_data = request.session['course_wizard']
        if 'level' in wizard_data:
            initial_data = {
                'level': wizard_data.get('level'),
                'language': wizard_data.get('language'),
                'duration_hours': wizard_data.get('duration_hours'),
            }
            # Convert JSON arrays back to text
            if wizard_data.get('what_you_will_learn'):
                initial_data['what_you_will_learn'] = '\n'.join(
                    f"- {item}" for item in wizard_data['what_you_will_learn']
                )
            if wizard_data.get('requirements'):
                initial_data['requirements'] = '\n'.join(
                    f"- {item}" for item in wizard_data['requirements']
                )
        form = CourseDetailsForm(initial=initial_data)

    return render(request, 'instructor/courses/create/step2.html', {'form': form})


@login_required
@instructor_required
def course_create_step3(request):
    """Step 3: Media upload."""
    # Check if previous steps completed
    if 'course_wizard' not in request.session or 'level' not in request.session['course_wizard']:
        messages.error(request, 'ကျေးဇူးပြု၍ Step 1 နှင့် 2 ကို ဦးစွာ ပြီးမြောက်ပါ။')
        return redirect('course_create_step1')

    if request.method == 'POST':
        form = CourseMediaForm(request.POST, request.FILES)
        if form.is_valid():
            # Store files temporarily (will be attached to course object in step5)
            request.session['course_wizard'].update({
                'has_thumbnail': True if form.cleaned_data.get('thumbnail') else False,
                'has_promo_video': True if form.cleaned_data.get('promo_video') else False,
            })
            # Store files in session as temporary storage isn't ideal
            # We'll handle file uploads in the final step
            request.session['course_wizard_files'] = {
                'thumbnail': request.FILES.get('thumbnail'),
                'promo_video': request.FILES.get('promo_video'),
            }
            request.session.modified = True
            messages.success(request, 'Step 3 ပြီးဆုံးပါပြီ။ Step 4 သို့ ဆက်လက်လုပ်ဆောင်ပါ။')
            return redirect('course_create_step4')
    else:
        form = CourseMediaForm()

    return render(request, 'instructor/courses/create/step3.html', {'form': form})


@login_required
@instructor_required
def course_create_step4(request):
    """Step 4: Pricing and access."""
    # Check if previous steps completed
    if 'course_wizard' not in request.session or 'has_thumbnail' not in request.session['course_wizard']:
        messages.error(request, 'ကျေးဇူးပြု၍ အရင် Steps များကို ဦးစွာ ပြီးမြောက်ပါ။')
        return redirect('course_create_step1')

    if request.method == 'POST':
        form = CoursePricingForm(request.POST)
        if form.is_valid():
            # Update session with final pricing data
            request.session['course_wizard'].update({
                'price': str(form.cleaned_data['price']),  # Convert Decimal to string for session
                'access_type': form.cleaned_data['access_type'],
            })
            request.session.modified = True
            messages.success(request, 'Step 4 ပြီးဆုံးပါပြီ။ Review & Submit သို့ ဆက်လက်လုပ်ဆောင်ပါ။')
            return redirect('course_create_step5')
    else:
        # Pre-fill from session
        initial_data = {}
        wizard_data = request.session['course_wizard']
        if 'price' in wizard_data:
            initial_data = {
                'price': wizard_data.get('price'),
                'access_type': wizard_data.get('access_type'),
            }
        form = CoursePricingForm(initial=initial_data)

    return render(request, 'instructor/courses/create/step4.html', {'form': form})


@login_required
@instructor_required
def course_create_step5(request):
    """Step 5: Review and submit."""
    # Check if all previous steps completed
    if 'course_wizard' not in request.session or 'price' not in request.session['course_wizard']:
        messages.error(request, 'ကျေးဇူးပြု၍ အရင် Steps များကို ဦးစွာ ပြီးမြောက်ပါ။')
        return redirect('course_create_step1')

    wizard_data = request.session['course_wizard']

    if request.method == 'POST':
        # Determine status based on button clicked
        status = 'draft' if 'save_draft' in request.POST else 'pending'

        # Create course object
        try:
            course = Course(
                title=wizard_data['title'],
                slug=wizard_data['slug'],
                category_id=wizard_data['category_id'],
                short_description=wizard_data['short_description'],
                description=wizard_data['description'],
                level=wizard_data['level'],
                language=wizard_data['language'],
                duration_hours=wizard_data['duration_hours'],
                what_you_will_learn=wizard_data['what_you_will_learn'],
                requirements=wizard_data['requirements'],
                price=wizard_data['price'],
                access_type=wizard_data['access_type'],
                instructor=request.user,
                status=status,
            )

            # Handle file uploads if they exist
            if 'course_wizard_files' in request.session:
                files = request.session['course_wizard_files']
                if files.get('thumbnail'):
                    course.thumbnail = files['thumbnail']
                if files.get('promo_video'):
                    course.promo_video = files['promo_video']

            course.save()

            # Clear wizard session
            del request.session['course_wizard']
            if 'course_wizard_files' in request.session:
                del request.session['course_wizard_files']
            request.session.modified = True

            if status == 'draft':
                messages.success(request, f'သင်ခန်းစာ "{course.title}" ကို Draft အဖြစ် သိမ်းဆည်းပြီးပါပြီ။')
            else:
                messages.success(request, f'သင်ခန်းစာ "{course.title}" ကို Admin သုံးသပ်ရန် တင်သွင်းပြီးပါပြီ။')

            return redirect('instructor_courses')

        except Exception as e:
            messages.error(request, f'သင်ခန်းစာ ဖန်တီးရာတွင် အမှားအယွင်း ရှိပါသည်: {str(e)}')

    # Prepare data for review
    try:
        category = Category.objects.get(id=wizard_data['category_id'])
    except Category.DoesNotExist:
        category = None

    context = {
        'wizard_data': wizard_data,
        'category': category,
    }
    return render(request, 'instructor/courses/create/step5.html', context)


# ============================================================================
# COURSE MANAGEMENT (PLACEHOLDERS)
# ============================================================================

@login_required
@instructor_required
@owns_course
def course_edit_view(request, course_id):
    """Edit existing course."""
    # Placeholder - will implement next
    messages.info(request, 'Course edit feature coming soon!')
    return redirect('instructor_courses')


@login_required
@instructor_required
@owns_course
def course_delete_view(request, course_id):
    """Delete course."""
    # Placeholder - will implement next
    messages.info(request, 'Course delete feature coming soon!')
    return redirect('instructor_courses')


@login_required
@instructor_required
@owns_course
def course_curriculum_view(request, course_id):
    """Manage course curriculum."""
    # Placeholder - will implement next
    messages.info(request, 'Curriculum manager coming soon!')
    return redirect('instructor_courses')
