"""
APScheduler configuration for automatic subscription expiry checks.
This runs daily at midnight to check for expired subscriptions.
"""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util

logger = logging.getLogger('pyinnyahub')


def check_subscription_expiry_job():
    """
    Job function to check subscription expiry.
    This will be called by APScheduler.
    """
    from django.core.management import call_command

    try:
        logger.info("Running subscription expiry check job")
        call_command('check_subscription_expiry')
        logger.info("Subscription expiry check completed successfully")
    except Exception as e:
        logger.error(f"Error running subscription expiry check: {str(e)}")


@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """
    Delete old job executions (older than max_age seconds).
    Default: 1 week (604_800 seconds).
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


def start_scheduler():
    """
    Start the APScheduler background scheduler.
    Called when Django starts.
    """
    if not settings.SCHEDULER_AUTOSTART:
        logger.info("Scheduler autostart is disabled")
        return

    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    # Schedule subscription expiry check - runs daily at midnight
    scheduler.add_job(
        check_subscription_expiry_job,
        trigger=CronTrigger(hour=0, minute=0),  # Midnight every day
        id="check_subscription_expiry",
        max_instances=1,
        replace_existing=True,
        name="Check Subscription Expiry"
    )
    logger.info("Added job: Check Subscription Expiry (daily at midnight)")

    # Clean up old job executions weekly
    scheduler.add_job(
        delete_old_job_executions,
        trigger=CronTrigger(day_of_week="mon", hour=0, minute=0),  # Monday at midnight
        id="delete_old_job_executions",
        max_instances=1,
        replace_existing=True,
        name="Delete Old Job Executions"
    )
    logger.info("Added job: Delete Old Job Executions (weekly)")

    try:
        logger.info("Starting APScheduler...")
        scheduler.start()
        logger.info("APScheduler started successfully")
    except KeyboardInterrupt:
        logger.info("Stopping APScheduler...")
        scheduler.shutdown()
        logger.info("APScheduler shut down successfully")
