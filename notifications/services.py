"""
Notification service for Pyinnya Hub LMS.
Centralized service for sending email and in-app notifications.
"""
import logging
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import Notification, EmailLog, NotificationSettings

logger = logging.getLogger('pyinnyahub')


class NotificationService:
    """
    Centralized service for handling all notifications.
    Sends both email and in-app notifications.
    """

    @staticmethod
    def _send_notification(event, user, notification_type, title, message,
                          email_subject=None, email_message=None,
                          related_object_type=None, related_object_id=None):
        """
        Unified method to send notifications respecting admin settings.

        Args:
            event: Event name from NotificationSettings.NOTIFICATION_EVENTS
            user: User object to receive notification
            notification_type: Type for in-app notification
            title: Title for in-app notification
            message: Message for in-app notification
            email_subject: Subject for email (if different from title)
            email_message: Body for email (if different from message)
            related_object_type: Optional related object type
            related_object_id: Optional related object ID
        """
        # Check if email should be sent
        if NotificationSettings.should_send_email(event):
            NotificationService._send_email(
                recipient=user.email,
                subject=email_subject or title,
                message=email_message or message,
                email_type=event,
                user=user
            )

        # Check if in-app notification should be sent
        if NotificationSettings.should_send_in_app(event):
            NotificationService._create_notification(
                user=user,
                notification_type=notification_type,
                title=title,
                message=message,
                related_object_type=related_object_type,
                related_object_id=related_object_id
            )

    @staticmethod
    def _send_email(recipient, subject, message, email_type=None, user=None):
        """
        Internal method to send email and log it.

        Args:
            recipient: Email address
            subject: Email subject
            message: Email body (plain text or HTML)
            email_type: Type of email for logging
            user: User object (optional)

        Returns:
            bool: True if sent successfully, False otherwise
        """
        # Create email log
        email_log = EmailLog.objects.create(
            recipient=recipient,
            subject=subject,
            body=message,
            email_type=email_type,
            user=user,
            status='pending'
        )

        try:
            # Send email
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )

            # Mark as sent
            email_log.mark_as_sent()
            logger.info(f"Email sent to {recipient}: {subject}")
            return True

        except Exception as e:
            # Mark as failed
            email_log.mark_as_failed(str(e))
            logger.error(f"Failed to send email to {recipient}: {str(e)}")
            return False

    @staticmethod
    def _create_notification(user, notification_type, title, message, related_object_type=None, related_object_id=None):
        """
        Internal method to create in-app notification.

        Args:
            user: User object
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            related_object_type: Type of related object (optional)
            related_object_id: ID of related object (optional)

        Returns:
            Notification: Created notification object
        """
        return Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            related_object_type=related_object_type,
            related_object_id=related_object_id
        )

    # ==========================================================================
    # REGISTRATION NOTIFICATIONS
    # ==========================================================================
    @classmethod
    def send_registration_confirmation(cls, user):
        """Send welcome email after successful registration."""
        email_subject = f"Welcome to {settings.SITE_NAME}!"
        email_message = f"""
        Dear {user.get_full_name()},

        Welcome to {settings.SITE_NAME}! Your account has been successfully created.

        Email: {user.email}
        Role: {user.get_role_display()}

        You can now log in and start exploring our courses.

        Best regards,
        {settings.SITE_NAME} Team
        """

        cls._send_notification(
            event='registration',
            user=user,
            notification_type='registration',
            title='Welcome to Pyinnya Hub!',
            message='Your account has been successfully created. Start exploring courses now!',
            email_subject=email_subject,
            email_message=email_message
        )

    # ==========================================================================
    # INSTRUCTOR APPLICATION NOTIFICATIONS
    # ==========================================================================
    @classmethod
    def send_instructor_application_approved(cls, user):
        """Notify user that their instructor application was approved."""
        email_subject = "Instructor Application Approved!"
        email_message = f"""
        Dear {user.get_full_name()},

        Congratulations! Your instructor application has been approved.

        You can now:
        - Create and manage courses
        - Track your students' progress
        - Earn from course enrollments

        Log in to start creating your first course!

        Best regards,
        {settings.SITE_NAME} Team
        """

        cls._send_notification(
            event='instructor_approved',
            user=user,
            notification_type='instructor_application',
            title='Instructor Application Approved!',
            message='Congratulations! You can now create and manage courses.',
            email_subject=email_subject,
            email_message=email_message
        )

    @classmethod
    def send_instructor_application_rejected(cls, user, reason):
        """Notify user that their instructor application was rejected."""
        email_subject = "Instructor Application Update"
        email_message = f"""
        Dear {user.get_full_name()},

        Thank you for your interest in becoming an instructor on {settings.SITE_NAME}.

        Unfortunately, we are unable to approve your application at this time.

        Reason: {reason}

        You can continue learning on our platform, and feel free to apply again in the future.

        Best regards,
        {settings.SITE_NAME} Team
        """

        cls._send_notification(
            event='instructor_rejected',
            user=user,
            notification_type='instructor_application',
            title='Instructor Application Update',
            message=f'Your application was not approved. Reason: {reason}',
            email_subject=email_subject,
            email_message=email_message
        )

    # ==========================================================================
    # PAYMENT NOTIFICATIONS
    # ==========================================================================
    @classmethod
    def send_payment_approved(cls, user, payment, subscription):
        """Notify user that their payment was approved and access granted."""
        course_name = payment.course.title if payment.course else 'All Courses (Global Subscription)'
        expiry_text = f"until {subscription.expires_at.strftime('%B %d, %Y')}" if subscription.expires_at else "forever (Lifetime)"

        email_subject = "Payment Approved - Access Granted!"
        email_message = f"""
        Dear {user.get_full_name()},

        Great news! Your payment has been approved.

        Course: {course_name}
        Amount: {payment.amount} MMK
        Access Type: {payment.get_access_type_display()}
        Access Valid: {expiry_text}

        You can now access the course content.

        Start learning now: {settings.SITE_URL}

        Best regards,
        {settings.SITE_NAME} Team
        """

        cls._send_notification(
            event='payment_approved',
            user=user,
            notification_type='payment',
            title='Payment Approved!',
            message=f'Your payment for {course_name} has been approved. Access granted!',
            email_subject=email_subject,
            email_message=email_message,
            related_object_type='payment',
            related_object_id=payment.id
        )

    @classmethod
    def send_payment_rejected(cls, user, payment, reason):
        """Notify user that their payment was rejected."""
        course_name = payment.course.title if payment.course else 'Global Subscription'

        email_subject = "Payment Review Result"
        email_message = f"""
        Dear {user.get_full_name()},

        Your payment submission for {course_name} has been reviewed.

        Unfortunately, we cannot approve this payment at this time.

        Reason: {reason}

        Please contact support at {settings.SUPPORT_EMAIL} if you have any questions.

        Best regards,
        {settings.SITE_NAME} Team
        """

        cls._send_notification(
            event='payment_rejected',
            user=user,
            notification_type='payment',
            title='Payment Not Approved',
            message=f'Your payment for {course_name} was not approved. Reason: {reason}',
            email_subject=email_subject,
            email_message=email_message,
            related_object_type='payment',
            related_object_id=payment.id
        )

    # ==========================================================================
    # COURSE NOTIFICATIONS
    # ==========================================================================
    @classmethod
    def send_course_approved(cls, course):
        """Notify instructor that their course was approved."""
        email_subject = f"Course Approved: {course.title}"
        email_message = f"""
        Dear {course.instructor.get_full_name()},

        Congratulations! Your course "{course.title}" has been approved.

        You can now publish it to make it visible to all students.

        Manage your course: {settings.SITE_URL}/instructor/courses/{course.id}/

        Best regards,
        {settings.SITE_NAME} Team
        """

        cls._send_notification(
            event='course_approved',
            user=course.instructor,
            notification_type='course',
            title='Course Approved!',
            message=f'Your course "{course.title}" has been approved.',
            email_subject=email_subject,
            email_message=email_message,
            related_object_type='course',
            related_object_id=course.id
        )

    @classmethod
    def send_course_rejected(cls, course, reason):
        """Notify instructor that their course was rejected."""
        email_subject = f"Course Review: {course.title}"
        email_message = f"""
        Dear {course.instructor.get_full_name()},

        Your course "{course.title}" has been reviewed.

        Unfortunately, it requires some changes before it can be approved.

        Feedback: {reason}

        Please make the necessary updates and resubmit for review.

        Edit your course: {settings.SITE_URL}/instructor/courses/{course.id}/edit/

        Best regards,
        {settings.SITE_NAME} Team
        """

        cls._send_notification(
            event='course_rejected',
            user=course.instructor,
            notification_type='course',
            title='Course Needs Updates',
            message=f'Your course "{course.title}" requires updates. Feedback: {reason}',
            email_subject=email_subject,
            email_message=email_message,
            related_object_type='course',
            related_object_id=course.id
        )

    # ==========================================================================
    # SUBSCRIPTION NOTIFICATIONS
    # ==========================================================================
    @classmethod
    def send_subscription_expiry_reminder(cls, subscription):
        """Send reminder email 3 days before subscription expires."""
        course_name = subscription.course.title if subscription.course else 'Global Subscription'
        days_remaining = subscription.days_remaining or 0

        email_subject = f"Your {course_name} Access Expires Soon"
        email_message = f"""
        Dear {subscription.user.get_full_name()},

        This is a reminder that your access to {course_name} will expire in {days_remaining} day(s).

        Expiry Date: {subscription.expires_at.strftime('%B %d, %Y')}

        To continue learning, please renew your subscription.

        Contact support: {settings.SUPPORT_EMAIL}

        Best regards,
        {settings.SITE_NAME} Team
        """

        cls._send_notification(
            event='subscription_expiry_reminder',
            user=subscription.user,
            notification_type='subscription',
            title='Subscription Expiring Soon',
            message=f'Your access to {course_name} expires in {days_remaining} day(s).',
            email_subject=email_subject,
            email_message=email_message,
            related_object_type='subscription',
            related_object_id=subscription.id
        )

    @classmethod
    def send_subscription_expired(cls, subscription):
        """Notify user that their subscription has expired."""
        course_name = subscription.course.title if subscription.course else 'Global Subscription'

        email_subject = f"Your {course_name} Access Has Expired"
        email_message = f"""
        Dear {subscription.user.get_full_name()},

        Your access to {course_name} has expired.

        To regain access, please purchase a new subscription.

        Contact support: {settings.SUPPORT_EMAIL}

        Best regards,
        {settings.SITE_NAME} Team
        """

        cls._send_notification(
            event='subscription_expired',
            user=subscription.user,
            notification_type='subscription',
            title='Subscription Expired',
            message=f'Your access to {course_name} has expired.',
            email_subject=email_subject,
            email_message=email_message,
            related_object_type='subscription',
            related_object_id=subscription.id
        )

    # ==========================================================================
    # PAYOUT NOTIFICATIONS
    # ==========================================================================
    @classmethod
    def send_payout_completed(cls, payout):
        """Notify instructor that payout has been completed."""
        email_subject = f"Payout Completed: {payout.net_amount} MMK"
        email_message = f"""
        Dear {payout.instructor.get_full_name()},

        Your payout has been processed successfully!

        Course: {payout.course.title}
        Amount: {payout.net_amount} MMK
        Transaction ID: {payout.transaction_id or 'N/A'}
        Payment Method: {payout.payment_method or 'N/A'}

        {payout.notes_to_instructor or ''}

        Thank you for being an instructor on {settings.SITE_NAME}!

        Best regards,
        {settings.SITE_NAME} Team
        """

        cls._send_notification(
            event='payout_completed',
            user=payout.instructor,
            notification_type='payout',
            title='Payout Completed!',
            message=f'Your payout of {payout.net_amount} MMK has been processed.',
            email_subject=email_subject,
            email_message=email_message,
            related_object_type='payout',
            related_object_id=payout.id
        )

    @classmethod
    def send_payout_cancelled(cls, payout, reason):
        """Notify instructor that payout was cancelled."""
        email_subject = f"Payout Update: {payout.course.title}"
        email_message = f"""
        Dear {payout.instructor.get_full_name()},

        Your payout for {payout.course.title} has been cancelled.

        Reason: {reason or 'Not specified'}

        If you have questions, please contact support at {settings.SUPPORT_EMAIL}

        Best regards,
        {settings.SITE_NAME} Team
        """

        cls._send_notification(
            event='payout_cancelled',
            user=payout.instructor,
            notification_type='payout',
            title='Payout Cancelled',
            message=f'Your payout for {payout.course.title} has been cancelled.',
            email_subject=email_subject,
            email_message=email_message,
            related_object_type='payout',
            related_object_id=payout.id
        )

    # ==========================================================================
    # PASSWORD RESET
    # ==========================================================================
    @classmethod
    def send_password_reset_email(cls, user, reset_link):
        """Send password reset email."""
        email_subject = "Password Reset Request"
        email_message = f"""
        Dear {user.get_full_name()},

        You requested to reset your password for {settings.SITE_NAME}.

        Click the link below to reset your password:
        {reset_link}

        This link will expire in 24 hours.

        If you didn't request this, please ignore this email.

        Best regards,
        {settings.SITE_NAME} Team
        """

        # Password reset only sends email, no in-app notification
        if NotificationSettings.should_send_email('password_reset'):
            cls._send_email(user.email, email_subject, email_message, email_type='password_reset', user=user)
