# File Storage Service Guide

## Overview

The centralized storage service (`core/storage_service.py`) provides organized, secure, and easily migratable file storage for Pyinnya Hub LMS.

## Features

✅ **Provider Abstraction**: Easy migration between Cloudinary, AWS S3, and local storage
✅ **Organized Structure**: Environment-specific folders (dev/staging/prod)
✅ **Public/Private Separation**: Security-first approach
✅ **Error Handling**: User-friendly Burmese/English error messages
✅ **Image Optimization**: Automatic resizing and format conversion
✅ **Responsive Images**: Multiple sizes for different devices
✅ **CDN Integration**: Cloudinary transformations for optimized delivery
✅ **Audit Logging**: All operations logged for troubleshooting

## File Organization

```
Storage Root
├── dev/                          # Development environment
│   ├── public/                   # Public files (no auth required)
│   │   ├── users/profiles/       # Profile pictures
│   │   └── courses/
│   │       ├── thumbnails/       # Course thumbnails
│   │       └── promo-videos/     # Promotional videos
│   └── private/                  # Private files (auth required)
│       ├── instructors/
│       │   ├── resumes/
│       │   └── certificates/
│       ├── lessons/
│       │   ├── videos/
│       │   ├── attachments/
│       │   └── text-files/
│       └── payments/receipts/
├── staging/                      # Staging environment (same structure)
└── prod/                         # Production (no prefix for clean URLs)
```

## Usage in Views

### Basic Upload

```python
from core.storage_service import handle_file_upload, upload_profile_picture
from django.contrib import messages

def update_profile_view(request):
    if request.method == 'POST':
        avatar = request.FILES.get('avatar')

        if avatar:
            success, result, url = handle_file_upload(
                upload_profile_picture,
                avatar
            )

            if success:
                # result is file_path
                request.user.profile_picture = result
                request.user.save()
                messages.success(request, 'Profile picture updated!')
            else:
                # result is error message
                messages.error(request, result)
```

### Upload with Additional Parameters

```python
from core.storage_service import handle_file_upload, upload_course_thumbnail

def course_create_view(request):
    thumbnail = request.FILES.get('thumbnail')

    if thumbnail:
        success, file_path, url = handle_file_upload(
            upload_course_thumbnail,
            thumbnail,
            course_id=course.id  # Additional parameter
        )
```

### Handling Multiple Files

```python
from core.storage_service import handle_file_upload, upload_instructor_resume, upload_instructor_certificates

# Resume
resume = request.FILES.get('resume')
if resume:
    success, path, url = handle_file_upload(
        upload_instructor_resume,
        resume,
        instructor_id=request.user.id
    )

# Certificates
certificates = request.FILES.get('certificates')
if certificates:
    success, path, url = handle_file_upload(
        upload_instructor_certificates,
        certificates,
        instructor_id=request.user.id
    )
```

## Available Upload Functions

| Function | Use Case | Max Size | Validation |
|----------|----------|----------|------------|
| `upload_profile_picture` | User avatars | 5MB | Image validation, size check |
| `upload_instructor_resume` | Instructor resumes | 5MB | PDF/DOC validation |
| `upload_instructor_certificates` | Instructor certificates | 10MB | PDF only |
| `upload_course_thumbnail` | Course thumbnails | 5MB | Image validation, min 800x450px |
| `upload_course_promo_video` | Course promo videos | 500MB | Video format validation |
| `upload_lesson_video` | Lesson videos | 500MB | Video format validation |
| `upload_lesson_attachment` | Lesson attachments | 50MB | Document validation |
| `upload_payment_receipt` | Payment receipts | 10MB | Image or PDF |

## Image Transformations (Cloudinary)

```python
from core.storage_service import storage_service

# Get thumbnail
thumbnail_url = storage_service.get_thumbnail_url(file_path, width=300, height=200)

# Get responsive sizes
sizes = storage_service.get_responsive_image_urls(file_path)
# Returns: {'thumbnail': url, 'small': url, 'medium': url, 'large': url, 'original': url}

# Custom transformation
custom_url = storage_service.get_file_url(file_path, {
    'width': 500,
    'height': 300,
    'crop': 'fill',
    'quality': 'auto',
    'fetch_format': 'auto'  # Auto WebP
})
```

## Error Handling

All upload functions return user-friendly bilingual error messages:

```python
success, result, url = handle_file_upload(upload_func, file)

if not success:
    # result contains user-friendly message like:
    # "ဖိုင် စစ်ဆေးမှု မအောင်မြင်ပါ။
    #  File validation failed: File size exceeds 5MB"
    messages.error(request, result)
```

## Migration Guide

### From Cloudinary to AWS S3

1. Update `.env`:
```env
USE_CLOUDINARY=False
USE_S3=True
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_STORAGE_BUCKET_NAME=your_bucket
```

2. No code changes needed! The storage service handles it automatically.

### From Local to Cloudinary

1. Update `.env`:
```env
USE_CLOUDINARY=True
CLOUDINARY_CLOUD_NAME=your_cloud
CLOUDINARY_API_KEY=your_key
CLOUDINARY_API_SECRET=your_secret
```

2. All existing file paths work seamlessly.

## Environment Setup

### Development
```env
ENVIRONMENT=dev
USE_CLOUDINARY=False  # Use local storage for dev
```

### Staging
```env
ENVIRONMENT=staging
USE_CLOUDINARY=True
CLOUDINARY_CLOUD_NAME=pyinnyahub-staging
```

### Production
```env
ENVIRONMENT=prod
USE_CLOUDINARY=True  # or USE_S3=True
CLOUDINARY_CLOUD_NAME=pyinnyahub
```

## Best Practices

1. **Always use handle_file_upload() in views** for automatic error handling
2. **Delete old files when updating** using `delete_file(old_path)`
3. **Use responsive images** for course thumbnails and profile pictures
4. **Set proper file size limits** to prevent abuse
5. **Use private categories** for sensitive content (resumes, receipts)
6. **Test error scenarios** (large files, wrong formats, network issues)

## Troubleshooting

### File upload fails silently
- Check logs: `logger.error` will show detailed errors
- Verify environment variables are set
- Check file size limits in settings

### Images not optimized
- Ensure Cloudinary is enabled for production
- Check transformation parameters
- Verify `fetch_format: auto` is set for WebP

### Migration issues
- Export file list before migration
- Use cloud provider sync tools (aws s3 sync, cloudinary auto-upload)
- Update database paths if needed

## Support

For issues or questions:
1. Check application logs
2. Review error messages (always bilingual)
3. Verify environment configuration
4. Test with small file first
