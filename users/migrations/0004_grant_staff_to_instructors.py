# Generated manually to grant is_staff permission to existing instructors

from django.db import migrations


def grant_staff_to_instructors(apps, schema_editor):
    """Grant is_staff=True to all existing instructors."""
    User = apps.get_model('users', 'User')

    # Update all instructors who don't have is_staff permission
    instructors_updated = User.objects.filter(
        role='instructor',
        is_staff=False
    ).update(is_staff=True)

    if instructors_updated > 0:
        print(f"✅ Granted admin panel access to {instructors_updated} instructor(s)")


def revoke_staff_from_instructors(apps, schema_editor):
    """Reverse migration: revoke is_staff from instructors who aren't superusers."""
    User = apps.get_model('users', 'User')

    # Only revoke from instructors who aren't superusers
    instructors_updated = User.objects.filter(
        role='instructor',
        is_staff=True,
        is_superuser=False
    ).update(is_staff=False)

    if instructors_updated > 0:
        print(f"⚠️  Revoked admin panel access from {instructors_updated} instructor(s)")


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_instructorapplication_certificates_and_more'),
    ]

    operations = [
        migrations.RunPython(
            grant_staff_to_instructors,
            revoke_staff_from_instructors
        ),
    ]
