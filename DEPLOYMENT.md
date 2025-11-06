# 🚀 Pyinnya Hub LMS - Deployment Guide

Complete guide for deploying to free-tier hosting platforms.

---

## 📋 Table of Contents

1. [Testing Locally](#testing-locally)
2. [Free Hosting Options](#free-hosting-options)
3. [Deploy to PythonAnywhere (Recommended)](#deploy-to-pythonanywhere)
4. [Deploy to Railway](#deploy-to-railway)
5. [Deploy to Render](#deploy-to-render)
6. [Post-Deployment Checklist](#post-deployment-checklist)

---

## 🧪 Testing Locally

### 1. Start the Server

```bash
cd /home/user/pyinnyahub-v2
python3 manage.py runserver
```

### 2. Access the Application

- **Home Page**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/
- **Login**: http://localhost:8000/login/
- **Register**: http://localhost:8000/register/
- **Courses**: http://localhost:8000/courses/

### 3. Test Accounts

| Role | Email | Password |
|------|-------|----------|
| **Admin** | admin@pyinnyahub.com | admin123 |
| **Instructor** | instructor@test.com | instructor123 |
| **Student** | student@test.com | student123 |

### 4. Test Features

✅ **User Registration**
- Go to http://localhost:8000/register/
- Fill in the form
- Check for welcome email (console if using console backend)

✅ **User Login**
- Go to http://localhost:8000/login/
- Login with test accounts

✅ **Course Browsing**
- Browse courses at http://localhost:8000/courses/
- Filter by category
- Search courses

✅ **Profile Management**
- Update profile at http://localhost:8000/profile/
- Upload profile picture

✅ **Admin Panel**
- Access http://localhost:8000/admin/
- Manage users, courses, categories

---

## 🆓 Free Hosting Options

### Comparison Table

| Platform | Free Tier | Database | Storage | Best For |
|----------|-----------|----------|---------|----------|
| **PythonAnywhere** | Always Free | MySQL/PostgreSQL | 512MB | MVP/Testing |
| **Railway** | $5 credit/month | PostgreSQL | 1GB | Production-ready |
| **Render** | 750 hours/month | PostgreSQL | Limited | Small projects |
| **Heroku** | Discontinued | - | - | Not recommended |
| **DigitalOcean** | $200 credit (60 days) | All | Full | Scaling |

---

## 🐍 Deploy to PythonAnywhere (Recommended for MVP)

**FREE FOREVER**
Perfect for testing and MVP deployment.

### Step 1: Create Account

1. Go to https://www.pythonanywhere.com/
2. Sign up for **Beginner Account** (FREE)
3. Verify your email

### Step 2: Upload Code

**Option A: Using Git (Recommended)**

```bash
# In PythonAnywhere Bash console
git clone https://github.com/YOUR_USERNAME/pyinnyahub-v2.git
cd pyinnyahub-v2
```

**Option B: Upload Files**
- Use "Files" tab to upload your project folder

### Step 3: Setup Virtual Environment

```bash
# In Bash console
cd pyinnyahub-v2
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 4: Configure Settings

```bash
# Create .env file
nano .env

# Add these settings:
DEBUG=False
SECRET_KEY=your-super-secret-key-change-this
ALLOWED_HOSTS=YOUR_USERNAME.pythonanywhere.com

# Database
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=db.sqlite3

# Email (use console backend for testing)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Step 5: Setup Database

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py init_notification_settings
python create_test_data.py
python manage.py collectstatic --noinput
```

### Step 6: Configure Web App

1. Go to **Web** tab
2. Click **Add a new web app**
3. Choose **Manual configuration**
4. Select **Python 3.10**

**Configure WSGI file:**

```python
# /var/www/YOUR_USERNAME_pythonanywhere_com_wsgi.py

import os
import sys

# Add your project directory
path = '/home/YOUR_USERNAME/pyinnyahub-v2'
if path not in sys.path:
    sys.path.append(path)

# Set Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**Configure Virtual Environment:**
- Virtualenv: `/home/YOUR_USERNAME/pyinnyahub-v2/venv`

**Configure Static Files:**
- URL: `/static/`
- Directory: `/home/YOUR_USERNAME/pyinnyahub-v2/staticfiles`

- URL: `/media/`
- Directory: `/home/YOUR_USERNAME/pyinnyahub-v2/media`

### Step 7: Reload and Test

1. Click **Reload** button
2. Visit: https://YOUR_USERNAME.pythonanywhere.com/

**✅ Your app is live!**

---

## 🚂 Deploy to Railway

**$5 FREE CREDIT/MONTH**
Great for production-ready apps with PostgreSQL.

### Step 1: Prepare for Railway

```bash
# Add Procfile
echo "web: gunicorn config.wsgi --log-file -" > Procfile

# Add runtime.txt
echo "python-3.11.0" > runtime.txt

# Install gunicorn
pip install gunicorn
pip freeze > requirements.txt
```

### Step 2: Setup PostgreSQL Settings

Update `.env` for production:

```bash
# Database (Railway will provide these)
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_URL=${DATABASE_URL}  # Railway auto-provides this

# Security
DEBUG=False
SECRET_KEY=${SECRET_KEY}
ALLOWED_HOSTS=${RAILWAY_STATIC_URL}

# Static files
STATIC_ROOT=staticfiles
```

Update `settings.py` to use DATABASE_URL:

```python
import dj_database_url

# Add to settings.py
if 'DATABASE_URL' in os.environ:
    DATABASES['default'] = dj_database_url.config(
        default=os.environ['DATABASE_URL'],
        conn_max_age=600
    )
```

### Step 3: Deploy to Railway

1. Go to https://railway.app/
2. Sign up with GitHub
3. Click **New Project** → **Deploy from GitHub repo**
4. Select your repository
5. Railway auto-detects Django and deploys!

### Step 4: Add PostgreSQL

1. Click **+ New** → **Database** → **PostgreSQL**
2. Railway automatically sets `DATABASE_URL`

### Step 5: Set Environment Variables

In Railway dashboard, add:
- `SECRET_KEY`: Generate a new one
- `DEBUG`: False
- `ALLOWED_HOSTS`: Your Railway domain

### Step 6: Run Migrations

In Railway console:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py init_notification_settings
python manage.py collectstatic --noinput
```

**✅ Your app is live on Railway!**

---

## 🎨 Deploy to Render

**750 FREE HOURS/MONTH**

### Step 1: Prepare Files

```bash
# Create build.sh
cat > build.sh << 'EOF'
#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
EOF

chmod +x build.sh
```

### Step 2: Create render.yaml

```yaml
databases:
  - name: pyinnyahub-db
    databaseName: pyinnyahub
    user: pyinnyahub

services:
  - type: web
    name: pyinnyahub-web
    runtime: python
    buildCommand: "./build.sh"
    startCommand: "gunicorn config.wsgi:application"
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: pyinnyahub-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: DEBUG
        value: False
```

### Step 3: Deploy

1. Go to https://render.com/
2. Sign up with GitHub
3. Click **New** → **Blueprint**
4. Connect your repository
5. Render auto-deploys!

**✅ Your app is live on Render!**

---

## ✅ Post-Deployment Checklist

### Security

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set `DEBUG=False` in production
- [ ] Configure `ALLOWED_HOSTS` properly
- [ ] Use environment variables for sensitive data
- [ ] Enable HTTPS (most platforms provide free SSL)

### Database

- [ ] Run `python manage.py migrate`
- [ ] Create superuser
- [ ] Initialize notification settings
- [ ] Backup database regularly

### Email

- [ ] Configure real SMTP (Gmail/SendGrid)
- [ ] Test email notifications
- [ ] Set correct `DEFAULT_FROM_EMAIL`

### Static Files

- [ ] Run `collectstatic`
- [ ] Configure static file serving
- [ ] Test media uploads

### Monitoring

- [ ] Check application logs
- [ ] Monitor error rates
- [ ] Set up uptime monitoring (UptimeRobot - free)

---

## 🔧 Troubleshooting

### "DisallowedHost" Error

```python
# Add to settings.py
ALLOWED_HOSTS = ['your-domain.com', 'localhost', '127.0.0.1']
```

### Static Files Not Loading

```bash
# Run collectstatic
python manage.py collectstatic --noinput

# Check settings.py
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'
```

### Database Connection Error

```bash
# Check DATABASE_URL is set
echo $DATABASE_URL

# Test connection
python manage.py check --database default
```

### APScheduler Not Working

```bash
# Disable APScheduler in production if needed
# Set in .env:
SCHEDULER_AUTOSTART=False

# Use cron jobs instead
# Add to crontab:
0 0 * * * /path/to/python /path/to/manage.py check_subscription_expiry
```

---

## 📊 Cost Comparison (After Free Tier)

| Platform | Monthly Cost | Best For |
|----------|--------------|----------|
| PythonAnywhere | $5/month | Small MVPs |
| Railway | $5-10/month | Growing apps |
| Render | $7/month | Medium apps |
| DigitalOcean | $5/month | Full control |
| AWS/Azure | $10-50/month | Enterprise |

---

## 🎯 Recommended Path

1. **MVP/Testing**: PythonAnywhere (FREE forever)
2. **Early Users**: Railway ($5 credit/month)
3. **Growing**: Render or DigitalOcean
4. **Scale**: AWS/Azure with CDN

---

## 📱 Next Steps After Deployment

1. **Custom Domain**: Add your own domain (optional)
2. **SSL Certificate**: Enable HTTPS (usually free)
3. **CDN**: Use CloudFlare for static files (free)
4. **Backup**: Set up automatic database backups
5. **Monitoring**: Add Sentry for error tracking (free tier)
6. **Analytics**: Add Google Analytics (free)

---

## 🆘 Need Help?

- Check logs in your hosting platform
- Review Django error pages (if DEBUG=True in development)
- Check database connections
- Verify environment variables

---

**🎉 Congratulations! Your LMS is now deployed and ready for users!**

For questions or issues, check the main README.md or contact support.
