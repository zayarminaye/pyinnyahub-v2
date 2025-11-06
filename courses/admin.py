from django.contrib import admin
from .models import Category, Course, Section, Lesson


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for course categories."""
    list_display = ('name', 'slug', 'is_active', 'course_count', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


class SectionInline(admin.TabularInline):
    """Inline admin for course sections."""
    model = Section
    extra = 0
    fields = ('title', 'order', 'is_published')


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
    fields = ('title', 'order', 'lesson_type', 'duration', 'is_free')


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    """Admin interface for course sections."""
    list_display = ('title', 'course', 'order', 'is_published', 'lesson_count')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'course__title')
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Admin interface for lessons."""
    list_display = ('title', 'section', 'lesson_type', 'duration', 'order', 'is_free')
    list_filter = ('lesson_type', 'is_free', 'created_at')
    search_fields = ('title', 'content', 'section__title')
    readonly_fields = ('created_at', 'updated_at')

