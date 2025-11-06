#!/usr/bin/env python3
"""
Quick script to create test data for Pyinnya Hub LMS.
Run: python3 create_test_data.py

SECURITY NOTE: This script creates users WITHOUT passwords.
You MUST set passwords manually after running this script.
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
        # DO NOT set password here - user must set it manually for security
        print(f"   ✓ Created student: {student.email} (PASSWORD NOT SET)")
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
        # DO NOT set password here - user must set it manually for security
        print(f"   ✓ Created instructor: {instructor.email} (PASSWORD NOT SET)")
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
    print("\n⚠️  IMPORTANT: Set passwords for test accounts!")
    print("\nRun this command to set passwords:")
    print("\npython3 manage.py shell")
    print("\nThen in the shell:")
    print("from django.contrib.auth import get_user_model")
    print("User = get_user_model()")
    print("")
    print("# Set student password")
    print("student = User.objects.get(email='student@test.com')")
    print("student.set_password('YOUR_SECURE_PASSWORD')")
    print("student.save()")
    print("")
    print("# Set instructor password")
    print("instructor = User.objects.get(email='instructor@test.com')")
    print("instructor.set_password('YOUR_SECURE_PASSWORD')")
    print("instructor.save()")
    print("")
    print("📝 Test Accounts Created:")
    print("   - student@test.com (Student)")
    print("   - instructor@test.com (Instructor)")
    print("   - [Your admin email] (Admin - created via createsuperuser)")

if __name__ == '__main__':
    create_test_data()
