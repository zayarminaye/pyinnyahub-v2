"""
Management command to check subscription expiry and send reminders.
Run this command via APScheduler or cron job daily.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from subscriptions.models import Subscription
from notifications.services import NotificationService


class Command(BaseCommand):
    help = 'Check for expired subscriptions and send expiry reminders'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Perform a dry run without making any changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))

        # Find expired subscriptions
        expired_subscriptions = Subscription.objects.expired()
        expired_count = expired_subscriptions.count()

        self.stdout.write(f"Found {expired_count} expired subscription(s)")

        for subscription in expired_subscriptions:
            self.stdout.write(f"  - Deactivating subscription for {subscription.user.email}")

            if not dry_run:
                subscription.deactivate()
                NotificationService.send_subscription_expired(subscription)

        # Find subscriptions expiring soon (within configured days)
        reminder_days = settings.EXPIRY_REMINDER_DAYS
        expiring_soon = Subscription.objects.expiring_soon(days=reminder_days)
        expiring_count = expiring_soon.count()

        self.stdout.write(f"\nFound {expiring_count} subscription(s) expiring within {reminder_days} day(s)")

        for subscription in expiring_soon:
            days_remaining = subscription.days_remaining or 0
            self.stdout.write(
                f"  - Sending reminder to {subscription.user.email} "
                f"({days_remaining} day(s) remaining)"
            )

            if not dry_run:
                NotificationService.send_subscription_expiry_reminder(subscription)

        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nSuccessfully processed {expired_count} expired '
                    f'and {expiring_count} expiring subscriptions'
                )
            )
        else:
            self.stdout.write(self.style.WARNING('\nDry run completed - no changes made'))
