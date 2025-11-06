"""
Serializers for Courses app.
Handles course, section, lesson, and related data serialization.
"""
from rest_framework import serializers
from .models import Category, Tag, Course, Section, Lesson, LessonAttachment, CourseReview, Wishlist


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for course categories."""
    course_count = serializers.IntegerField(source='get_course_count', read_only=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'icon', 'is_active', 'order', 'course_count')


class TagSerializer(serializers.ModelSerializer):
    """Serializer for course tags."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class LessonAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for lesson attachments."""

    class Meta:
        model = LessonAttachment
        fields = ('id', 'title', 'file', 'file_size', 'created_at')


class LessonSerializer(serializers.ModelSerializer):
    """Serializer for lessons."""
    lesson_attachments = LessonAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = (
            'id', 'title', 'content_type', 'order', 'description',
            'video_url', 'video_file', 'text_content', 'duration_minutes',
            'attachments', 'is_preview', 'lesson_attachments', 'created_at'
        )


class SectionSerializer(serializers.ModelSerializer):
    """Serializer for course sections."""
    lessons = LessonSerializer(many=True, read_only=True)
    lesson_count = serializers.IntegerField(source='lesson_count', read_only=True)
    total_duration = serializers.IntegerField(source='total_duration', read_only=True)

    class Meta:
        model = Section
        fields = (
            'id', 'title', 'description', 'order',
            'lessons', 'lesson_count', 'total_duration', 'created_at'
        )


class CourseListSerializer(serializers.ModelSerializer):
    """Serializer for course list (minimal data)."""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = (
            'id', 'title', 'slug', 'short_description', 'thumbnail',
            'price', 'access_type', 'level', 'language', 'duration_hours',
            'instructor_name', 'category_name', 'tags',
            'enrollment_count', 'rating_average', 'rating_count',
            'is_featured', 'is_published', 'status', 'created_at'
        )


class CourseDetailSerializer(serializers.ModelSerializer):
    """Serializer for course detail (full data)."""
    instructor = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    sections = SectionSerializer(many=True, read_only=True)
    total_lessons = serializers.IntegerField(read_only=True)
    total_duration_minutes = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = (
            'id', 'title', 'slug', 'description', 'short_description',
            'thumbnail', 'promo_video', 'price', 'access_type',
            'level', 'language', 'duration_hours',
            'requirements', 'what_you_will_learn',
            'instructor', 'category', 'tags', 'sections',
            'status', 'is_published', 'is_featured',
            'enrollment_count', 'view_count', 'rating_average', 'rating_count',
            'total_lessons', 'total_duration_minutes',
            'created_at', 'updated_at'
        )

    def get_instructor(self, obj):
        return {
            'id': obj.instructor.id,
            'name': obj.instructor.get_full_name(),
            'email': obj.instructor.email,
            'bio': obj.instructor.bio,
            'expertise': obj.instructor.expertise,
            'profile_picture': obj.instructor.profile_picture.url if obj.instructor.profile_picture else None
        }


class CourseCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating courses."""

    class Meta:
        model = Course
        fields = (
            'title', 'slug', 'description', 'short_description',
            'thumbnail', 'promo_video', 'price', 'access_type',
            'level', 'language', 'duration_hours',
            'requirements', 'what_you_will_learn',
            'category', 'tags'
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        validated_data['instructor'] = self.context['request'].user
        course = Course.objects.create(**validated_data)
        if tags:
            course.tags.set(tags)
        return course


class CourseReviewSerializer(serializers.ModelSerializer):
    """Serializer for course reviews."""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = CourseReview
        fields = ('id', 'user', 'user_name', 'rating', 'review', 'is_approved', 'created_at')
        read_only_fields = ('user', 'is_approved')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class WishlistSerializer(serializers.ModelSerializer):
    """Serializer for wishlist."""
    course = CourseListSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = ('id', 'course', 'created_at')
        read_only_fields = ('user',)
