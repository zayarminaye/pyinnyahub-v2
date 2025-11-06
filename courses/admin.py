from django.contrib import admin
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
    """Admin interface for courses."""
    list_display = ('title', 'instructor', 'category', 'status', 'price', 'is_published', 'created_at')
    list_filter = ('status', 'is_published', 'is_featured', 'category', 'created_at')
    search_fields = ('title', 'description', 'instructor__email')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [SectionInline]
    readonly_fields = ('enrollment_count', 'view_count', 'created_at', 'updated_at')

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'instructor', 'category', 'description')
        }),
        ('Details', {
            'fields': ('what_you_will_learn', 'requirements', 'target_audience', 'language')
        }),
        ('Media', {
            'fields': ('thumbnail', 'preview_video')
        }),
        ('Pricing', {
            'fields': ('price',)
        }),
        ('Status', {
            'fields': ('status', 'is_published', 'is_featured')
        }),
        ('Statistics', {
            'fields': ('enrollment_count', 'view_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


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

