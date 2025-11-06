"""
Management command to initialize default notification settings.
Run this once after deployment to set up notification preferences.
"""
from django.core.management.base import BaseCommand
from notifications.models import NotificationSettings


class Command(BaseCommand):
    help = 'Initialize default notification settings for all events'

    def handle(self, *args, **options):
        self.stdout.write('Initializing notification settings...')

        NotificationSettings.initialize_defaults()

        count = NotificationSettings.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully initialized {count} notification setting(s)'
            )
        )

        # Display all settings
        self.stdout.write('\nCurrent notification settings:')
        for setting in NotificationSettings.objects.all():
            status = 'Enabled' if setting.is_enabled else 'Disabled'
            email = '✓' if setting.send_email else '✗'
            in_app = '✓' if setting.send_in_app else '✗'

            self.stdout.write(
                f"  - {setting.get_event_display()}: {status} "
                f"(Email: {email}, In-App: {in_app})"
            )
