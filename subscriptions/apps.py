from django.apps import AppConfig
import sys


class SubscriptionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "subscriptions"

    def ready(self):
        """
        Start the APScheduler when Django starts.
        This will run subscription expiry checks automatically.

        IMPORTANT: Only start scheduler when running the actual server,
        not during management commands (migrate, collectstatic, etc.)
        """
        # Don't start scheduler during management commands
        if len(sys.argv) > 1 and sys.argv[1] in [
            'migrate', 'makemigrations', 'collectstatic',
            'createsuperuser', 'shell', 'test', 'check',
            'showmigrations', 'sqlmigrate', 'dbshell'
        ]:
            return

        # Start scheduler for production server
        from . import scheduler
        scheduler.start_scheduler()
