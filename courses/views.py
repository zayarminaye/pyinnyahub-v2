"""
Views for Courses app.
"""
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils.text import slugify
from django.db import models
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Course, Category, Section, Lesson, LessonProgress
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
            from core.storage_service import handle_file_upload, upload_course_thumbnail, upload_course_promo_video

            wizard_file_data = {}

            # Upload thumbnail using storage service
            if form.cleaned_data.get('thumbnail'):
                thumbnail = form.cleaned_data['thumbnail']

                success, result, url = handle_file_upload(
                    upload_course_thumbnail,
                    thumbnail
                )

                if success:
                    wizard_file_data['thumbnail_path'] = result
                    wizard_file_data['thumbnail_url'] = url
                    wizard_file_data['has_thumbnail'] = True
                else:
                    messages.error(request, result)
                    return render(request, 'instructor/courses/create/step3.html', {'form': form})

            # Upload promo video using storage service
            if form.cleaned_data.get('promo_video'):
                promo_video = form.cleaned_data['promo_video']

                success, result, url = handle_file_upload(
                    upload_course_promo_video,
                    promo_video
                )

                if success:
                    wizard_file_data['promo_video_path'] = result
                    wizard_file_data['promo_video_url'] = url
                    wizard_file_data['has_promo_video'] = True
                else:
                    messages.error(request, result)
                    return render(request, 'instructor/courses/create/step3.html', {'form': form})

            # Store file data in session
            request.session['course_wizard'].update(wizard_file_data)
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

            # Files were already uploaded in step3 via storage service
            # Assign paths before saving
            if wizard_data.get('thumbnail_path'):
                course.thumbnail = wizard_data['thumbnail_path']

            if wizard_data.get('promo_video_path'):
                course.promo_video = wizard_data['promo_video_path']

            course.save()

            # Clear wizard session
            del request.session['course_wizard']
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
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        form = CourseEditForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            # Check if resubmitting rejected course
            resubmit = request.POST.get('resubmit_for_review') == 'true'

            # Save the course
            course = form.save(commit=False)

            # If resubmitting a rejected course, change status to pending
            if resubmit and course.status == 'rejected':
                course.status = 'pending'
                course.rejection_reason = None
                messages.success(request, f'သင်ခန်းစာ "{course.title}" ကို ပြုပြင်ပြီး Admin သုံးသပ်ရန် ပြန်လည်တင်သွင်းပြီးပါပြီ။')
            else:
                messages.success(request, f'သင်ခန်းစာ "{course.title}" ကို အောင်မြင်စွာ ပြုပြင်ပြီးပါပြီ။')

            course.save()
            return redirect('instructor_courses')
    else:
        form = CourseEditForm(instance=course)

    context = {
        'form': form,
        'course': course,
    }
    return render(request, 'instructor/courses/edit.html', context)


@login_required
@instructor_required
@owns_course
def course_delete_view(request, course_id):
    """Delete course."""
    course = get_object_or_404(Course, id=course_id)

    # Only allow deletion of draft or rejected courses
    if course.status not in ['draft', 'rejected']:
        messages.error(request, 'Approved သို့မဟုတ် Pending Review သင်ခန်းစာများကို ဖျက်၍ မရပါ။')
        return redirect('instructor_courses')

    # Check if course has active subscriptions
    from subscriptions.models import Subscription
    active_subs = Subscription.objects.filter(course=course, is_active=True).count()
    if active_subs > 0:
        messages.error(request, 'ဤသင်ခန်းစာတွင် active subscriptions ရှိနေသောကြောင့် ဖျက်၍ မရပါ။')
        return redirect('instructor_courses')

    if request.method == 'POST':
        course_title = course.title
        course.delete()
        messages.success(request, f'သင်ခန်းစာ "{course_title}" ကို အောင်မြင်စွာ ဖျက်ပြီးပါပြီ။')
        return redirect('instructor_courses')

    # If not POST, redirect back
    return redirect('instructor_courses')


