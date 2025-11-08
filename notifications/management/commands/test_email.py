"""
Management command to test email configuration.
Usage: python manage.py test_email recipient@example.com
"""
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = 'Test email configuration by sending a test email'

    def add_arguments(self, parser):
        parser.add_argument(
            'recipient',
            type=str,
            help='Email address to send test email to'
        )

    def handle(self, *args, **options):
        recipient = options['recipient']

        self.stdout.write(self.style.WARNING('Testing email configuration...'))
        self.stdout.write(f'From: {settings.DEFAULT_FROM_EMAIL}')
        self.stdout.write(f'To: {recipient}')
        self.stdout.write(f'SMTP Host: {settings.EMAIL_HOST}')
        self.stdout.write(f'SMTP Port: {settings.EMAIL_PORT}')
        self.stdout.write('')

        try:
            # Send test email
            send_mail(
                subject='Test Email from Pyinnya Hub LMS',
                message=f'''
                This is a test email from {settings.SITE_NAME}.

                If you received this email, your email configuration is working correctly!

                Configuration:
                - Email Backend: {settings.EMAIL_BACKEND}
                - SMTP Host: {settings.EMAIL_HOST}
                - SMTP Port: {settings.EMAIL_PORT}
                - From Email: {settings.DEFAULT_FROM_EMAIL}

                Best regards,
                {settings.SITE_NAME} Team
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )

            self.stdout.write(self.style.SUCCESS('✓ Test email sent successfully!'))
            self.stdout.write(self.style.SUCCESS(f'  Please check {recipient} for the test email.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Failed to send test email!'))
            self.stdout.write(self.style.ERROR(f'  Error: {str(e)}'))
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('Troubleshooting tips:'))
            self.stdout.write('  1. Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in your .env file')
            self.stdout.write('  2. For Gmail, use an "App Password" instead of your regular password')
            self.stdout.write('  3. Verify EMAIL_HOST and EMAIL_PORT are correct')
            self.stdout.write('  4. Check if EMAIL_USE_TLS is set correctly')
            self.stdout.write('')
            return

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Email configuration test completed!'))
