# Deployment Checklist for New Features

## After Pulling Latest Changes

### 1. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

This will create the `SystemMessage` model in the database.

### 2. Seed System Messages
```bash
python manage.py seed_messages
```

This populates the database with all default system messages that admins can edit.

**Output:**
```
Seeding system messages...
Created: file_upload_generic_error
Created: file_upload_too_large
Created: file_upload_invalid_type
...
Seeding complete! Created: 30, Updated: 0
```

### 3. Access Django Admin

1. Go to: `https://your-domain.com/admin/`
2. Look for **"System Messages"** under the **CORE** section
3. You'll see all 30+ editable messages

### 4. Customize Messages (Optional)

Edit any message to match your audience tone:

**Before (too formal):**
```
ကျေးဇူးပြု၍ သင်ခန်းစာ ဖန်တီးရန် အောက်ပါ form ကို ဖြည့်သွင်းပါ။
```

**After (natural):**
```
သင်ခန်းစာအသစ် ဖန်တီးဖို့ ဖောင်ဖြည့်ပါ။
```

## New Features Summary

### 1. Centralized File Storage Service

**Location:** `core/storage_service.py`

**Benefits:**
- Easy migration between Cloudinary ↔ AWS S3 ↔ Local
- Organized folder structure with environment separation
- Automatic image optimization
- Responsive image generation
- Graceful error handling

**Usage Example:**
```python
from core.storage_service import handle_file_upload, upload_course_thumbnail

success, file_path, url = handle_file_upload(
    upload_course_thumbnail,
    request.FILES['thumbnail'],
    course_id=course.id
)

if success:
    course.thumbnail = file_path
    course.save()
else:
    messages.error(request, file_path)  # Error message
```

**Migration Example:**
```env
# Switch from Cloudinary to S3 - just update .env
USE_CLOUDINARY=False
USE_S3=True
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_STORAGE_BUCKET_NAME=your_bucket
```

**Documentation:** `STORAGE_SERVICE_GUIDE.md`

### 2. Editable System Messages

**Location:** `core/models.py` (SystemMessage model)

**Benefits:**
- All messages editable via Django Admin
- No code changes needed to adjust tone
- Bilingual support (Burmese/English)
- Variable substitution
- Consistent messaging

**Usage Example:**
```python
from core.message_helper import show_message, get_message

# Show message to user
show_message(request, 'course_created_draft', course_title="Python 101")

# Get message for custom use
error_msg = get_message('file_upload_too_large', max_size=5)
```

**In Django Admin:**
1. Go to **System Messages**
2. Find message by key or category
3. Edit Burmese and English versions
4. Use variables like `{course_title}`, `{user_name}`
5. Save - changes take effect immediately (cached for 1 hour)

**Documentation:** `ADMIN_MESSAGE_CUSTOMIZATION_GUIDE.md`

### 3. Custom Instructor Portal

**Features:**
- Course dashboard with filtering
- 5-step creation wizard
- Course editing with rejection handling
- Curriculum manager with drag-drop
- Professional UI

**URLs:**
- Dashboard: `/courses/instructor/my-courses/`
- Create Course: `/courses/instructor/create/step1/`
- Curriculum Manager: `/courses/instructor/<id>/curriculum/`

### 4. Instructor Application with File Upload

**Improvements:**
- Uses new storage service
- Better error handling
- Organized file storage
- Validation with user-friendly messages

## Testing Checklist

### File Upload Testing

- [ ] Upload profile picture
- [ ] Upload course thumbnail (test: too large, wrong format, valid)
- [ ] Upload promo video
- [ ] Upload instructor resume
- [ ] Upload instructor certificates
- [ ] Verify files are in correct Cloudinary folders

### Message Customization Testing

- [ ] Edit a message in admin
- [ ] Trigger that message (e.g., upload a file)
- [ ] Verify edited message appears
- [ ] Test with variables (course title, user name)
- [ ] Test bilingual display

### Course Creation Testing

- [ ] Create course through wizard (all 5 steps)
- [ ] Save as draft
- [ ] Submit for review
- [ ] Edit rejected course
- [ ] Resubmit after rejection
- [ ] Verify curriculum manager drag-drop

## Environment Variables

Make sure these are set:

```env
# Storage Configuration
USE_CLOUDINARY=True  # or False for S3/local
CLOUDINARY_CLOUD_NAME=your_cloud
CLOUDINARY_API_KEY=your_key
CLOUDINARY_API_SECRET=your_secret

# Environment (affects file paths)
ENVIRONMENT=prod  # or dev/staging

# Optional: AWS S3 (if USE_CLOUDINARY=False)
USE_S3=True
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_STORAGE_BUCKET_NAME=your_bucket
AWS_S3_REGION_NAME=us-east-1
```

## Common Issues

### Issue: "Message not found: file_upload_success"

**Solution:** Run `python manage.py seed_messages`

### Issue: File upload fails silently

**Solution:**
1. Check Cloudinary credentials in `.env`
2. Check logs for detailed error
3. Verify file size and format

### Issue: Messages not updating

**Solution:** Clear cache or wait 1 hour for auto-refresh

```python
# In Django shell
from django.core.cache import cache
cache.clear()
```

### Issue: Drag-drop not working in curriculum manager

**Solution:**
1. Check browser console for JavaScript errors
2. Verify SortableJS CDN is loading
3. Clear browser cache

## Support

- **Storage Service Guide:** `STORAGE_SERVICE_GUIDE.md`
- **Message Customization Guide:** `ADMIN_MESSAGE_CUSTOMIZATION_GUIDE.md`
- **Logs:** Check Django logs for detailed errors
- **Admin Panel:** All configuration is in Django Admin

## Performance Notes

- **System Messages:** Cached for 1 hour to reduce database queries
- **File Storage:** Cloudinary provides CDN for fast delivery
- **Image Transformations:** Generated on-the-fly and cached by Cloudinary
- **Migrations:** Should take <1 minute

## Backup Recommendation

Before making bulk message changes:

```bash
# Backup messages
python manage.py dumpdata core.SystemMessage --indent 2 > messages_backup.json

# Restore if needed
python manage.py loaddata messages_backup.json
```
