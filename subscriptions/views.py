"""
Views for subscription management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from courses.models import Course
from .models import Subscription
from payments.models import Payment


@login_required
def my_subscriptions_view(request):
    """Display user's active and expired subscriptions."""
    active_subscriptions = Subscription.objects.filter(
        student=request.user,
        is_active=True
    ).select_related('course', 'course__instructor', 'course__category')

    expired_subscriptions = Subscription.objects.filter(
        student=request.user,
        is_active=False
    ).select_related('course', 'course__instructor', 'course__category')[:10]

    context = {
        'active_subscriptions': active_subscriptions,
        'expired_subscriptions': expired_subscriptions,
    }
    return render(request, 'subscriptions/my_subscriptions.html', context)


@login_required
def enroll_course_view(request, course_slug):
    """Initiate course enrollment - redirects to payment upload."""
    course = get_object_or_404(Course, slug=course_slug, status='approved', is_published=True)

    # Check if already enrolled
    existing_subscription = Subscription.objects.filter(
        student=request.user,
        course=course,
        is_active=True
    ).first()

    if existing_subscription:
        if not existing_subscription.is_expired():
            messages.warning(request, 'သင့်တွင် ဤသင်ခန်းစာ ရှိပြီးဖြစ်ပါသည်။')
            return redirect('course_detail', slug=course_slug)

    # Check for pending payment
    pending_payment = Payment.objects.filter(
        student=request.user,
        course=course,
        status='pending'
    ).first()

    if pending_payment:
        messages.info(request, 'သင့်ငွေပေးချေမှု စိစစ်နေဆဲဖြစ်ပါသည်။ ခဏစောင့်ဆိုင်းပေးပါ။')
        return redirect('payment_status', payment_id=pending_payment.id)

    # Redirect to payment upload
    return redirect('upload_payment', course_slug=course_slug)


@login_required
def subscription_detail_view(request, subscription_id):
    """View subscription details and lessons."""
    subscription = get_object_or_404(
        Subscription,
        id=subscription_id,
        student=request.user
    )

    course = subscription.course
    sections = course.sections.filter(is_published=True).prefetch_related('lessons')

    context = {
        'subscription': subscription,
        'course': course,
        'sections': sections,
    }
    return render(request, 'subscriptions/subscription_detail.html', context)