@login_required
@instructor_required
@owns_course
def course_submit_for_review(request, course_id):
    """Submit course for admin review."""
    course = get_object_or_404(Course, id=course_id)

    # Only allow submission for draft or rejected courses
    if course.status not in ['draft', 'rejected']:
        messages.warning(request, 'ဤသင်ခန်းစာကို ထပ်မံတင်သွင်း၍ မရနိုင်ပါ။')
        return redirect('instructor_courses')

    # Validate course has minimum content
    if not course.sections.exists():
        messages.error(request, 'သင်ခန်းစာတွင် အနည်းဆုံး အပိုင်း ၁ ပိုင်း ရှိရမည်။')
        return redirect('course_curriculum', course_id=course.id)

    total_lessons = sum(section.lessons.count() for section in course.sections.all())
    if total_lessons == 0:
        messages.error(request, 'သင်ခန်းစာတွင် အနည်းဆုံး သင်ခန်းစာ ၁ ခု ရှိရမည်။')
        return redirect('course_curriculum', course_id=course.id)

    # Submit for review
    course.submit_for_review()
    messages.success(request, f'သင်ခန်းစာ "{course.title}" ကို Admin သုံးသပ်ရန် အောင်မြင်စွာ တင်သွင်းပြီးပါပြီ။')
    return redirect('instructor_courses')


@login_required
@instructor_required
@owns_course
def course_students_view(request, course_id):
    """View students enrolled in the course."""
    course = get_object_or_404(Course, id=course_id)

    # Get all subscriptions for this course
    from subscriptions.models import Subscription
    from payments.models import Payment

    subscriptions = Subscription.objects.filter(
        course=course
    ).select_related('user', 'payment').order_by('-created_at')

    # Get payment information
    payments = Payment.objects.filter(
        course=course
    ).select_related('user', 'reviewed_by').order_by('-created_at')

    context = {
        'course': course,
        'subscriptions': subscriptions,
        'payments': payments,
    }
    return render(request, 'instructor/courses/students.html', context)


@login_required
@instructor_required
@owns_course
def course_curriculum_view(request, course_id):
    """Manage course curriculum."""
    course = get_object_or_404(Course, id=course_id)
    sections = course.sections.all().order_by('order').prefetch_related('lessons')

    context = {
        'course': course,
        'sections': sections,
    }
    return render(request, 'instructor/courses/curriculum.html', context)


# ============================================================================
# CURRICULUM MANAGEMENT AJAX ENDPOINTS
# ============================================================================


@login_required
@instructor_required
@require_POST
def section_create_ajax(request, course_id):
    """Create a new section via AJAX."""
    course = get_object_or_404(Course, id=course_id, instructor=request.user)

    try:
        data = json.loads(request.body)
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()

        if not title:
            return JsonResponse({
                'success': False,
                'error': 'Section အမည် ထည့်ရန် လိုအပ်ပါသည။ / Title is required.'
            }, status=400)

        # Get the next order number (explicitly check for None to handle order=0)
        max_order_result = course.sections.aggregate(models.Max('order'))['order__max']
        max_order = max_order_result if max_order_result is not None else -1

        section = Section.objects.create(
            course=course,
            title=title,
            description=description,
            order=max_order + 1
        )

        return JsonResponse({
            'success': True,
            'section': {
                'id': section.id,
                'title': section.title,
                'description': section.description,
                'order': section.order,
            }
        })
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating section: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Section ဖန်တီးရာတွင် အမှားအယွင်း ရှိပါသည်။ ကျေးဇူးပြု၍ ထပ်မံကြိုးစားပါ။ / Error creating section. Please try again.'
        }, status=500)


