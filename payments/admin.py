from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Payment, PaymentHistory


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin interface for payments with approval workflow."""
    list_display = ('user_info', 'course_info', 'amount', 'status_badge', 'payment_method', 'created_at', 'quick_actions')
    list_filter = ('status', 'payment_method', 'access_type', 'is_global', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'course__title', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at', 'reviewed_at', 'reviewed_by', 'receipt_preview')
    date_hierarchy = 'created_at'
    actions = ['approve_payments', 'reject_payments']

    fieldsets = (
        ('Payment Information', {
            'fields': ('user', 'course', 'amount', 'access_type', 'is_global')
        }),
        ('Transaction Details', {
            'fields': ('receipt', 'receipt_preview', 'transaction_id', 'payment_method', 'notes')
        }),
        ('Review Status', {
            'fields': ('status', 'reviewed_by', 'reviewed_at', 'admin_notes', 'rejection_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def user_info(self, obj):
        """Display user name with link."""
        user_url = reverse('admin:users_user_change', args=[obj.user.id])
        return format_html(
            '<a href="{}" target="_blank">{}</a><br><small>{}</small>',
            user_url,
            obj.user.get_full_name(),
            obj.user.email
        )
    user_info.short_description = 'Student'

    def course_info(self, obj):
        """Display course with link."""
        if obj.course:
            course_url = reverse('admin:courses_course_change', args=[obj.course.id])
            return format_html(
                '<a href="{}" target="_blank">{}</a>',
                course_url,
                obj.course.title
            )
        return format_html('<span style="color: #007bff;">Global Subscription</span>')
    course_info.short_description = 'Course'

    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'pending': '#ffc107',
            'approved': '#28a745',
            'rejected': '#dc3545'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def receipt_preview(self, obj):
        """Display receipt preview."""
        if obj.receipt:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="max-width: 300px; max-height: 300px;"/></a>',
                obj.receipt.url,
                obj.receipt.url
            )
        return '-'
    receipt_preview.short_description = 'Receipt Preview'

    def quick_actions(self, obj):
        """Quick approve/reject buttons in list view."""
        if obj.status == 'pending':
            return format_html(
                '<a class="button" href="{}?action=approve" style="background: #28a745; color: white;">✅ Approve</a> '
                '<a class="button" href="{}?action=reject" style="background: #dc3545; color: white;">❌ Reject</a>',
                reverse('admin:payments_payment_change', args=[obj.id]),
                reverse('admin:payments_payment_change', args=[obj.id])
            )
        elif obj.status == 'approved':
            return format_html('<span style="color: #28a745;">✅ Approved</span>')
        elif obj.status == 'rejected':
            return format_html('<span style="color: #dc3545;">❌ Rejected</span>')
        return '-'
    quick_actions.short_description = 'Actions'

    def approve_payments(self, request, queryset):
        """Bulk approve selected payments."""
        approved_count = 0
        for payment in queryset.filter(status='pending'):
            try:
                payment.approve(request.user)
                approved_count += 1
                self.log_change(request, payment, f'Approved by {request.user.email}')
            except Exception as e:
                self.message_user(
                    request,
                    f'Error approving payment for {payment.user.get_full_name()}: {str(e)}',
                    level='error'
                )

        if approved_count > 0:
            self.message_user(
                request,
                f'Successfully approved {approved_count} payment(s) and created subscriptions.',
                level='success'
            )
    approve_payments.short_description = '✅ Approve selected payments'

    def reject_payments(self, request, queryset):
        """Bulk reject selected payments - Note: Rejection reason must be set individually."""
        self.message_user(
            request,
            'To reject payments with proper reasons, please edit each payment individually and provide rejection reason.',
            level='warning'
        )
    reject_payments.short_description = '❌ Reject payments (requires individual reasons)'

    def save_model(self, request, obj, form, change):
        """Handle manual status changes from detail page."""
        if change:  # Editing existing object
            old_obj = Payment.objects.get(pk=obj.pk)

            # If status changed to approved
            if old_obj.status != 'approved' and obj.status == 'approved':
                obj.approve(request.user)
                self.message_user(request, f'Payment approved! Subscription created for {obj.user.get_full_name()}.', level='success')
                self.log_change(request, obj, f'Approved by {request.user.email}')
                return  # approve() already saves

            # If status changed to rejected
            elif old_obj.status != 'rejected' and obj.status == 'rejected':
                if not obj.rejection_reason or obj.rejection_reason.strip() == '':
                    self.message_user(
                        request,
                        'Error: Rejection reason is REQUIRED when rejecting a payment. Please provide a reason.',
                        level='error'
                    )
                    obj.status = old_obj.status  # Revert status
                    super().save_model(request, obj, form, change)
                    return

                reason = obj.rejection_reason
                obj.reject(request.user, reason)
                self.message_user(
                    request,
                    f'Payment rejected. Student will be notified with the reason.',
                    level='warning'
                )
                self.log_change(request, obj, f'Rejected by {request.user.email} - Reason: {reason}')
                return  # reject() already saves

        super().save_model(request, obj, form, change)


@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    """Admin interface for payment history."""
    list_display = ('payment', 'old_status', 'new_status', 'changed_by', 'created_at')
    list_filter = ('old_status', 'new_status', 'created_at')
    search_fields = ('payment__user__email', 'notes')
    readonly_fields = ('created_at',)

