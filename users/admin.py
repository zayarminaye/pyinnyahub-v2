from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, InstructorApplication


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for custom user model."""
    list_display = ('email', 'get_full_name', 'is_instructor', 'is_admin_user', 'is_active', 'date_joined')
    list_filter = ('is_instructor', 'is_admin_user', 'is_active', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number', 'bio', 'profile_picture')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_instructor', 'is_admin_user', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'is_instructor', 'is_admin_user'),
        }),
    )


@admin.register(InstructorApplication)
class InstructorApplicationAdmin(admin.ModelAdmin):
    """Admin interface for instructor applications."""
    list_display = ('user', 'status', 'years_of_experience', 'created_at', 'reviewed_at')
    list_filter = ('status', 'created_at', 'reviewed_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'expertise')
    readonly_fields = ('created_at', 'updated_at', 'reviewed_at', 'reviewed_by')

    fieldsets = (
        ('Applicant', {
            'fields': ('user',)
        }),
        ('Application Details', {
            'fields': ('expertise', 'years_of_experience', 'bio', 'portfolio_url')
        }),
        ('Status', {
            'fields': ('status', 'reviewed_by', 'reviewed_at', 'rejection_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

