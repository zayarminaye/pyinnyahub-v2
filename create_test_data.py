#!/usr/bin/env python3
"""
Quick script to create test data for Pyinnya Hub LMS.
Run: python3 create_test_data.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from courses.models import Category, Tag
from django.utils.text import slugify

User = get_user_model()

def create_test_data():
    print("Creating test data...")

    # Create test users
    print("\n1. Creating test users...")

    # Student
    student, created = User.objects.get_or_create(
        email='student@test.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'Student',
            'role': 'student',
            'is_active': True
        }
    )
    if created:
        student.set_password('student123')
        student.save()
        print(f"   ✓ Created student: {student.email}")
    else:
        print(f"   - Student already exists: {student.email}")

    # Instructor
    instructor, created = User.objects.get_or_create(
        email='instructor@test.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'Instructor',
            'role': 'instructor',
            'is_active': True,
            'bio': 'Experienced instructor with 10 years of teaching.',
            'expertise': 'Web Development, Python, Django',
            'years_of_experience': 10
        }
    )
    if created:
        instructor.set_password('instructor123')
        instructor.save()
        print(f"   ✓ Created instructor: {instructor.email}")
    else:
        print(f"   - Instructor already exists: {instructor.email}")

    # Create categories
    print("\n2. Creating course categories...")
    categories_data = [
        {'name': 'Programming', 'icon': '💻'},
        {'name': 'Business', 'icon': '💼'},
        {'name': 'Design', 'icon': '🎨'},
        {'name': 'Marketing', 'icon': '📈'},
        {'name': 'Languages', 'icon': '🗣️'},
    ]

    for idx, cat_data in enumerate(categories_data):
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'slug': slugify(cat_data['name']),
                'icon': cat_data['icon'],
                'description': f'{cat_data["name"]} courses for all levels',
                'is_active': True,
                'order': idx
            }
        )
        if created:
            print(f"   ✓ Created category: {category.name}")
        else:
            print(f"   - Category already exists: {category.name}")

    # Create tags
    print("\n3. Creating course tags...")
    tags_data = ['Python', 'Django', 'JavaScript', 'React', 'Node.js',
                 'HTML', 'CSS', 'SQL', 'Web Development', 'Mobile Development']

    for tag_name in tags_data:
        tag, created = Tag.objects.get_or_create(
            name=tag_name,
            defaults={'slug': slugify(tag_name)}
        )
        if created:
            print(f"   ✓ Created tag: {tag.name}")

    print("\n✅ Test data creation complete!")
    print("\n📝 Test Accounts Created:")
    print("   Student:")
    print("      Email: student@test.com")
    print("      Password: student123")
    print("\n   Instructor:")
    print("      Email: instructor@test.com")
    print("      Password: instructor123")
    print("\n   Admin (you created earlier):")
    print("      Email: [your superuser email]")
    print("      Password: [your superuser password]")

if __name__ == '__main__':
    create_test_data()
