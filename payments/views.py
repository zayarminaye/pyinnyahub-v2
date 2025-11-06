"""
Views for payment management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from courses.models import Course
from .models import Payment


@login_required
def upload_payment_view(request, course_slug):
    """Upload payment receipt for course enrollment."""
    course = get_object_or_404(Course, slug=course_slug, status='approved', is_published=True)

    # Check for existing pending payment
    existing_payment = Payment.objects.filter(
        student=request.user,
        course=course,
        status='pending'
    ).first()

    if existing_payment:
        messages.info(request, 'သင့်တွင် စောင့်ဆိုင်းနေဆဲ ငွေပေးချေမှု ရှိပြီးဖြစ်ပါသည်။')
        return redirect('payment_status', payment_id=existing_payment.id)

    if request.method == 'POST':
        amount = request.POST.get('amount')
        payment_method = request.POST.get('payment_method')
        transaction_id = request.POST.get('transaction_id')
        receipt = request.FILES.get('receipt')

        # Validate
        if not all([amount, payment_method, transaction_id, receipt]):
            messages.error(request, 'ကျေးဇူးပြု၍ အချက်အလက်အားလုံး ဖြည့်ပေးပါ။')
        else:
            try:
                # Create payment
                payment = Payment.objects.create(
                    student=request.user,
                    course=course,
                    amount=amount,
                    payment_method=payment_method,
                    transaction_id=transaction_id,
                    receipt=receipt,
                    status='pending'
                )
                messages.success(request, 'ငွေပေးချေမှု အောင်မြင်စွာ တင်သွင်းပြီးပါပြီ။ Admin မှ အတည်ပြုပေးမည်ဖြစ်ပါသည်။')
                return redirect('payment_status', payment_id=payment.id)
            except Exception as e:
                messages.error(request, f'အမှား ဖြစ်ပွားခဲ့ပါသည်: {str(e)}')

    context = {
        'course': course,
    }
    return render(request, 'payments/upload_payment.html', context)


@login_required
def payment_status_view(request, payment_id):
    """View payment status."""
    payment = get_object_or_404(Payment, id=payment_id, student=request.user)

    context = {
        'payment': payment,
    }
    return render(request, 'payments/payment_status.html', context)


@login_required
def my_payments_view(request):
    """View all user payments."""
    payments = Payment.objects.filter(
        student=request.user
    ).select_related('course', 'reviewed_by').order_by('-created_at')

    context = {
        'payments': payments,
    }
    return render(request, 'payments/my_payments.html', context)
