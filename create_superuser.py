#!/usr/bin/env python3
"""
Create superuser if it doesn't exist.
Used during deployment when shell access is not available.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Get credentials from environment variables
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@pyinnyahub.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
first_name = os.environ.get('DJANGO_SUPERUSER_FIRST_NAME', 'Admin')
last_name = os.environ.get('DJANGO_SUPERUSER_LAST_NAME', 'User')

if not password:
    print("⚠️  DJANGO_SUPERUSER_PASSWORD not set. Skipping superuser creation.")
    print("   Set this environment variable in Render to create admin account.")
    exit(0)

# Check if superuser already exists
if User.objects.filter(email=email).exists():
    user = User.objects.get(email=email)
    # Update password in case it changed
    user.set_password(password)
    user.save()
    print(f"✅ Updated existing superuser: {email}")
else:
    # Create new superuser
    User.objects.create_superuser(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )
    print(f"✅ Created superuser: {email}")

print(f"\n📝 Admin Login:")
print(f"   Email: {email}")
print(f"   Password: ****** (from DJANGO_SUPERUSER_PASSWORD)")
