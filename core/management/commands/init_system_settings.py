"""
Management command to initialize system settings.
Run during deployment or when settings need to be reset.
"""
from django.core.management.base import BaseCommand
from core.models import SystemSettings


class Command(BaseCommand):
    help = 'Initialize system settings with default values'

    def handle(self, *args, **kwargs):
        settings, created = SystemSettings.objects.get_or_create(pk=1)

        if created:
            self.stdout.write(self.style.SUCCESS('✅ System settings created with default values'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ System settings already exist'))

        self.stdout.write(f'   Site Name: {settings.site_name}')
        self.stdout.write(f'   Default Theme: {settings.default_theme}')
        self.stdout.write(f'   Theme Toggle: {"Enabled" if settings.allow_theme_toggle else "Disabled"}')
