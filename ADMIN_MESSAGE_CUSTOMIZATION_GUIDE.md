# Admin Message Customization Guide

## Overview

All system messages and notifications in Pyinnya Hub LMS are editable through the Django Admin panel. This allows you to customize the tone, language, and style of messages to match your audience without touching any code.

## Why This Matters

Different audiences respond better to different message styles:
- **Formal Myanmar**: ကျေးဇူးပြု၍ စာရင်းသွင်းမှု ပြုလုပ်ပါ။
- **Natural Myanmar**: စာရင်းသွင်းလိုက်ပါ။
- **Too Casual**: ဝင်လိုက်ပါကွ။ ❌

You want messages that are:
✅ **Natural** (သဘာဝကျကျ)
✅ **Clear** (ရှင်းလင်းလွယ်ကူ)
✅ **Respectful but not stiff** (လေးစားစရာရှိသော်လည်း တင်းမာမှုမရှိ)
✅ **Consistent** (တသမတ်တည်း)

## How to Edit Messages

### Step 1: Access System Messages

1. Log in to Django Admin: `https://your-domain.com/admin/`
2. Click on **"System Messages"** under **CORE** section
3. You'll see a list of all editable messages

### Step 2: Find the Message to Edit

You can:
- **Browse by Category**: Auth, Course, Payment, etc.
- **Filter by Type**: Success, Error, Warning, Info
- **Search**: Use the search box to find specific messages

### Step 3: Edit the Message

Click on a message to edit. You'll see:

