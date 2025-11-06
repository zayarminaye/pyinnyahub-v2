from django.contrib import admin
from .models import Payment, PaymentHistory


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin interface for payments."""
    list_display = ('user', 'course', 'amount', 'status', 'payment_method', 'created_at')
    list_filter = ('status', 'payment_method', 'access_type', 'is_global', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'course__title', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at', 'reviewed_at', 'reviewed_by')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Payment Information', {
            'fields': ('user', 'course', 'amount', 'access_type', 'is_global')
        }),
        ('Transaction Details', {
            'fields': ('receipt', 'transaction_id', 'payment_method', 'notes')
        }),
        ('Review Status', {
            'fields': ('status', 'reviewed_by', 'reviewed_at', 'admin_notes', 'rejection_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    """Admin interface for payment history."""
    list_display = ('payment', 'old_status', 'new_status', 'changed_by', 'created_at')
    list_filter = ('old_status', 'new_status', 'created_at')
    search_fields = ('payment__user__email', 'notes')
    readonly_fields = ('created_at',)

