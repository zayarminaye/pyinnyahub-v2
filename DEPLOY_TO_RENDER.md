# 🎨 Deploy Pyinnya Hub LMS to Render

**Complete step-by-step guide to deploy your Django LMS to Render (FREE tier available)**

---

## 📋 Prerequisites

- GitHub account
- Your code pushed to a GitHub repository
- 10 minutes of your time

---

## 🚀 Step-by-Step Deployment Guide

### **Step 1: Prepare Your Project Files**

#### 1.1 Install Required Packages

```bash
cd /home/user/pyinnyahub-v2

# Install production dependencies
pip install gunicorn psycopg2-binary dj-database-url whitenoise

# Update requirements.txt
pip freeze > requirements.txt
```

#### 1.2 Create `build.sh` File

This script runs during deployment to set up your app.

```bash
cat > build.sh << 'EOF'
#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🗂️  Collecting static files..."
python manage.py collectstatic --no-input

echo "🗄️  Running database migrations..."
python manage.py migrate

echo "📧 Initializing notification settings..."
python manage.py init_notification_settings

echo "✅ Build complete!"
EOF

# Make it executable
chmod +x build.sh
```

#### 1.3 Update `settings.py` for Production

Add this to your `config/settings.py`:

```python
import dj_database_url

# At the top, after imports
import os
from pathlib import Path

# WHITENOISE for static files (add after MIDDLEWARE)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this line
    'django.contrib.sessions.middleware.SessionMiddleware',
    # ... rest of your middleware
]

# Static files configuration (update these settings)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Database configuration (replace existing DATABASES)
if 'DATABASE_URL' in os.environ:
    # Production database (Render provides this)
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ['DATABASE_URL'],
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Development database
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
```

#### 1.4 Update `.gitignore`

Make sure these are in your `.gitignore`:

```bash
cat >> .gitignore << 'EOF'
staticfiles/
*.sqlite3
.env
db.sqlite3
media/
__pycache__/
*.pyc
EOF
```

#### 1.5 Commit and Push

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main  # or your branch name
```

---

### **Step 2: Create Render Account**

1. Go to https://render.com/
2. Click **"Get Started for Free"**
3. Sign up with your **GitHub** account (recommended)
4. Authorize Render to access your repositories

---

### **Step 3: Create PostgreSQL Database**

#### 3.1 Create Database

1. From Render Dashboard, click **"New +"** button (top right)
2. Select **"PostgreSQL"**
3. Fill in the details:
   - **Name**: `pyinnyahub-db` (or any name you prefer)
   - **Database**: `pyinnyahub`
   - **User**: `pyinnyahub_user`
   - **Region**: Choose closest to your users (e.g., Singapore, Frankfurt, Oregon)
   - **Plan**: **"Free"** (0.1 GB storage, good for testing)

4. Click **"Create Database"**

#### 3.2 Wait for Database Creation

- Wait 1-2 minutes for the database to be created
- Status will change from "Creating" to "Available"
- Keep this page open - you'll need the connection details

---

### **Step 4: Create Web Service**

#### 4.1 Create New Web Service

1. Click **"New +"** button again
2. Select **"Web Service"**
3. Choose **"Build and deploy from a Git repository"**
4. Click **"Next"**

#### 4.2 Connect Repository

1. If this is your first time:
   - Click **"Connect GitHub"**
   - Authorize Render
   - Grant access to your repositories

2. Find and select your **pyinnyahub-v2** repository
3. Click **"Connect"**

#### 4.3 Configure Web Service

Fill in these details:

- **Name**: `pyinnyahub-lms` (this will be your subdomain)
- **Region**: Same as your database (e.g., Singapore)
- **Branch**: `main` (or your branch name)
- **Root Directory**: (leave empty)
- **Runtime**: **Python 3**
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn config.wsgi:application`
- **Plan**: **"Free"** (512 MB RAM, good for testing)

---

### **Step 5: Add Environment Variables**

