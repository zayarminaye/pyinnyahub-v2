# 🔒 Security Guidelines

## Critical Security Actions Required

### 1. Change All Default Passwords Immediately

**⚠️ CRITICAL**: Test accounts were created during development. You MUST change all passwords before deploying or sharing this codebase.

```bash
python3 manage.py shell
```

Then run:

```python
from django.contrib.auth import get_user_model
User = get_user_model()

# Change admin password
admin = User.objects.get(email='admin@pyinnyahub.com')
admin.set_password('YOUR_VERY_SECURE_ADMIN_PASSWORD_HERE')
admin.save()

# Change instructor password
instructor = User.objects.get(email='instructor@test.com')
instructor.set_password('YOUR_VERY_SECURE_INSTRUCTOR_PASSWORD_HERE')
instructor.save()

# Change student password
student = User.objects.get(email='student@test.com')
student.set_password('YOUR_VERY_SECURE_STUDENT_PASSWORD_HERE')
student.save()

print("✅ All passwords changed successfully!")
```

### 2. Update Environment Variables

Before deploying to production, ensure you have changed:

```bash
# .env file
SECRET_KEY=[Generate new secret key - DO NOT use the default]
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database credentials (if using PostgreSQL)
DB_PASSWORD=[Your secure database password]

# Email settings
EMAIL_HOST_PASSWORD=[Your email service password]
```

To generate a new SECRET_KEY:

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### 3. Security Checklist Before Deployment

- [ ] Changed all test account passwords
- [ ] Generated new SECRET_KEY
- [ ] Set DEBUG=False in production
- [ ] Configured ALLOWED_HOSTS correctly
- [ ] Using HTTPS (SSL/TLS certificates)
- [ ] Configured CSRF and CORS settings
- [ ] Set up database backups
- [ ] Reviewed file upload permissions
- [ ] Configured proper firewall rules
- [ ] Enabled rate limiting (if applicable)
- [ ] Set up logging and monitoring
- [ ] Reviewed all environment variables

### 4. Git History Note

**⚠️ WARNING**: Earlier commits in this repository may contain default passwords in documentation files. If you plan to make this repository public, consider:

1. **Option 1 (Recommended for new repos)**: Start fresh repository without sensitive history
2. **Option 2**: Use git-filter-repo or BFG Repo-Cleaner to remove sensitive data from git history
3. **Option 3**: Keep repository private and never make it public

### 5. Production Security Best Practices

#### Django Settings
- Always use `DEBUG=False` in production
- Use strong `SECRET_KEY` (never commit to git)
- Configure `ALLOWED_HOSTS` properly
- Enable HTTPS redirect: `SECURE_SSL_REDIRECT=True`
- Set secure cookie flags: `SESSION_COOKIE_SECURE=True`, `CSRF_COOKIE_SECURE=True`

#### File Uploads
- Validate file types and sizes
- Use virus scanning for uploaded files (ClamAV)
- Store media files separately (use S3 or similar)
- Never serve user-uploaded files directly

#### Database
- Use strong database passwords
- Restrict database access to application server only
- Regular backups with encryption
- Use connection pooling

#### Authentication
- Enforce strong password policies
- Implement rate limiting for login attempts
- Use 2FA for admin accounts (django-otp)
- Set up session timeout

#### Monitoring
- Enable Django security logging
- Monitor for suspicious activity
- Set up alerts for critical errors
- Regular security audits

## Reporting Security Issues

If you discover a security vulnerability in this application, please email: security@pyinnyahub.com

**DO NOT** create public GitHub issues for security vulnerabilities.

## Resources

- [Django Security Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Security Best Practices](https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/web_application_security)
