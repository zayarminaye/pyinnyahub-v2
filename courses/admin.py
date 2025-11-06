from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Category, Course, Section, Lesson


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for course categories."""
    list_display = ('name', 'slug', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


class SectionInline(admin.TabularInline):
    """Inline admin for course sections."""
    model = Section
    extra = 0
    fields = ('title', 'order')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Enhanced admin interface for courses with approval workflow and audit trail."""

    list_display = (
        'title',
        'instructor_info',
        'category',
        'status_badge',
        'price',
        'is_published',
        'created_at',
        'quick_actions'
    )
    list_filter = ('status', 'is_published', 'is_featured', 'category', 'level', 'created_at')
    search_fields = ('title', 'description', 'instructor__email', 'instructor__first_name', 'instructor__last_name')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [SectionInline]
    readonly_fields = (
        'instructor_details',
        'enrollment_count',
        'view_count',
        'created_at',
        'updated_at',
        'reviewed_by',
        'reviewed_at'
    )
    actions = ['approve_courses', 'reject_courses', 'publish_courses', 'unpublish_courses']

    fieldsets = (
        ('👨‍🏫 Instructor Information', {
            'fields': ('instructor_details',)
        }),
        ('📚 Basic Information', {
            'fields': ('title', 'slug', 'instructor', 'category', 'short_description', 'description')
        }),
        ('📖 Course Details', {
            'fields': ('level', 'language', 'duration_hours', 'what_you_will_learn', 'requirements', 'target_audience')
        }),
        ('🎬 Media', {
            'fields': ('thumbnail', 'promo_video')
        }),
        ('💰 Pricing', {
            'fields': ('price', 'access_type')
        }),
        ('✅ Review & Status', {
            'fields': ('status', 'reviewed_by', 'reviewed_at', 'rejection_reason', 'is_published', 'is_featured')
        }),
        ('📊 Statistics', {
            'fields': ('enrollment_count', 'view_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def instructor_info(self, obj):
        """Display instructor name with link."""
        user_url = reverse('admin:users_user_change', args=[obj.instructor.id])
        return format_html(
            '<a href="{}" target="_blank">{}</a>',
            user_url,
            obj.instructor.get_full_name()
        )
    instructor_info.short_description = 'Instructor'

    def instructor_details(self, obj):
        """Enhanced display of instructor information."""
        user = obj.instructor
        user_url = reverse('admin:users_user_change', args=[user.id])
        return format_html(
            '<div style="padding: 10px; background: #f8f9fa; border-radius: 5px;">'
            '<p><strong>Name:</strong> <a href="{}" target="_blank">{}</a></p>'
            '<p><strong>Email:</strong> {}</p>'
            '<p><strong>Role:</strong> {}</p>'
            '</div>',
            user_url,
            user.get_full_name(),
            user.email,
            user.get_role_display()
        )
    instructor_details.short_description = 'Instructor Details'

    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'draft': '#6c757d',
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

    def quick_actions(self, obj):
        """Quick approve/reject buttons in list view."""
        if obj.status == 'pending':
            return format_html(
                '<a class="button" href="{}?action=approve">✅ Approve</a> '
                '<a class="button" href="{}?action=reject">❌ Reject</a>',
                reverse('admin:courses_course_change', args=[obj.id]),
                reverse('admin:courses_course_change', args=[obj.id])
            )
        elif obj.status == 'rejected':
            return format_html(
                '<span style="color: #dc3545;">⚠️ Rejected</span>'
            )
        return '-'
    quick_actions.short_description = 'Actions'

    def approve_courses(self, request, queryset):
        """Bulk approve selected courses."""
        approved_count = 0
        for course in queryset.filter(status__in=['pending', 'rejected']):
            try:
                course.approve(request.user)
                approved_count += 1
                # Log the action
                self.log_change(request, course, f'Approved by {request.user.email}')
            except Exception as e:
                self.message_user(
                    request,
                    f'Error approving {course.title}: {str(e)}',
                    level='error'
                )

        if approved_count > 0:
            self.message_user(
                request,
                f'Successfully approved {approved_count} course(s).',
                level='success'
            )
    approve_courses.short_description = '✅ Approve selected courses'

    def reject_courses(self, request, queryset):
        """Bulk reject selected courses - Note: Rejection reason must be set individually."""
        self.message_user(
            request,
            'To reject courses with proper reasons, please edit each course individually and provide rejection reason.',
            level='warning'
        )
    reject_courses.short_description = '❌ Reject courses (requires individual reasons)'

    def publish_courses(self, request, queryset):
        """Bulk publish approved courses."""
        published_count = 0
        for course in queryset.filter(status='approved'):
            course.is_published = True
            course.save(update_fields=['is_published'])
            published_count += 1

        if published_count > 0:
            self.message_user(
                request,
                f'Successfully published {published_count} course(s).',
                level='success'
            )
    publish_courses.short_description = '📢 Publish selected courses'

    def unpublish_courses(self, request, queryset):
        """Bulk unpublish courses."""
        unpublished_count = 0
        for course in queryset:
            course.is_published = False
            course.save(update_fields=['is_published'])
            unpublished_count += 1

        if unpublished_count > 0:
            self.message_user(
                request,
                f'Successfully unpublished {unpublished_count} course(s).',
                level='success'
            )
    unpublish_courses.short_description = '📴 Unpublish selected courses'

    def save_model(self, request, obj, form, change):
        """Handle manual status changes from detail page with audit logging."""
        if change:  # Editing existing object
            old_obj = Course.objects.get(pk=obj.pk)

            # If status changed to approved
            if old_obj.status != 'approved' and obj.status == 'approved':
                obj.approve(request.user)
                self.message_user(request, f'Course "{obj.title}" approved successfully!', level='success')
                # Log the action
                self.log_change(request, obj, f'Approved by {request.user.email}')
                return  # approve() already saves

            # If status changed to rejected
            elif old_obj.status != 'rejected' and obj.status == 'rejected':
                if not obj.rejection_reason or obj.rejection_reason.strip() == '':
                    self.message_user(
                        request,
                        'Error: Rejection reason is REQUIRED when rejecting a course. Please provide a reason.',
                        level='error'
                    )
                    obj.status = old_obj.status  # Revert status
                    super().save_model(request, obj, form, change)
                    return

                reason = obj.rejection_reason
                obj.reject(request.user, reason)
                self.message_user(
                    request,
                    f'Course "{obj.title}" rejected. Instructor will see the rejection reason.',
                    level='warning'
                )
                # Log the action
                self.log_change(request, obj, f'Rejected by {request.user.email} - Reason: {reason}')
                return  # reject() already saves

        super().save_model(request, obj, form, change)


class LessonInline(admin.TabularInline):
    """Inline admin for section lessons."""
    model = Lesson
    extra = 0
    fields = ('title', 'order', 'content_type', 'duration_minutes', 'is_preview')


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    """Admin interface for course sections."""
    list_display = ('title', 'course', 'order', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'course__title')
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Admin interface for lessons."""
    list_display = ('title', 'section', 'content_type', 'duration_minutes', 'order', 'is_preview', 'is_approved')
    list_filter = ('content_type', 'is_preview', 'is_approved', 'requires_approval', 'created_at')
    search_fields = ('title', 'description', 'section__title')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Basic Information', {
            'fields': ('section', 'title', 'content_type', 'order', 'description', 'duration_minutes')
        }),
        ('Content', {
            'fields': ('video_url', 'video_file', 'text_content')
        }),
        ('Download Controls', {
            'fields': ('allow_video_download', 'allow_attachment_download')
        }),
        ('Access & Approval', {
            'fields': ('is_preview', 'is_approved', 'requires_approval')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

