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
                ('key', models.CharField(db_index=True, help_text='Unique identifier for this message (e.g., "btn_start_learning")', max_length=100, unique=True)),
                ('category', models.CharField(choices=[('auth', 'Authentication'), ('course', 'Courses'), ('payment', 'Payments'), ('notification', 'Notifications'), ('button', 'Buttons'), ('menu', 'Menu'), ('email', 'Email'), ('general', 'General')], default='general', max_length=20)),
                ('message_type', models.CharField(choices=[('success', 'Success'), ('error', 'Error'), ('warning', 'Warning'), ('info', 'Info'), ('button', 'Button'), ('label', 'Label'), ('email', 'Email')], default='label', max_length=20)),
                ('message_burmese', models.TextField(help_text='Message in Burmese', verbose_name='Message (Burmese)')),
                ('message_english', models.TextField(blank=True, help_text='Message in English (optional)', verbose_name='Message (English)')),
                ('description', models.TextField(blank=True, help_text='Description of when/where this message is used')),
                ('variables', models.JSONField(blank=True, default=dict, help_text='Available variables for this message (e.g., {"user_name": "User\'s name"})')),
                ('is_active', models.BooleanField(default=True, help_text='Whether this message is currently active')),
            ],
            options={
                'verbose_name': 'System Message',
                'verbose_name_plural': 'System Messages',
                'ordering': ['category', 'key'],
            },
        ),
        migrations.AddIndex(
            model_name='systemmessage',
            index=models.Index(fields=['category', 'is_active'], name='core_system_categ_idx'),
        ),
    ]