@login_required
@instructor_required
@require_POST
def section_update_ajax(request, course_id, section_id):
    """Update section via AJAX."""
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    section = get_object_or_404(Section, id=section_id, course=course)

    try:
        data = json.loads(request.body)
        section.title = data.get('title', section.title).strip()
        section.description = data.get('description', section.description).strip()
        section.save()

        return JsonResponse({
            'success': True,
            'section': {
                'id': section.id,
                'title': section.title,
                'description': section.description,
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@instructor_required
@require_POST
def section_delete_ajax(request, course_id, section_id):
    """Delete section via AJAX."""
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    section = get_object_or_404(Section, id=section_id, course=course)

    try:
        section.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@instructor_required
@require_POST
def section_reorder_ajax(request, course_id):
    """Reorder sections via drag-and-drop."""
    course = get_object_or_404(Course, id=course_id, instructor=request.user)

    try:
        from django.db import transaction
        data = json.loads(request.body)
        section_ids = data.get('section_ids', [])

        # Use atomic transaction with high temporary values to avoid unique constraint violations
        with transaction.atomic():
            # First, set all sections to very high temporary orders (10000+)
            for idx, section in enumerate(Section.objects.filter(id__in=section_ids, course=course)):
                section.order = 10000 + idx
                section.save()

            # Then update to final order
            for index, section_id in enumerate(section_ids):
                Section.objects.filter(id=section_id, course=course).update(order=index)

        return JsonResponse({'success': True})
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error reordering sections: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@instructor_required
@require_POST
def lesson_create_ajax(request, course_id, section_id):
    """Create a new lesson via AJAX with content upload."""
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    section = get_object_or_404(Section, id=section_id, course=course)

    try:
        # Handle FormData (multipart/form-data)
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        content_type = request.POST.get('content_type', 'video')

        if not title:
            return JsonResponse({
                'success': False,
                'error': 'Lesson အမည် ထည့်ရန် လိုအပ်ပါသည်။ / Title is required.'
            }, status=400)

        # Get the next order number (explicitly check for None to handle order=0)
        max_order_result = section.lessons.aggregate(models.Max('order'))['order__max']
        max_order = max_order_result if max_order_result is not None else -1

        # Create lesson
        lesson = Lesson.objects.create(
            section=section,
            title=title,
            description=description,
            content_type=content_type,
            order=max_order + 1
        )

        # Handle content based on type
        if content_type == 'video':
            # Handle video file upload
            if 'video_file' in request.FILES:
                from core.storage_service import handle_file_upload, upload_lesson_video
                success, result, url = handle_file_upload(
                    upload_lesson_video,
                    request.FILES['video_file'],
                    lesson_id=lesson.id
                )
                if success:
                    lesson.video_file = result
                else:
                    lesson.delete()
                    return JsonResponse({'success': False, 'error': result}, status=400)

            # Handle video URL
            video_url = request.POST.get('video_url', '').strip()
            if video_url:
                lesson.video_url = video_url

        elif content_type in ['text', 'quiz', 'assignment']:
            text_content = request.POST.get('text_content', '').strip()
            if text_content:
                lesson.text_content = text_content

        # Handle duration
        duration = request.POST.get('duration_minutes', '').strip()
        if duration:
            try:
                lesson.duration_minutes = int(duration)
            except ValueError:
                pass

        lesson.save()

        return JsonResponse({
            'success': True,
            'lesson': {
                'id': lesson.id,
                'title': lesson.title,
                'content_type': lesson.content_type,
                'order': lesson.order,
            }
        })
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating lesson: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Lesson ဖန်တီးရာတွင် အမှားအယွင်း ရှိပါသည်။ ကျေးဇူးပြု၍ ထပ်မံကြိုးစားပါ။ / Error creating lesson. Please try again.'
        }, status=500)


@login_required
@instructor_required
def lesson_get_ajax(request, course_id, lesson_id):
    """Get lesson data via AJAX."""
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    lesson = get_object_or_404(Lesson, id=lesson_id, section__course=course)

    return JsonResponse({
        'success': True,
        'lesson': {
            'id': lesson.id,
            'title': lesson.title,
            'description': lesson.description or '',
            'content_type': lesson.content_type,
            'video_url': lesson.video_url or '',
            'video_file_url': lesson.video_file.url if lesson.video_file else '',
            'video_file_name': lesson.video_file.name.split('/')[-1] if lesson.video_file else '',
            'text_content': lesson.text_content or '',
            'duration_minutes': lesson.duration_minutes or 0,
        }
    })


@login_required
@instructor_required
@require_POST
def lesson_update_ajax(request, course_id, lesson_id):
    """Update lesson via AJAX with content."""
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    lesson = get_object_or_404(Lesson, id=lesson_id, section__course=course)

    try:
        # Handle FormData (multipart/form-data)
        lesson.title = request.POST.get('title', lesson.title).strip()
        lesson.description = request.POST.get('description', '').strip()

        # Check if content type is being changed
        new_content_type = request.POST.get('content_type', lesson.content_type).strip()
        if new_content_type != lesson.content_type:
            # Clear old content when changing content type
            lesson.video_file = None
            lesson.video_url = ''
            lesson.text_content = ''
            lesson.content_type = new_content_type

        # Handle content based on type
        if lesson.content_type == 'video':
            # Handle video file upload
            if 'video_file' in request.FILES:
                from core.storage_service import handle_file_upload, upload_lesson_video
                success, result, url = handle_file_upload(
                    upload_lesson_video,
                    request.FILES['video_file'],
                    lesson_id=lesson.id
                )
                if success:
                    lesson.video_file = result
                else:
                    return JsonResponse({'success': False, 'error': result}, status=400)

            # Handle video URL
            video_url = request.POST.get('video_url', '').strip()
            if video_url:
                lesson.video_url = video_url

        elif lesson.content_type in ['text', 'quiz', 'assignment']:
            text_content = request.POST.get('text_content', '').strip()
            if text_content:
                lesson.text_content = text_content

        # Handle duration
        duration = request.POST.get('duration_minutes', '').strip()
        if duration:
            try:
                lesson.duration_minutes = int(duration)
            except ValueError:
                pass

        lesson.save()

        return JsonResponse({
            'success': True,
            'lesson': {
                'id': lesson.id,
                'title': lesson.title,
            }
        })
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error updating lesson: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Lesson update မအောင်မြင်ပါ။ / Failed to update lesson.'
        }, status=500)


