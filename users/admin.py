from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import User, InstructorApplication


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for custom user model."""
    list_display = ('email', 'get_full_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number', 'bio', 'profile_picture')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name'),
        }),
    )


@admin.register(InstructorApplication)
class InstructorApplicationAdmin(admin.ModelAdmin):
    """Admin interface for instructor applications with enhanced review capabilities."""

    list_display = (
        'applicant_info',
        'status_badge',
        'expertise',
        'has_resume',
        'has_certificates',
        'created_at',
        'reviewed_at',
        'quick_actions'
    )
    list_filter = ('status', 'created_at', 'reviewed_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'expertise')
    readonly_fields = (
        'applicant_details',
        'resume_link',
        'certificates_link',
        'created_at',
        'updated_at',
        'reviewed_at',
        'reviewed_by'
    )
    actions = ['approve_applications', 'reject_applications']

    fieldsets = (
        ('👤 Applicant Information', {
            'fields': ('applicant_details',)
        }),
        ('📝 Application Details', {
            'fields': ('expertise', 'experience', 'education', 'motivation')
        }),
        ('📎 Uploaded Documents', {
            'fields': ('resume_link', 'certificates_link')
        }),
        ('✅ Review & Status', {
            'fields': ('status', 'reviewed_by', 'reviewed_at', 'rejection_reason', 'admin_notes')
        }),
        ('🕒 Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def applicant_info(self, obj):
        """Display applicant name and email with link to user profile."""
        user_url = reverse('admin:users_user_change', args=[obj.user.id])
        return format_html(
            '<a href="{}" target="_blank"><strong>{}</strong></a><br><small>{}</small>',
            user_url,
            obj.user.get_full_name(),
            obj.user.email
        )
    applicant_info.short_description = 'Applicant'

    def applicant_details(self, obj):
        """Enhanced display of applicant information."""
        user = obj.user
        user_url = reverse('admin:users_user_change', args=[user.id])
        return format_html(
            '<div style="padding: 10px; background: #f8f9fa; border-radius: 5px;">'
            '<p><strong>Name:</strong> <a href="{}" target="_blank">{}</a></p>'
            '<p><strong>Email:</strong> {}</p>'
            '<p><strong>Phone:</strong> {}</p>'
            '<p><strong>Current Role:</strong> {}</p>'
            '</div>',
            user_url,
            user.get_full_name(),
            user.email,
            user.phone_number or 'Not provided',
            user.get_role_display()
        )
    applicant_details.short_description = 'Applicant Details'

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

    def has_resume(self, obj):
        """Show if resume is uploaded."""
        return '✅' if obj.resume else '❌'
    has_resume.short_description = 'Resume'

    def has_certificates(self, obj):
        """Show if certificates are uploaded."""
        return '✅' if obj.certificates else '❌'
    has_certificates.short_description = 'Certificates'

    def resume_link(self, obj):
        """Clickable link to download resume."""
        if obj.resume:
            return format_html(
                '<a href="{}" target="_blank" class="button">📄 Download Resume</a>',
                obj.resume.url
            )
        return format_html('<span style="color: #999;">No resume uploaded</span>')
    resume_link.short_description = 'Resume'

    def certificates_link(self, obj):
        """Clickable link to download certificates."""
        if obj.certificates:
            return format_html(
                '<a href="{}" target="_blank" class="button">📜 Download Certificates (PDF)</a>',
                obj.certificates.url
            )
        return format_html('<span style="color: #999;">No certificates uploaded</span>')
    certificates_link.short_description = 'Certificates'

    def quick_actions(self, obj):
        """Quick approve/reject buttons in list view."""
        if obj.status == 'pending':
            return format_html(
                '<a class="button" href="{}?action=approve" '
                'onclick="return confirm(\'Approve this application?\')">✅ Approve</a> '
                '<a class="button" href="{}?action=reject" '
                'onclick="return confirm(\'Reject this application?\')">❌ Reject</a>',
                reverse('admin:users_instructorapplication_change', args=[obj.id]),
                reverse('admin:users_instructorapplication_change', args=[obj.id])
            )
        return '-'
    quick_actions.short_description = 'Actions'

    def approve_applications(self, request, queryset):
        """Bulk approve selected applications."""
        approved_count = 0
        for application in queryset.filter(status='pending'):
            try:
                application.approve(request.user)
                approved_count += 1
            except Exception as e:
                self.message_user(
                    request,
                    f'Error approving {application.user.email}: {str(e)}',
                    level='error'
                )

        if approved_count > 0:
            self.message_user(
                request,
                f'Successfully approved {approved_count} application(s).',
                level='success'
            )
    approve_applications.short_description = '✅ Approve selected applications'

    def reject_applications(self, request, queryset):
        """Bulk reject selected applications - Note: Rejection reason must be set individually."""
        self.message_user(
            request,
            'To reject applications with proper reasons, please edit each application individually and provide a detailed rejection reason for the applicant.',
            level='warning'
        )
    reject_applications.short_description = '❌ Reject applications (requires individual reasons)'

    def save_model(self, request, obj, form, change):
        """Handle manual status changes from detail page."""
        if change:  # Editing existing object
            old_obj = InstructorApplication.objects.get(pk=obj.pk)

            # If status changed to approved
            if old_obj.status != 'approved' and obj.status == 'approved':
                obj.approve(request.user)
                self.message_user(request, 'Application approved successfully!', level='success')
                # Log the action
                self.log_change(request, obj, f'Approved by {request.user.email} - User promoted to instructor')
                return  # approve() already saves

            # If status changed to rejected
            elif old_obj.status != 'rejected' and obj.status == 'rejected':
                if not obj.rejection_reason or obj.rejection_reason.strip() == '':
                    self.message_user(
                        request,
                        'Error: Rejection reason is REQUIRED when rejecting an application. Please provide a detailed reason for the applicant.',
                        level='error'
                    )
                    obj.status = old_obj.status  # Revert status
                    super().save_model(request, obj, form, change)
                    return

                reason = obj.rejection_reason
                obj.reject(request.user, reason)
                self.message_user(
                    request,
                    f'Application rejected. {obj.user.get_full_name()} will see the rejection reason.',
                    level='warning'
                )
                # Log the action
                self.log_change(request, obj, f'Rejected by {request.user.email} - Reason: {reason}')
                return  # reject() already saves

        super().save_model(request, obj, form, change)

