from django.contrib import admin
from .models import Payout


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    """Admin interface for instructor payouts."""
    list_display = ('instructor', 'course', 'amount', 'net_amount', 'status', 'created_at', 'processed_at')
    list_filter = ('status', 'created_at', 'processed_at')
    search_fields = ('instructor__email', 'instructor__first_name', 'instructor__last_name', 'course__title')
    readonly_fields = ('created_at', 'updated_at', 'net_amount')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Payout Information', {
            'fields': ('instructor', 'course', 'payment', 'amount', 'commission', 'net_amount')
        }),
        ('Status & Processing', {
            'fields': ('status', 'processed_by', 'processed_at', 'payment_method', 'transaction_id', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

