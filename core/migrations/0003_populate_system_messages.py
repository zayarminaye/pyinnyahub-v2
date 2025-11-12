# Data migration to populate SystemMessage with common UI text

from django.db import migrations


def populate_messages(apps, schema_editor):
    """Populate SystemMessage with commonly used UI text."""
    SystemMessage = apps.get_model('core', 'SystemMessage')

    messages = [
        # Button Labels - Course Learning
        {
            'key': 'btn_start_learning',
            'category': 'button',
            'message_type': 'button',
            'message_burmese': 'သင်ခန်းစာ စတင်မည်',
            'message_english': 'Start Learning',
            'description': 'Button to start a course when student has not viewed any lessons yet',
        },
        {
            'key': 'btn_continue_learning',
            'category': 'button',
            'message_type': 'button',
            'message_burmese': 'ဆက်လက်လေ့လာမည်',
            'message_english': 'Continue Learning',
            'description': 'Button to continue learning when student has already started',
        },
        {
            'key': 'btn_mark_complete',
            'category': 'button',
            'message_type': 'button',
            'message_burmese': 'ပြီးပြီဟု မှတ်မည်',
            'message_english': 'Mark as Complete',
            'description': 'Button to mark a lesson as completed',
        },
        {
            'key': 'btn_completed',
            'category': 'button',
            'message_type': 'button',
            'message_burmese': 'ပြီးပြီ',
            'message_english': 'Completed',
            'description': 'Button label when lesson is already marked as complete',
        },
        {
            'key': 'btn_course_details',
            'category': 'button',
            'message_type': 'button',
            'message_burmese': 'အသေးစိတ်',
            'message_english': 'Details',
            'description': 'Button to view course details',
        },
        {
            'key': 'btn_review_course',
            'category': 'button',
            'message_type': 'button',
            'message_burmese': 'ပြန်ကြည့်မည်',
            'message_english': 'Review',
            'description': 'Button to review completed course',
        },
        {
            'key': 'btn_continue_watching',
            'category': 'button',
            'message_type': 'button',
            'message_burmese': 'ဆက်ကြည့်မည်',
            'message_english': 'Continue Watching',
            'description': 'Button to continue watching a lesson in progress',
        },

        # Labels - Course List
        {
            'key': 'label_all_courses',
            'category': 'label',
            'message_type': 'label',
            'message_burmese': 'သင်ခန်းစာများ',
            'message_english': 'Courses',
            'description': 'Label for courses heading',
        },
        {
            'key': 'label_my_courses',
            'category': 'label',
            'message_type': 'label',
            'message_burmese': 'ကျွန်ုပ်၏ သင်ခန်းစာများ',
            'message_english': 'My Courses',
            'description': 'Label for my courses page',
        },
        {
            'key': 'label_active_courses',
            'category': 'label',
            'message_type': 'label',
            'message_burmese': 'အသုံးပြုနိုင်သော သင်ခန်းစာများ',
            'message_english': 'Active Courses',
            'description': 'Label for active/enrolled courses section',
        },
        {
            'key': 'label_progress',
            'category': 'label',
            'message_type': 'label',
            'message_burmese': 'တိုးတက်မှု',
            'message_english': 'Progress',
            'description': 'Label for progress indicator',
        },
        {
            'key': 'label_lessons_completed',
            'category': 'label',
            'message_type': 'label',
            'message_burmese': 'သင်ခန်းပြီး',
            'message_english': 'lessons completed',
            'description': 'Label showing completed lessons count',
        },

        # Student Dashboard Labels
        {
            'key': 'label_student_dashboard',
            'category': 'label',
            'message_type': 'label',
            'message_burmese': 'Student Dashboard',
            'message_english': 'Student Dashboard',
            'description': 'Label for student dashboard page',
        },
        {
            'key': 'label_enrolled_courses',
            'category': 'label',
            'message_type': 'label',
            'message_burmese': 'စာရင်းသွင်းထားသော သင်ခန်းစာ စုစုပေါင်း',
            'message_english': 'Total Enrolled Courses',
            'description': 'Label for total enrolled courses count',
        },
        {
            'key': 'label_in_progress',
            'category': 'label',
            'message_type': 'label',
            'message_burmese': 'လေ့လာနေဆဲ',
            'message_english': 'In Progress',
            'description': 'Label for courses in progress',
        },
        {
            'key': 'label_completed',
            'category': 'label',
            'message_type': 'label',
            'message_burmese': 'ပြီးစီးပြီ',
            'message_english': 'Completed',
            'description': 'Label for completed courses',
        },
        {
            'key': 'label_learning_time',
            'category': 'label',
            'message_type': 'label',
            'message_burmese': 'လေ့လာချိန်',
            'message_english': 'Learning Time',
            'description': 'Label for total learning time',
        },
        {
            'key': 'label_recent_activity',
            'category': 'label',
            'message_type': 'label',
            'message_burmese': 'မကြာသေးမီ လေ့လာခဲ့သော သင်ခန်းစာများ',
            'message_english': 'Recent Activity',
            'description': 'Label for recent learning activity section',
        },

        # Notifications - Success Messages
        {
            'key': 'notif_lesson_completed',
            'category': 'notification',
            'message_type': 'success',
            'message_burmese': 'Lesson မှတ်သားပြီးပါပြီ! / Lesson marked as complete!',
            'message_english': 'Lesson marked as complete!',
            'description': 'Success notification when lesson is marked complete',
        },
        {
            'key': 'notif_payment_submitted',
            'category': 'notification',
            'message_type': 'success',
            'message_burmese': 'ငွေပေးချေမှု အောင်မြင်စွာ တင်သွင်းပြီးပါပြီ။ Admin မှ အတည်ပြုပေးမည်ဖြစ်ပါသည်။',
            'message_english': 'Payment submitted successfully. Admin will review it.',
            'description': 'Success notification after payment upload',
        },
        {
            'key': 'notif_payment_approved_msg',
            'category': 'notification',
            'message_type': 'success',
            'message_burmese': 'သင့်ငွေပေးချေမှု အောင်မြင်ပါသည်။ ယခု သင်ခန်းစာကို စတင်နိုင်ပါပြီ။',
            'message_english': 'Your payment was approved. You can now start the course.',
            'description': 'Success message on payment status page when approved',
        },

        # Notifications - Warning/Info Messages
        {
            'key': 'notif_already_enrolled_msg',
            'category': 'notification',
            'message_type': 'warning',
            'message_burmese': 'သင့်တွင် ဤသင်ခန်းစာ ရှိပြီးဖြစ်ပါသည်။',
            'message_english': 'You are already enrolled in this course.',
            'description': 'Warning when trying to enroll in already enrolled course',
        },
        {
            'key': 'notif_payment_pending_msg',
            'category': 'notification',
            'message_type': 'info',
            'message_burmese': 'သင့်ငွေပေးချေမှု စိစစ်နေဆဲဖြစ်ပါသည်။ ခဏစောင့်ဆိုင်းပေးပါ။',
            'message_english': 'Your payment is under review. Please wait.',
            'description': 'Info message when payment is pending approval',
        },

        # Empty States
        {
            'key': 'empty_no_courses',
            'category': 'general',
            'message_type': 'info',
            'message_burmese': 'သင်ခန်းစာ မရှိသေးပါ',
            'message_english': 'No courses yet',
            'description': 'Empty state when student has no enrolled courses',
        },
        {
            'key': 'empty_no_courses_msg',
            'category': 'general',
            'message_type': 'info',
            'message_burmese': 'သင့်တွင် စာရင်းသွင်းထားသော သင်ခန်းစာ မရှိသေးပါ။',
            'message_english': 'You have not enrolled in any courses yet.',
            'description': 'Empty state message for my courses page',
        },
        {
            'key': 'empty_no_lessons',
            'category': 'general',
            'message_type': 'info',
            'message_burmese': 'Select a lesson to start learning',
            'message_english': 'Select a lesson to start learning',
            'description': 'Empty state when no lesson is selected',
        },

        # Payment Method Display Names
        {
            'key': 'payment_kbz_pay',
            'category': 'payment',
            'message_type': 'label',
            'message_burmese': 'KBZ Pay',
            'message_english': 'KBZ Pay',
            'description': 'Display name for KBZ Pay payment method',
        },
        {
            'key': 'payment_wave_money',
            'category': 'payment',
            'message_type': 'label',
            'message_burmese': 'Wave Money',
            'message_english': 'Wave Money',
            'description': 'Display name for Wave Money payment method',
        },
        {
            'key': 'payment_aya_pay',
            'category': 'payment',
            'message_type': 'label',
            'message_burmese': 'AYA Pay',
            'message_english': 'AYA Pay',
            'description': 'Display name for AYA Pay payment method',
        },
        {
            'key': 'payment_cb_pay',
            'category': 'payment',
            'message_type': 'label',
            'message_burmese': 'CB Pay',
            'message_english': 'CB Pay',
            'description': 'Display name for CB Pay payment method',
        },
        {
            'key': 'payment_bank_transfer',
            'category': 'payment',
            'message_type': 'label',
            'message_burmese': 'Bank Transfer',
            'message_english': 'Bank Transfer',
            'description': 'Display name for Bank Transfer payment method',
        },

        # Preview Mode
        {
            'key': 'preview_mode_title',
            'category': 'general',
            'message_type': 'info',
            'message_burmese': 'Preview Mode',
            'message_english': 'Preview Mode',
            'description': 'Title for preview mode banner',
        },
        {
            'key': 'preview_mode_msg',
            'category': 'general',
            'message_type': 'info',
            'message_burmese': 'You are previewing this course as an instructor. Students will see this exact interface.',
            'message_english': 'You are previewing this course as an instructor. Students will see this exact interface.',
            'description': 'Message explaining preview mode',
        },
    ]

    # Create all messages
    for msg_data in messages:
        SystemMessage.objects.get_or_create(
            key=msg_data['key'],
            defaults=msg_data
        )


def reverse_migration(apps, schema_editor):
    """Remove all populated messages."""
    SystemMessage = apps.get_model('core', 'SystemMessage')
    SystemMessage.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_systemmessage'),
    ]

    operations = [
        migrations.RunPython(populate_messages, reverse_migration),
    ]
