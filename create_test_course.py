#!/usr/bin/env python3
"""
Create a test course for testing the enrollment workflow.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from courses.models import Course, Category, Section, Lesson
from django.utils.text import slugify

User = get_user_model()

def create_test_course():
    """Create a test course with sections and lessons."""

    # Get instructor
    instructor = User.objects.filter(role='instructor').first()
    if not instructor:
        print("❌ No instructor found. Please create an instructor first.")
        return

    # Get or create Programming category
    category, _ = Category.objects.get_or_create(
        slug='programming',
        defaults={
            'name': 'Programming',
            'icon': '💻',
            'is_active': True,
        }
    )

    # Create course
    course, created = Course.objects.get_or_create(
        slug='python-for-beginners',
        defaults={
            'title': 'Python for Beginners - Complete Course',
            'short_description': 'Learn Python programming from scratch with practical examples',
            'description': 'This comprehensive Python course covers everything from basic syntax to advanced topics. Perfect for beginners who want to start their programming journey.',
            'instructor': instructor,
            'category': category,
            'price': 50000,
            'access_type': 'monthly',
            'level': 'beginner',
            'language': 'Burmese',
            'duration_hours': 20,
            'what_you_will_learn': [
                'Python basics and syntax',
                'Variables, data types, and operators',
                'Control flow and loops',
                'Functions and modules',
                'Object-oriented programming',
                'File handling and exceptions'
            ],
            'requirements': [
                'A computer with internet connection',
                'Willingness to learn',
                'No prior programming experience needed'
            ],
            'status': 'approved',  # Pre-approved for testing
            'is_published': True,
            'is_featured': True,
        }
    )

    if created:
        print(f"✅ Created course: {course.title}")

        # Create sections
        section1, _ = Section.objects.get_or_create(
            course=course,
            order=1,
            defaults={
                'title': 'Introduction to Python',
                'description': 'Get started with Python programming',
            }
        )

        section2, _ = Section.objects.get_or_create(
            course=course,
            order=2,
            defaults={
                'title': 'Python Fundamentals',
                'description': 'Learn the core concepts of Python',
            }
        )

        # Create lessons for section 1
        Lesson.objects.get_or_create(
            section=section1,
            order=1,
            defaults={
                'title': 'Welcome to the Course',
                'description': 'Introduction and course overview',
                'content_type': 'video',
                'duration_minutes': 5,
                'is_preview': True,
            }
        )

        Lesson.objects.get_or_create(
            section=section1,
            order=2,
            defaults={
                'title': 'Installing Python',
                'description': 'How to install Python on your computer',
                'content_type': 'video',
                'duration_minutes': 10,
                'is_preview': True,
            }
        )

        # Create lessons for section 2
        Lesson.objects.get_or_create(
            section=section2,
            order=1,
            defaults={
                'title': 'Variables and Data Types',
                'description': 'Learn about Python variables and data types',
                'content_type': 'video',
                'duration_minutes': 15,
            }
        )

        Lesson.objects.get_or_create(
            section=section2,
            order=2,
            defaults={
                'title': 'Operators in Python',
                'description': 'Understanding Python operators',
                'content_type': 'video',
                'duration_minutes': 20,
            }
        )

        print(f"✅ Created 2 sections with 4 lessons")
        print(f"\n📚 Course Details:")
        print(f"   Title: {course.title}")
        print(f"   Price: {course.price} MMK")
        print(f"   Access Type: {course.access_type}")
        print(f"   Instructor: {instructor.get_full_name()}")
        print(f"   URL: /courses/{course.slug}/")
    else:
        print(f"ℹ️  Course already exists: {course.title}")

if __name__ == '__main__':
    create_test_course()
