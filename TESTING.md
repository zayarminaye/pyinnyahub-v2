# 🧪 Pyinnya Hub LMS - Testing Guide

Complete guide for testing all features of the LMS.

---

## 🚀 Quick Start

```bash
# 1. Start the server
cd /home/user/pyinnyahub-v2
python3 manage.py runserver

# 2. Open browser
# Visit: http://localhost:8000/
```

---

## 👤 Test Accounts

| Role | Email | Password | Purpose |
|------|-------|----------|---------|
| **Admin** | admin@pyinnyahub.com | admin123 | Full system access |
| **Instructor** | instructor@test.com | instructor123 | Create courses |
| **Student** | student@test.com | student123 | Enroll in courses |

---

## 📝 Testing Checklist

### ✅ **1. User Authentication**

#### Register New User
1. Go to http://localhost:8000/register/
2. Fill in the form:
   - First Name: `တက္ကသိုလ်`
   - Last Name: `ကျောင်းသား`
   - Email: `newuser@test.com`
   - Password: `password123`
   - Confirm Password: `password123`
3. Click **စာရင်းသွင်းမည်**
4. You should see success message
5. Check console for welcome email (if using console email backend)

**Expected Result**: ✅ User registered successfully

#### Login
1. Go to http://localhost:8000/login/
2. Enter credentials:
   - Email: `student@test.com`
   - Password: `student123`
3. Click **ဝင်မည်**
4. You should be redirected to dashboard

**Expected Result**: ✅ Logged in successfully

#### Logout
1. Click your name in navbar
2. Click **ထွက်မည်**
3. You should be logged out

**Expected Result**: ✅ Logged out successfully

---

### ✅ **2. Course Browsing**

#### View All Courses
1. Go to http://localhost:8000/courses/
2. You should see course list (empty if no courses)
3. Try search bar

**Expected Result**: ✅ Course list displays

#### Filter by Category
1. Click category badges (Programming, Business, etc.)
2. Courses should filter

**Expected Result**: ✅ Filtering works

#### Search Courses
1. Use search bar
2. Enter course name
3. Click search

**Expected Result**: ✅ Search works

---

### ✅ **3. Course Details**

1. Click any course card
2. You should see:
   - Course thumbnail
   - Title and description
   - Instructor info
   - Price and access type
   - Course sections and lessons
   - Enrollment button

**Expected Result**: ✅ Course details display correctly

---

### ✅ **4. User Profile**

#### View Profile
1. Login as any user
2. Click your name → **ပရိုဖိုင်**
3. You should see profile page

**Expected Result**: ✅ Profile displays

#### Update Profile
1. Change name or bio
2. Upload profile picture
3. Click **သိမ်းဆည်းမည်**
4. You should see success message

**Expected Result**: ✅ Profile updated successfully

---

### ✅ **5. Admin Panel**

#### Access Admin
1. Go to http://localhost:8000/admin/
2. Login with admin credentials
3. You should see Django admin

**Expected Result**: ✅ Admin panel accessible

#### Manage Users
1. Go to **Users**
2. View list of all users
3. Click any user to edit
4. Change role (student → instructor)
5. Save

**Expected Result**: ✅ User management works

#### Manage Categories
1. Go to **Categories**
2. Click **Add Category**
3. Fill in:
   - Name: `Web Development`
   - Slug: `web-development` (auto-filled)
   - Icon: `💻`
   - Is Active: ✓
4. Save

**Expected Result**: ✅ Category created

#### Manage Notification Settings
1. Go to **Notification Settings**
2. Click any setting
3. Toggle email/in-app
4. Save

**Expected Result**: ✅ Notification settings updated

---

### ✅ **6. REST API Testing**

#### Test Registration API

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "apiuser@test.com",
    "password": "password123",
    "password2": "password123",
    "first_name": "API",
    "last_name": "User"
  }'
```

**Expected Result**: ✅ User created via API

#### Test Login API

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@test.com",
    "password": "student123"
  }'
```

**Expected Result**: ✅ Receives JWT tokens

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "student@test.com",
    ...
  }
}
```

#### Test Protected Endpoint

```bash
# Get access token from login response
ACCESS_TOKEN="your-access-token-here"

curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

**Expected Result**: ✅ Profile data returned

---

### ✅ **7. Management Commands**

#### Test Subscription Expiry Check