Scroll down to **"Environment Variables"** section and add these:

#### 5.1 Required Variables

Click **"Add Environment Variable"** for each:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | Click "Add from Database" → select your database → select "Internal Database URL" |
| `SECRET_KEY` | Click "Generate" (Render will auto-generate) |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `pyinnyahub-lms.onrender.com` (replace with your service name) |
| `PYTHON_VERSION` | `3.11.9` |

#### 5.2 Optional Variables (for email)

| Key | Value |
|-----|-------|
| `EMAIL_BACKEND` | `django.core.mail.backends.smtp.EmailBackend` |
| `EMAIL_HOST` | `smtp.gmail.com` |
| `EMAIL_PORT` | `587` |
| `EMAIL_USE_TLS` | `True` |
| `EMAIL_HOST_USER` | `your-email@gmail.com` |
| `EMAIL_HOST_PASSWORD` | `your-app-password` |
| `DEFAULT_FROM_EMAIL` | `noreply@pyinnyahub.com` |

**Note**: For Gmail, you need to use an [App Password](https://support.google.com/accounts/answer/185833), not your regular password.

---

### **Step 6: Deploy!**

1. Click **"Create Web Service"** at the bottom
2. Render will start building your app
3. You'll see the build logs in real-time

**Build process (3-5 minutes):**
- ⏳ Installing dependencies...
- ⏳ Collecting static files...
- ⏳ Running migrations...
- ⏳ Initializing settings...
- ✅ Build complete!
- ✅ Deploy live!

---

### **Step 7: Create Admin Account**

Once deployed, you need to create an admin user.

#### 7.1 Access Shell

1. In your Render web service dashboard
2. Click **"Shell"** tab (left sidebar)
3. Wait for shell to connect (may take 30 seconds)

#### 7.2 Create Superuser

In the shell, run:

```bash
python manage.py createsuperuser
```

Fill in:
- **Email**: `admin@pyinnyahub.com`
- **First name**: `Admin`
- **Last name**: `User`
- **Password**: [Your secure password]
- **Password (again)**: [Your secure password]

#### 7.3 Create Test Accounts (Optional)

```bash
python create_test_data.py
```

Then set passwords:

```bash
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
User = get_user_model()

student = User.objects.get(email='student@test.com')
student.set_password('YourSecurePassword123!')
student.save()

instructor = User.objects.get(email='instructor@test.com')
instructor.set_password('YourSecurePassword123!')
instructor.save()

exit()
```

---

### **Step 8: Test Your Deployment**

1. Your app is now live at: `https://pyinnyahub-lms.onrender.com` (replace with your service name)

2. Test these URLs:
   - **Homepage**: https://pyinnyahub-lms.onrender.com/
   - **Admin Panel**: https://pyinnyahub-lms.onrender.com/admin/
   - **Login**: https://pyinnyahub-lms.onrender.com/login/
   - **Courses**: https://pyinnyahub-lms.onrender.com/courses/

3. Login with your admin credentials
4. Go to Admin Dashboard
5. Check that everything works!

---

## 🔧 Common Issues & Solutions

### Issue 1: "DisallowedHost" Error

**Error**: `DisallowedHost at / Invalid HTTP_HOST header: 'pyinnyahub-lms.onrender.com'`

**Solution**:
1. Go to Render Dashboard → Your service → Environment
2. Update `ALLOWED_HOSTS` to include your domain:
   ```
   ALLOWED_HOSTS=pyinnyahub-lms.onrender.com,.onrender.com
   ```
3. Click **"Save Changes"** (app will auto-redeploy)

### Issue 2: Static Files Not Loading (CSS/JS missing)

**Error**: Homepage loads but no styling

**Solution**:
1. Make sure `whitenoise` is in `requirements.txt`
2. Check `STATICFILES_STORAGE` in settings.py:
   ```python
   STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
   ```
3. In Render Shell, run:
   ```bash
   python manage.py collectstatic --noinput
   ```
4. Redeploy (or wait for auto-deploy)

### Issue 3: Database Connection Error

**Error**: `FATAL: database "pyinnyahub" does not exist`

**Solution**:
1. Check that `DATABASE_URL` environment variable is set correctly
2. In Render Dashboard → Database → Info, copy **Internal Database URL**
3. Update environment variable with this URL
4. Redeploy

### Issue 4: "relation does not exist" Error

**Error**: `ProgrammingError: relation "users_user" does not exist`

**Solution**: Migrations didn't run. In Render Shell:
```bash
python manage.py migrate
```

### Issue 5: Build Fails with "Permission Denied"

**Error**: `build.sh: Permission denied`

**Solution**: Make build.sh executable locally:
```bash
chmod +x build.sh
git add build.sh
git commit -m "Make build.sh executable"
git push
```

---

## 📊 Monitoring Your App

### View Logs

1. Go to Render Dashboard → Your service
2. Click **"Logs"** tab
3. You can see real-time application logs

### Check Metrics

1. Click **"Metrics"** tab
2. View:
   - CPU usage
   - Memory usage
   - Request count
   - Response times

### Set Up Alerts

1. Go to **"Settings"** → **"Notifications"**
2. Add your email
3. Get notified when:
   - Deployments succeed/fail
   - Service goes down
   - High error rates

---

## 🎯 Next Steps

### 1. Custom Domain (Optional)

To use your own domain (e.g., www.pyinnyahub.com):

1. In Render Dashboard → Your service → Settings
2. Scroll to **"Custom Domain"**
3. Click **"Add Custom Domain"**
4. Enter your domain
5. Update your DNS settings (instructions provided by Render)
6. Render provides **free SSL certificate** automatically!

### 2. Upgrade to Paid Plan

Free tier limitations:
- ❌ Spins down after 15 minutes of inactivity (first request takes ~30 seconds)
- ❌ 512 MB RAM
- ❌ Shared CPU

Starter plan ($7/month):
- ✅ Always on (no spin down)
- ✅ 512 MB RAM
- ✅ Dedicated CPU

### 3. Enable Continuous Deployment

Already enabled by default! Every git push to your main branch automatically deploys.

To disable:
1. Settings → Build & Deploy
2. Toggle "Auto-Deploy" off

---

## 💰 Cost Summary

| Resource | Free Tier | Paid Plan |
|----------|-----------|-----------|
| **Web Service** | 750 hours/month<br>512 MB RAM<br>Spins down after 15 min | $7/month<br>Always on<br>512 MB - 8 GB RAM |
| **PostgreSQL** | 90 days free<br>256 MB RAM<br>1 GB storage | $7/month<br>256 MB - 64 GB RAM<br>10 GB - 512 GB storage |
| **Bandwidth** | 100 GB/month | Unlimited |
| **SSL** | ✅ Free | ✅ Free |
| **Custom Domain** | ✅ Free | ✅ Free |

**Total for Free Tier**: $0 (for 90 days, then database becomes paid)

---

## 🆘 Need Help?

- **Render Docs**: https://render.com/docs
- **Django Deployment Guide**: https://docs.djangoproject.com/en/4.2/howto/deployment/
- **Render Discord**: https://render.com/discord

---

## ✅ Deployment Checklist

- [ ] Installed gunicorn, psycopg2-binary, whitenoise, dj-database-url
- [ ] Created build.sh file
- [ ] Updated settings.py with production settings
- [ ] Committed and pushed to GitHub
- [ ] Created Render account
- [ ] Created PostgreSQL database
- [ ] Created web service
- [ ] Added environment variables
- [ ] Waited for deployment to complete
- [ ] Created superuser in shell
- [ ] Tested app URLs
- [ ] Verified static files load
- [ ] Changed all default passwords (SECURITY.md)
- [ ] Set up email configuration (optional)
- [ ] Configured custom domain (optional)

**🎉 Congratulations! Your LMS is now live on Render!**