@login_required
@instructor_required
@require_POST
def lesson_delete_ajax(request, course_id, lesson_id):
    """Delete lesson via AJAX."""
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    lesson = get_object_or_404(Lesson, id=lesson_id, section__course=course)

    try:
        lesson.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@instructor_required
@require_POST
def lesson_reorder_ajax(request, course_id, section_id):
    """Reorder lessons via drag-and-drop."""
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    section = get_object_or_404(Section, id=section_id, course=course)

    try:
        from django.db import transaction
        # Parse JSON data
        data = json.loads(request.body)
        lesson_ids = data.get('lesson_ids', [])

        if not lesson_ids:
            return JsonResponse({'success': False, 'error': 'No lesson IDs provided'}, status=400)

        # Validate all lessons belong to this section
        existing_lessons = set(section.lessons.values_list('id', flat=True))
        for lesson_id in lesson_ids:
            if int(lesson_id) not in existing_lessons:
                return JsonResponse({'success': False, 'error': f'Invalid lesson ID: {lesson_id}'}, status=400)

        # Use atomic transaction with high temporary values to avoid unique constraint violations
        with transaction.atomic():
            # First, set all lessons to very high temporary orders (10000+)
            for idx, lesson in enumerate(Lesson.objects.filter(id__in=lesson_ids, section=section)):
                lesson.order = 10000 + idx
                lesson.save()

            # Then update to final order
            for index, lesson_id in enumerate(lesson_ids):
                Lesson.objects.filter(id=lesson_id, section=section).update(order=index)

        return JsonResponse({'success': True})
    except json.JSONDecodeError as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"JSON decode error in lesson reorder: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error reordering lessons: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': f'Lesson reorder မအောင်မြင်ပါ။ / Failed to reorder lessons. Error: {str(e)}'}, status=500)


@login_required
@instructor_required
def lesson_content_edit(request, course_id, lesson_id):
    """Edit lesson content (video, text, files)."""
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    lesson = get_object_or_404(Lesson, id=lesson_id, section__course=course)

    if request.method == 'POST':
        try:
            # Handle video upload
            if lesson.content_type == 'video' and 'video_file' in request.FILES:
                from core.storage_service import handle_file_upload, upload_lesson_video
                success, result, url = handle_file_upload(
                    upload_lesson_video,
                    request.FILES['video_file'],
                    lesson_id=lesson.id
                )
                if success:
                    lesson.video_file = result
                    messages.success(request, 'ဗီဒီယို upload ပြီးပါပြီ။ / Video uploaded successfully.')
                else:
                    messages.error(request, result)
                    return redirect('lesson_content_edit', course_id=course_id, lesson_id=lesson_id)

            # Handle video URL
            if lesson.content_type == 'video' and 'video_url' in request.POST:
                lesson.video_url = request.POST.get('video_url', '').strip()

            # Handle text content
            if lesson.content_type == 'text' and 'text_content' in request.POST:
                lesson.text_content = request.POST.get('text_content', '').strip()

            # Handle duration
            duration = request.POST.get('duration_minutes', '').strip()
            if duration:
                lesson.duration_minutes = int(duration)

            lesson.save()
            messages.success(request, 'Lesson content သိမ်းဆည်းပြီးပါပြီ။ / Lesson content saved.')
            return redirect('course_curriculum', course_id=course_id)

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error saving lesson content: {str(e)}", exc_info=True)
            messages.error(request, f'အမှားအယွင်း ရှိပါသည်။ / Error: {str(e)}')

    context = {
        'course': course,
        'lesson': lesson,
        'section': lesson.section,
    }
    return render(request, 'instructor/courses/lesson_content_edit.html', context)


@login_required
@instructor_required
def course_preview(request, course_id):
    """Preview course as students would see it - redirects to learning interface."""
    course = get_object_or_404(Course, id=course_id, instructor=request.user)

    # Redirect to the actual student learning interface
    # The learning view will handle the preview mode
    return redirect('course_learn', course_id=course.id)