#### Message Identification
- **Key**: Unique identifier used in code (don't change this!)
- **Category**: Message category (for organization)
- **Message Type**: Success, Error, Warning, or Info
- **Is Active**: Enable/disable this message

#### Message Content
- **Message Burmese**: Edit the Burmese version
- **Message English**: Edit the English version

**Important**: Make sure both languages convey the same meaning!

#### Variables & Documentation
- **Variables**: List of placeholders you can use (e.g., `{course_title}`, `{user_name}`)
- **Description**: What this message is for
- **Admin Notes**: Your internal notes

### Step 4: Using Variables

Some messages use variables that get replaced with actual values:

**Example:**
```
Message Template: သင်ခန်းစာ "{course_title}" ကို {user_name} မှ ဖန်တီးပြီးပါပြီ။
Variables: ["course_title", "user_name"]

Actual Output: သင်ခန်းစာ "Python Programming" ကို John Doe မှ ဖန်တီးပြီးပါပြီ။
```

## Common Message Categories

### File Upload Messages

| Key | When Used | Current Burmese | Current English |
|-----|-----------|----------------|----------------|
| `file_upload_generic_error` | Any file upload fails | ဖိုင်တင်ရာတွင် အမှားအယွင်း ရှိပါသည်... | Error uploading file... |
| `file_upload_too_large` | File exceeds size limit | ဖိုင် အရွယ်အစား ကြီးလွန်းပါသည်... | File size too large... |
| `file_upload_invalid_type` | Wrong file format | ဖိုင် အမျိုးအစား မှားယွင်းနေပါသည်... | Invalid file type... |
| `file_upload_success` | File uploaded OK | ဖိုင်ကို အောင်မြင်စွာ တင်ပြီးပါပြီ။ | File uploaded successfully. |

### Course Messages

| Key | When Used |
|-----|-----------|
| `course_created_draft` | Course saved as draft |
| `course_submitted_review` | Course submitted for approval |
| `course_approved` | Admin approves course |
| `course_rejected` | Admin rejects course |
| `course_updated` | Course edited successfully |

### Instructor Messages

| Key | When Used |
|-----|-----------|
| `instructor_application_submitted` | New instructor application |
| `instructor_application_resubmitted` | Resubmitted after rejection |
| `instructor_application_approved` | Application approved |
| `instructor_application_rejected` | Application rejected |

### Payment Messages

| Key | When Used |
|-----|-----------|
| `payment_submitted` | Payment receipt uploaded |
| `payment_approved` | Payment verified |
| `payment_rejected` | Payment rejected |

## Best Practices

### 1. Maintain Consistent Tone

Pick a tone and stick to it throughout:

**❌ Inconsistent:**
- Success: ဖန်တီးပြီးပါပြီ။ (Casual)
- Error: ကျေးဇူးပြု၍ ပြန်လည်စစ်ဆေးပါ။ (Formal)

**✅ Consistent (Natural):**
- Success: ဖန်တီးပြီးပါပြီ။
- Error: ပြန်လည်စစ်ဆေးပြီး ထပ်မံကြိုးစားပါ။

### 2. Be Specific About Actions

**❌ Vague:**
```
အမှားရှိပါသည်။
(There is an error.)
```

**✅ Specific:**
```
ဖိုင် အရွယ်အစား ကြီးလွန်းပါသည်။ အများဆုံး 5MB ခွင့်ပြုပါသည်။
(File too large. Maximum 5MB allowed.)
```

### 3. Guide Users to Next Steps

**❌ Just stating the problem:**
```
ငွေပေးချေမှု ငြင်းပယ်ခံရပါသည်။
(Payment rejected.)
```

**✅ Stating problem + solution:**
```
ငွေပေးချေမှု ငြင်းပယ်ခံရပါသည်။ ကျေးဇူးပြု၍ ပြန်လည်စစ်ဆေးပြီး ထပ်မံတင်သွင်းပေးပါ။
(Payment rejected. Please review and resubmit.)
```

### 4. Test Your Changes

After editing messages:
1. Save the message
2. Go to the actual feature and trigger that message
3. Check if it sounds natural
4. Ask a native Burmese speaker if unsure

## Testing Message Variables

To test if variables work correctly:

1. Look at the **Variables** list
2. Check the code to see what actual values will be passed
3. Test with different scenarios

**Example:**
```
Message: သင်ခန်းစာ "{course_title}" ကို Admin သုံးသပ်ရန် တင်သွင်းပြီးပါပြီ။
Variables: ["course_title"]

Test Cases:
- Short title: "Python"
- Long title: "Complete Web Development with Django and React"
- Burmese title: "မြန်မာစာ သင်ခန်းစာ"
```

## Deactivating Messages

If you want to temporarily disable a message:
1. Edit the message
2. Uncheck **"Is Active"**
3. Save

The system will show a fallback message: `[Message not found: key_name]`

## Adding New Messages

To add a new custom message:
1. Click "Add System Message"
2. Fill in:
   - **Key**: Unique identifier (use lowercase with underscores)
   - **Category**: Choose appropriate category
   - **Message Type**: Success, Error, Warning, or Info
   - **Messages**: Both Burmese and English versions
3. Contact your developer to use this message in code

## Backup & Restore

**Important**: Always backup before making bulk changes!

```bash
# Export messages (run on server)
python manage.py dumpdata core.SystemMessage --indent 2 > messages_backup.json

# Restore messages
python manage.py loaddata messages_backup.json
```

## Common Scenarios

### Scenario 1: Message Too Formal

**Problem**: "ကျေးဇူးပြု၍ အောက်ပါ form ကို ဖြည့်သွင်းပါ။"

**Solution**: Make it natural: "ဖောင်ဖြည့်ပြီး တင်သွင်းပါ။"

### Scenario 2: Message Too Casual

**Problem**: "ဝင်လိုက်ပါကွ။"

**Solution**: More respectful: "အကောင့်ဝင်ရန် အောက်ပါ form ဖြည့်ပါ။"

### Scenario 3: Inconsistent Terminology

**Problem**: Sometimes "သင်ခန်းစာ", sometimes "Course"

**Solution**: Pick one and stick to it throughout all messages.

## Getting Help

If you're unsure about:
- **Tone**: Ask a native Burmese speaker to review
- **Variables**: Check the description field or ask a developer
- **Technical issues**: Check application logs

## Quick Reference: Message Keys

### Most Commonly Edited

1. `file_upload_generic_error` - General file upload error
2. `course_created_draft` - Course saved as draft
3. `course_submitted_review` - Course submitted for review
4. `payment_submitted` - Payment uploaded
5. `instructor_application_submitted` - Instructor application sent

### Rarely Changed

- Authentication messages (standard across platforms)
- System error messages (technical in nature)

---

**Remember**: Good messages make users feel confident and supported, not confused or frustrated!
