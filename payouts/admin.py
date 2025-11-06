from django.contrib import admin
from .models import Payout


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    """Admin interface for instructor payouts."""
    list_display = ('instructor', 'course', 'amount', 'status', 'created_at', 'paid_at')
    list_filter = ('status', 'created_at', 'paid_at')
    search_fields = ('instructor__email', 'instructor__first_name', 'instructor__last_name', 'course__title')
    readonly_fields = ('created_at', 'updated_at', 'paid_at')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Payout Information', {
            'fields': ('instructor', 'course', 'payment', 'amount')
        }),
        ('Status', {
            'fields': ('status', 'paid_at', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