```bash
python3 manage.py check_subscription_expiry --dry-run
```

**Expected Result**: ✅ Command runs without errors

```
DRY RUN MODE - No changes will be made
Found 0 expired subscription(s)
Found 0 subscription(s) expiring within 3 day(s)
```

#### Test Notification Settings Init

```bash
python3 manage.py init_notification_settings
```

**Expected Result**: ✅ 12 settings initialized

---

### ✅ **8. APScheduler**

#### Verify Scheduler Running

```bash
# Check logs when starting server
python3 manage.py runserver

# You should see:
# INFO scheduler Added job: Check Subscription Expiry (daily at midnight)
# INFO scheduler Added job: Delete Old Job Executions (weekly)
# INFO scheduler APScheduler started successfully
```

**Expected Result**: ✅ Scheduler starts automatically

---

## 🔍 Advanced Testing

### Test Email Notifications

#### Setup Console Backend (for testing)

In `.env`:
```bash
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

#### Test Registration Email

1. Register new user
2. Check console output
3. You should see email content

**Expected Result**: ✅ Email printed to console

#### Test Welcome Email via Code

```python
python3 manage.py shell

>>> from notifications.services import NotificationService
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(email='student@test.com')
>>> NotificationService.send_registration_confirmation(user)
```

**Expected Result**: ✅ Email sent

---

### Test Database Queries

```python
python3 manage.py shell

# Test user queries
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> User.objects.count()
3

>>> User.objects.students().count()
1

# Test course queries
>>> from courses.models import Course, Category
>>> Course.objects.published().count()
0

>>> Category.objects.filter(is_active=True).count()
5

# Test notification settings
>>> from notifications.models import NotificationSettings
>>> NotificationSettings.objects.count()
12
```

**Expected Result**: ✅ All queries work

---

## 🐛 Common Issues & Solutions

### Issue: Server won't start

```bash
# Check if port is in use
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different port
python3 manage.py runserver 8001
```

### Issue: Templates not found

```bash
# Check templates directory exists
ls templates/

# Check settings.py
# DIRS: [BASE_DIR / 'templates']
```

### Issue: Static files not loading

```bash
# Collect static files
python3 manage.py collectstatic

# Check settings
# STATIC_URL = '/static/'
# STATIC_ROOT = BASE_DIR / 'staticfiles'
```

### Issue: Database errors

```bash
# Reset database (dev only!)
rm db.sqlite3
python3 manage.py migrate
python3 create_test_data.py
```

---

## 📊 Performance Testing

### Test Page Load Times

```bash
# Install Apache Bench (optional)
ab -n 100 -c 10 http://localhost:8000/

# Or use curl
time curl http://localhost:8000/
```

### Test Database Queries

```python
# In Django shell
>>> from django.db import connection
>>> from django.test.utils import CaptureQueriesContext

>>> with CaptureQueriesContext(connection) as context:
...     Course.objects.published().count()
>>>
>>> len(context.captured_queries)
# Should be 1 query
```

---

## 🎯 Testing Workflow Example

### Complete User Journey

1. **Register** → Success message appears
2. **Login** → Redirected to dashboard
3. **Browse Courses** → See course list
4. **View Course** → See course details
5. **Update Profile** → Profile updated
6. **Logout** → Logged out

**Total Time**: ~5 minutes

**Expected Result**: ✅ All steps complete without errors

---

## ✅ Final Checklist

Before deployment, ensure:

- [ ] All tests pass
- [ ] No console errors in browser
- [ ] All links work
- [ ] Forms submit correctly
- [ ] Images load properly
- [ ] Responsive design works on mobile
- [ ] Database queries are optimized
- [ ] APScheduler is running
- [ ] Email notifications work
- [ ] Admin panel is accessible
- [ ] API endpoints return correct data

---

## 📱 Browser Testing

Test on multiple browsers:

- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari
- [ ] Edge
- [ ] Mobile browsers

---

## 🎉 Success Criteria

Your LMS is ready when:

✅ All test accounts work
✅ Pages load without errors
✅ Forms submit successfully
✅ Email notifications send
✅ Admin panel is functional
✅ API endpoints work
✅ Database queries are fast
✅ UI is responsive
✅ No security warnings

---

**🚀 Ready to deploy? See DEPLOYMENT.md for deployment guide!**
