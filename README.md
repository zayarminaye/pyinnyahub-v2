# Pyinnya Hub LMS

A comprehensive Learning Management System (LMS) built with Django, designed for Myanmar learners and instructors. Features manual payment processing, course approval workflows, subscription management, and instructor payouts.

## Features

### User Management
- **Three user roles**: Student, Instructor, Admin
- Email-based authentication with JWT tokens
- Instructor application and approval system
- Role-based access control (RBAC)

### Course Management
- Full course creation with sections and lessons
- Support for video, text, quiz, and assignment content
- Course approval workflow (Draft → Pending → Approved → Published)
- Categories, tags, and ratings
- Course wishlist functionality

### Payment & Enrollment
- Manual payment with receipt upload (images/PDFs)
- Admin review and approval of payments
- Course-level or global subscription access
- Access types: Monthly, Yearly, Lifetime
- Automatic subscription expiry tracking

### Instructor Features
- Create and manage courses
- Track student enrollments
- View earnings and payout history
- Course performance analytics

### Admin Dashboard
- Approve/reject instructor applications
- Review and approve payments
- Manage course publications
- Process instructor payouts
- Configure notification settings
- System analytics and reports

### Notifications
- Email notifications (Gmail SMTP/SendGrid)
- In-app notifications
- Admin-configurable notification channels
- Events: Registration, payments, course approvals, subscriptions, payouts

### Automation
- APScheduler for background tasks
- Automatic subscription expiry checks (daily)
- Expiry reminder emails (3 days before)
- Easy switch to Celery for scaling

## Tech Stack

- **Backend**: Django 4.2 + Django REST Framework
- **Database**: SQLite (MVP) / PostgreSQL (scalable)
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Email**: Gmail SMTP (free tier) / SendGrid
- **Storage**: Local filesystem / S3-compatible (scalable)
- **Scheduler**: APScheduler / Cron
- **Language**: Burmese (default)

## Project Structure

```
pyinnyahub-v2/
├── config/                 # Django settings
├── core/                   # Reusable base models and utilities
├── users/                  # Custom User model, auth, instructor applications
├── courses/                # Course, Section, Lesson, Category models
├── payments/               # Payment processing with receipt uploads
├── subscriptions/          # Subscription and access control
├── payouts/                # Instructor earnings and payouts
├── notifications/          # Email and in-app notifications
├── media/                  # Uploaded files
├── static/                 # Static assets
├── templates/              # Django templates
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

## Installation

### Prerequisites
- Python 3.9+
- pip
- virtualenv (recommended)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd pyinnyahub-v2
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Initialize notification settings**
   ```bash
   python manage.py init_notification_settings
   ```

7. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   - Main site: http://localhost:8000
   - Admin panel: http://localhost:8000/admin
   - API: http://localhost:8000/api/

## Configuration

### Environment Variables

Edit `.env` file with your settings:

```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite for MVP)
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=db.sqlite3

# Email (Gmail SMTP)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=Pyinnya Hub LMS <your-email@gmail.com>

# Site Settings
SITE_NAME=Pyinnya Hub LMS
SITE_URL=http://localhost:8000
SUPPORT_EMAIL=support@pyinnyahub.com

# File Upload
MAX_UPLOAD_SIZE=10485760  # 10MB
ALLOWED_RECEIPT_TYPES=image/jpeg,image/png,application/pdf

# Subscriptions
MONTHLY_DAYS=30
YEARLY_DAYS=365
EXPIRY_REMINDER_DAYS=3

# Feature Flags
ENABLE_REGISTRATION=True
ENABLE_INSTRUCTOR_APPLICATIONS=True
ENABLE_PAYMENT_UPLOADS=True

# Security
JWT_ACCESS_TOKEN_LIFETIME=60  # minutes
JWT_REFRESH_TOKEN_LIFETIME=1440  # minutes

# APScheduler
SCHEDULER_AUTOSTART=True
```

### Gmail SMTP Setup

1. Enable 2-factor authentication on your Google account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Use the generated password in `EMAIL_HOST_PASSWORD`

### SendGrid Setup (Optional)

```bash
EMAIL_HOST=smtp.sendgrid.net
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
```

## Management Commands

### Check Subscription Expiry
```bash
# Run manually
python manage.py check_subscription_expiry

# Dry run (no changes)
python manage.py check_subscription_expiry --dry-run
```

### Initialize Notification Settings
```bash
python manage.py init_notification_settings
```

### Create Sample Data (Development)
```bash
python manage.py loaddata fixtures/sample_data.json
```

## Automated Tasks (APScheduler)

The system automatically runs these tasks:

- **Daily at midnight**: Check subscription expiry and send reminders
- **Weekly on Monday**: Clean up old job execution logs

APScheduler starts automatically when Django server starts (if `SCHEDULER_AUTOSTART=True`).

### Alternative: Cron Jobs

If you prefer cron over APScheduler, disable auto-start and set up cron:

```bash
# Edit .env
SCHEDULER_AUTOSTART=False

