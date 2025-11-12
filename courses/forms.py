"""
Forms for instructor course creation and management.
"""
from django import forms
from django.utils.text import slugify
from .models import Course, Section, Lesson, Category


class CourseBasicInfoForm(forms.Form):
    """Step 1: Basic course information."""
    title = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'သင်ခန်းစာ ခေါင်းစဉ်'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    short_description = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'သင်ခန်းစာ အကျဉ်းချုပ် (500 စာလုံး)'
        })
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'သင်ခန်းစာ အသေးစိတ် ဖော်ပြချက်'
        })
    )


class CourseDetailsForm(forms.Form):
    """Step 2: Course details and learning outcomes."""
    level = forms.ChoiceField(
        choices=[
            ('beginner', 'အစပြု'),
            ('intermediate', 'အလယ်အလတ်'),
            ('advanced', 'အဆင့်မြင့်'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    language = forms.CharField(
        max_length=50,
        initial='Burmese',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    duration_hours = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'နာရီ'
        })
    )
    what_you_will_learn = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'တစ်ကြောင်းချင်းစီ ဝေးထားပါ\n- ပထမ သင်ခန်းစာ\n- ဒုတိယ သင်ခန်းစာ'
        }),
        help_text='တစ်ကြောင်းချင်းစီ သီးခြားဝေး ရေးပါ'
    )
    requirements = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'လိုအပ်ချက်များ (optional)\n- ကွန်ပျူတာ အခြေခံ\n- အင်တာနက် ချိတ်ဆက်မှု'
        }),
        help_text='တစ်ကြောင်းချင်းစီ သီးခြားဝေး ရေးပါ'
    )

    def clean_what_you_will_learn(self):
        """Convert text to JSON array."""
        text = self.cleaned_data['what_you_will_learn']
        lines = [line.strip('- ').strip() for line in text.split('\n') if line.strip()]
        return lines

    def clean_requirements(self):
        """Convert text to JSON array."""
        text = self.cleaned_data.get('requirements', '')
        if not text:
            return []
        lines = [line.strip('- ').strip() for line in text.split('\n') if line.strip()]
        return lines


class CourseMediaForm(forms.Form):
    """Step 3: Media upload."""
    thumbnail = forms.ImageField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        help_text='အနည်းဆုံး 800x450px, အများဆုံး 5MB'
    )
    promo_video = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'video/mp4,video/webm'
        }),
        help_text='MP4 သို့မဟုတ် WEBM, အများဆုံး 500MB (optional)'
    )


class CoursePricingForm(forms.Form):
    """Step 4: Pricing and access."""
    price = forms.DecimalField(
        min_value=0,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'ကျပ်'
        })
    )
    access_type = forms.ChoiceField(
        choices=[
            ('monthly', 'လစဉ်'),
            ('yearly', 'နှစ်စဉ်'),
            ('lifetime', 'တစ်သက်တာ'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class CourseEditForm(forms.ModelForm):
    """Combined form for editing existing courses."""

    class Meta:
        model = Course
        fields = [
            'title', 'slug', 'category', 'short_description', 'description',
            'level', 'language', 'duration_hours',
            'thumbnail', 'promo_video',
            'price', 'access_type'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'language': forms.TextInput(attrs={'class': 'form-control'}),
            'duration_hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'promo_video': forms.FileInput(attrs={'class': 'form-control', 'accept': 'video/*'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'access_type': forms.Select(attrs={'class': 'form-select'}),
        }

    # Custom fields for JSONField
    what_you_will_learn_text = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        help_text='တစ်ကြောင်းချင်းစီ သီးခြားဝေး ရေးပါ'
    )
    requirements_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        help_text='တစ်ကြောင်းချင်းစီ သီးခြားဝေး ရေးပါ'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Make file fields optional when editing (not changing them)
            self.fields['thumbnail'].required = False
            self.fields['promo_video'].required = False

            # Convert JSON arrays to text for display
            if self.instance.what_you_will_learn:
                self.fields['what_you_will_learn_text'].initial = '\n'.join(
                    f"- {item}" for item in self.instance.what_you_will_learn
                )
            if self.instance.requirements:
                self.fields['requirements_text'].initial = '\n'.join(
                    f"- {item}" for item in self.instance.requirements
                )

    def clean_what_you_will_learn_text(self):
        """Convert text to JSON array."""
        text = self.cleaned_data['what_you_will_learn_text']
        lines = [line.strip('- ').strip() for line in text.split('\n') if line.strip()]
        return lines

    def clean_requirements_text(self):
        """Convert text to JSON array."""
        text = self.cleaned_data.get('requirements_text', '')
        if not text:
            return []
        lines = [line.strip('- ').strip() for line in text.split('\n') if line.strip()]
        return lines

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.what_you_will_learn = self.cleaned_data['what_you_will_learn_text']
        instance.requirements = self.cleaned_data['requirements_text']

        if commit:
            instance.save()
            # Save many-to-many data (if any)
            self.save_m2m()
        return instance


class SectionForm(forms.ModelForm):
    """Form for creating/editing course sections."""

    class Meta:
        model = Section
        fields = ['title', 'description', 'order']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Section ခေါင်းစဉ်'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Section ဖော်ပြချက် (optional)'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
        }


class LessonForm(forms.ModelForm):
    """Form for creating/editing lessons."""

    class Meta:
        model = Lesson
        fields = [
            'title', 'content_type', 'description', 'order',
            'video_url', 'video_file', 'text_content',
            'duration_minutes', 'is_preview',
            'allow_video_download', 'allow_attachment_download'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Lesson ခေါင်းစဉ်'
            }),
            'content_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Lesson ဖော်ပြချက်'
            }),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'video_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://www.youtube.com/watch?v=...'
            }),
            'video_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'video/*'
            }),
            'text_content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'မိနစ်'
            }),
            'is_preview': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'allow_video_download': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'allow_attachment_download': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields conditionally required based on content_type
        self.fields['video_url'].required = False
        self.fields['video_file'].required = False
        self.fields['text_content'].required = False
