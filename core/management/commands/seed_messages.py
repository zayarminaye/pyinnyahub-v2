"""
Management command to seed system messages into the database.
Run with: python manage.py seed_messages
"""
from django.core.management.base import BaseCommand
from core.models import SystemMessage


class Command(BaseCommand):
    help = 'Seed system messages into the database for admin editing'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding system messages...')

        messages_data = [
            # File Upload Messages
            {
                'key': 'file_upload_generic_error',
                'category': 'file_upload',
                'message_type': 'error',
                'description': 'Generic file upload error',
                'message_burmese': 'ဖိုင်တင်ရာတွင် အမှားအယွင်း ရှိပါသည်။ ကျေးဇူးပြု၍ ထပ်မံကြိုးစားပါ။',
                'message_english': 'Error uploading file. Please try again.',
                'variables': [],
            },
            {
                'key': 'file_upload_too_large',
                'category': 'file_upload',
                'message_type': 'error',
                'description': 'File size exceeds limit',
                'message_burmese': 'ဖိုင် အရွယ်အစား ကြီးလွန်းပါသည်။ အများဆုံး {max_size}MB ခွင့်ပြုပါသည်။',
                'message_english': 'File size too large. Maximum allowed is {max_size}MB.',
                'variables': ['max_size'],
            },
            {
                'key': 'file_upload_invalid_type',
                'category': 'file_upload',
                'message_type': 'error',
                'description': 'Invalid file type',
                'message_burmese': 'ဖိုင် အမျိုးအစား မှားယွင်းနေပါသည်။ ခွင့်ပြုထားသော အမျိုးအစားများ: {allowed_types}',
                'message_english': 'Invalid file type. Allowed types: {allowed_types}',
                'variables': ['allowed_types'],
            },
            {
                'key': 'file_upload_success',
                'category': 'file_upload',
                'message_type': 'success',
                'description': 'File uploaded successfully',
                'message_burmese': 'ဖိုင်ကို အောင်မြင်စွာ တင်ပြီးပါပြီ။',
                'message_english': 'File uploaded successfully.',
                'variables': [],
            },

            # Course Messages
            {
                'key': 'course_created_draft',
                'category': 'course',
                'message_type': 'success',
                'description': 'Course saved as draft',
                'message_burmese': 'သင်ခန်းစာ "{course_title}" ကို Draft အဖြစ် သိမ်းဆည်းပြီးပါပြီ။',
                'message_english': 'Course "{course_title}" saved as draft.',
                'variables': ['course_title'],
            },
            {
                'key': 'course_submitted_review',
                'category': 'course',
                'message_type': 'success',
                'description': 'Course submitted for admin review',
                'message_burmese': 'သင်ခန်းစာ "{course_title}" ကို Admin သုံးသပ်ရန် တင်သွင်းပြီးပါပြီ။',
                'message_english': 'Course "{course_title}" submitted for admin review.',
                'variables': ['course_title'],
            },
            {
                'key': 'course_approved',
                'category': 'course',
                'message_type': 'success',
                'description': 'Course approved by admin',
                'message_burmese': 'သင်ခန်းစာကို အတည်ပြုပြီးပါပြီ။ ယခု ထုတ်ဝေနိုင်ပါပြီ။',
                'message_english': 'Course has been approved. It is now published.',
                'variables': [],
            },
            {
                'key': 'course_rejected',
                'category': 'course',
                'message_type': 'error',
                'description': 'Course rejected by admin',
                'message_burmese': 'သင်ခန်းစာ ငြင်းပယ်ခံရပါသည်။ အကြောင်းရင်းကို ကြည့်ပြီး ပြင်ဆင်တင်သွင်းပါ။',
                'message_english': 'Course has been rejected. Please review the feedback and resubmit.',
                'variables': [],
            },
            {
                'key': 'course_updated',
                'category': 'course',
                'message_type': 'success',
                'description': 'Course updated successfully',
                'message_burmese': 'သင်ခန်းစာ "{course_title}" ကို အောင်မြင်စွာ ပြုပြင်ပြီးပါပြီ။',
                'message_english': 'Course "{course_title}" updated successfully.',
                'variables': ['course_title'],
            },
            {
                'key': 'course_deleted',
                'category': 'course',
                'message_type': 'success',
                'description': 'Course deleted',
                'message_burmese': 'သင်ခန်းစာ "{course_title}" ကို ဖျက်ပြီးပါပြီ။',
                'message_english': 'Course "{course_title}" deleted successfully.',
                'variables': ['course_title'],
            },

            # Instructor Application Messages
            {
                'key': 'instructor_application_submitted',
                'category': 'instructor',
                'message_type': 'success',
                'description': 'Instructor application submitted',
                'message_burmese': 'လျှောက်ထားမှု အောင်မြင်ပါသည်။ Admin မှ စိစစ်ပြီး အကြောင်းကြားပါမည်။',
                'message_english': 'Application submitted successfully. Admin will review and notify you.',
                'variables': [],
            },
            {
                'key': 'instructor_application_resubmitted',
                'category': 'instructor',
                'message_type': 'success',
                'description': 'Instructor application resubmitted after rejection',
                'message_burmese': 'လျှောက်ထားမှု ပြန်လည်တင်သွင်းပြီးပါပြီ။ Admin မှ ထပ်မံစိစစ်ပြီး အကြောင်းကြားပါမည်။',
                'message_english': 'Application resubmitted successfully. Admin will review again.',
                'variables': [],
            },
            {
                'key': 'instructor_application_approved',
                'category': 'instructor',
                'message_type': 'success',
                'description': 'Instructor application approved',
                'message_burmese': '{user_name} ကို ဆရာ/ဆရာမအဖြစ် အတည်ပြုပြီးပါပြီ။',
                'message_english': '{user_name} approved as instructor.',
                'variables': ['user_name'],
            },
            {
                'key': 'instructor_application_rejected',
                'category': 'instructor',
                'message_type': 'info',
                'description': 'Instructor application rejected notification',
                'message_burmese': 'ဆရာ/ဆရာမ လျှောက်ထားမှု ငြင်းပယ်ပြီးပါပြီ။',
                'message_english': 'Instructor application has been rejected.',
                'variables': [],
            },

            # Payment Messages
            {
                'key': 'payment_submitted',
                'category': 'payment',
                'message_type': 'success',
                'description': 'Payment submitted for review',
                'message_burmese': 'ငွေပေးချေမှု အောင်မြင်စွာ တင်သွင်းပြီးပါပြီ။ Admin မှ အတည်ပြုပေးမည်ဖြစ်ပါသည်။',
                'message_english': 'Payment submitted successfully. Admin will verify and approve.',
                'variables': [],
            },
            {
                'key': 'payment_approved',
                'category': 'payment',
                'message_type': 'success',
                'description': 'Payment approved',
                'message_burmese': 'ငွေပေးချေမှု အတည်ပြုပြီးပါပြီ။ သင်ခန်းစာကို စတင်နိုင်ပါပြီ။',
                'message_english': 'Payment approved. You can now start the course.',
                'variables': [],
            },
            {
                'key': 'payment_rejected',
                'category': 'payment',
                'message_type': 'error',
                'description': 'Payment rejected',
                'message_burmese': 'ငွေပေးချေမှု ငြင်းပယ်ခံရပါသည်။ ကျေးဇူးပြု၍ ပြန်လည်စစ်ဆေးပြီး ထပ်မံတင်သွင်းပေးပါ။',
                'message_english': 'Payment rejected. Please review and resubmit.',
                'variables': [],
            },

            # Authentication Messages
            {
                'key': 'login_success',
                'category': 'auth',
                'message_type': 'success',
                'description': 'Successful login',
                'message_burmese': 'ကြိုဆိုပါသည်၊ {user_name}!',
                'message_english': 'Welcome back, {user_name}!',
                'variables': ['user_name'],
            },
            {
                'key': 'logout_success',
                'category': 'auth',
                'message_type': 'info',
                'description': 'Successful logout',
                'message_burmese': 'လုံခြုံစွာ ထွက်ခွာပြီးပါပြီ။',
                'message_english': 'You have been logged out successfully.',
                'variables': [],
            },
            {
                'key': 'registration_success',
                'category': 'auth',
                'message_type': 'success',
                'description': 'Successful registration',
                'message_burmese': 'Pyinnya Hub မှ ကြိုဆိုပါသည်။ စာရင်းသွင်းမှု အောင်မြင်ပါသည်။',
                'message_english': 'Welcome to Pyinnya Hub! Registration successful.',
                'variables': [],
            },
            {
                'key': 'access_denied',
                'category': 'auth',
                'message_type': 'error',
                'description': 'Access denied',
                'message_burmese': 'ဝင်ခွင့်မရှိပါ။',
                'message_english': 'Access denied.',
                'variables': [],
            },

            # Subscription Messages
            {
                'key': 'subscription_enrolled',
                'category': 'subscription',
                'message_type': 'success',
                'description': 'Successfully enrolled in course',
                'message_burmese': 'သင်ခန်းစာတွင် အောင်မြင်စွာ စာရင်းသွင်းပြီးပါပြီ။',
                'message_english': 'Successfully enrolled in the course.',
                'variables': [],
            },
            {
                'key': 'subscription_already_enrolled',
                'category': 'subscription',
                'message_type': 'info',
                'description': 'Already enrolled in course',
                'message_burmese': 'သင့်တွင် ဤသင်ခန်းစာ ရှိပြီးဖြစ်ပါသည်။',
                'message_english': 'You are already enrolled in this course.',
                'variables': [],
            },

            # General Messages
            {
                'key': 'operation_success',
                'category': 'general',
                'message_type': 'success',
                'description': 'Generic success message',
                'message_burmese': 'လုပ်ဆောင်မှု အောင်မြင်ပါသည်။',
                'message_english': 'Operation successful.',
                'variables': [],
            },
            {
                'key': 'operation_error',
                'category': 'general',
                'message_type': 'error',
                'description': 'Generic error message',
                'message_burmese': 'အမှားအယွင်း ရှိပါသည်။ ကျေးဇူးပြု၍ ထပ်မံကြိုးစားပါ။',
                'message_english': 'An error occurred. Please try again.',
                'variables': [],
            },
            {
                'key': 'step_completed',
                'category': 'general',
                'message_type': 'success',
                'description': 'Wizard step completed',
                'message_burmese': 'Step {step_number} ပြီးဆုံးပါပြီ။ Step {next_step} သို့ ဆက်လက်လုပ်ဆောင်ပါ။',
                'message_english': 'Step {step_number} completed. Continue to Step {next_step}.',
                'variables': ['step_number', 'next_step'],
            },
        ]

        created_count = 0
        updated_count = 0

        for msg_data in messages_data:
            msg, created = SystemMessage.objects.update_or_create(
                key=msg_data['key'],
                defaults=msg_data
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created: {msg.key}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'Updated: {msg.key}'))

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSeeding complete! Created: {created_count}, Updated: {updated_count}'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                '\nAdmins can now edit these messages in Django Admin under "System Messages"'
            )
        )