# Add to crontab (crontab -e)
0 0 * * * /path/to/venv/bin/python /path/to/manage.py check_subscription_expiry
```

## API Documentation

### Authentication
```bash
# Register
POST /api/auth/register/
{
  "email": "user@example.com",
  "password": "YourSecurePassword123!",
  "first_name": "John",
  "last_name": "Doe"
}

# Login
POST /api/auth/login/
{
  "email": "user@example.com",
  "password": "YourSecurePassword123!"
}

# Returns: {access, refresh, user}
```

### Courses
```bash
# List published courses
GET /api/courses/

# Course detail
GET /api/courses/{id}/

# Enroll in course (student)
POST /api/payments/
{
  "course": 1,
  "amount": 50000,
  "access_type": "monthly",
  "receipt": <file>,
  "payment_method": "KBZPay"
}
```

### Instructor Dashboard
```bash
# Create course
POST /api/instructor/courses/

# Submit for review
POST /api/instructor/courses/{id}/submit/

# View earnings
GET /api/instructor/payouts/
```

### Admin Operations
```bash
# Approve payment
POST /api/admin/payments/{id}/approve/

# Reject payment
POST /api/admin/payments/{id}/reject/
{
  "reason": "Invalid receipt"
}

# Approve course
POST /api/admin/courses/{id}/approve/

# Process payout
POST /api/admin/payouts/{id}/mark_paid/
{
  "transaction_id": "TXN123",
  "payment_method": "Bank Transfer"
}
```

## Deployment

### Production Checklist

1. **Update settings**
   ```bash
   DEBUG=False
   SECRET_KEY=<strong-random-key>
   ALLOWED_HOSTS=yourdomain.com
   ```

2. **Switch to PostgreSQL**
   ```bash
   DATABASE_ENGINE=django.db.backends.postgresql
   DATABASE_NAME=pyinnyahub_db
   DATABASE_USER=dbuser
   DATABASE_PASSWORD=dbpassword
   DATABASE_HOST=localhost
   DATABASE_PORT=5432
   ```

3. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

4. **Set up web server** (Nginx + Gunicorn)
   ```bash
   pip install gunicorn
   gunicorn config.wsgi:application --bind 0.0.0.0:8000
   ```

5. **Configure storage** (S3/CloudFlare R2)
   ```bash
   pip install django-storages boto3
   # Configure in settings.py
   ```

6. **Set up monitoring** (Sentry, New Relic)

7. **Configure backups** (Database + Media files)

### Hosting Options (Free/Low-Cost)

- **PythonAnywhere**: Free tier available
- **Railway**: Free tier with PostgreSQL
- **Heroku**: Free dyno (limited hours)
- **DigitalOcean**: $5/month droplet
- **AWS Lightsail**: $3.50/month

## Scaling Recommendations

As your platform grows:

1. **Database**: SQLite → PostgreSQL
2. **Storage**: Local files → S3/CloudFlare R2
3. **Cache**: Add Redis
4. **Background jobs**: APScheduler → Celery + Redis
5. **Email**: Gmail SMTP → SendGrid Pro
6. **CDN**: CloudFlare for static assets
7. **Load balancer**: Multiple Django instances

## Admin Panel Access

Access Django admin at `/admin/`:

### Key Admin Features

- **User Management**: View/edit users, change roles
- **Course Approval**: Approve/reject course submissions
- **Payment Review**: Review payment receipts, approve/reject
- **Payout Processing**: Manage instructor payouts
- **Notification Settings**: Configure email/in-app notifications
- **System Settings**: Feature flags, site configuration

## Troubleshooting

### APScheduler not running

```bash
# Check logs
tail -f logs/django.log

# Verify setting
grep SCHEDULER_AUTOSTART .env
```

### Email not sending

```bash
# Test email configuration
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Message', 'from@example.com', ['to@example.com'])

# Check email logs
>>> from notifications.models import EmailLog
>>> EmailLog.objects.filter(status='failed')
```

### Database migration errors

```bash
# Reset migrations (development only!)
python manage.py migrate --fake-initial

# Or start fresh
rm db.sqlite3
python manage.py migrate
```

## Contributing

This is a private MVP project. For questions or issues, contact the development team.

## License

Proprietary - All rights reserved.

## Support

For technical support:
- Email: support@pyinnyahub.com
- Documentation: [Internal Wiki]
- Issues: [GitHub Issues]

---

**Built with ❤️ for Myanmar learners**
