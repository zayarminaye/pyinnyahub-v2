from django.apps import AppConfig


class SubscriptionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "subscriptions"

    def ready(self):
        """
        Start the APScheduler when Django starts.
        This will run subscription expiry checks automatically.
        """
        from . import scheduler
        scheduler.start_scheduler()
