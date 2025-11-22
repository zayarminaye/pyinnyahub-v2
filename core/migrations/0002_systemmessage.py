# Generated manually for SystemMessage model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SystemMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('key', models.CharField(db_index=True, help_text='Unique key to reference this message in code (e.g., "file_upload_success")', max_length=100, unique=True)),
                ('category', models.CharField(choices=[('auth', 'Authentication'), ('course', 'Course'), ('payment', 'Payment'), ('instructor', 'Instructor'), ('subscription', 'Subscription'), ('file_upload', 'File Upload'), ('general', 'General')], default='general', max_length=50)),
                ('message_type', models.CharField(choices=[('success', 'Success'), ('error', 'Error'), ('warning', 'Warning'), ('info', 'Info'), ('email', 'Email'), ('notification', 'Notification')], default='info', max_length=20)),
                ('message_burmese', models.TextField(blank=True, help_text='Message in Burmese (သဘာဝကျကျ ရေးပါ - not too formal or informal)')),
                ('message_english', models.TextField(blank=True, help_text='Message in English')),
                ('description', models.CharField(blank=True, help_text='Description of when this message is used', max_length=255)),
                ('variables', models.JSONField(blank=True, default=list, help_text='List of variable names (e.g., ["course_title", "user_name"])')),
                ('is_active', models.BooleanField(default=True)),
                ('admin_notes', models.TextField(blank=True, help_text='Internal notes for admins')),
            ],
            options={
                'verbose_name': 'System Message',
                'verbose_name_plural': 'System Messages',
                'ordering': ['category', 'key'],
                'db_table': 'system_messages',
            },
        ),
        migrations.AddIndex(
            model_name='systemmessage',
            index=models.Index(fields=['key', 'is_active'], name='core_sysmsg_key_active_idx'),
        ),
        migrations.AddIndex(
            model_name='systemmessage',
            index=models.Index(fields=['category'], name='core_sysmsg_category_idx'),
        ),
    ]
