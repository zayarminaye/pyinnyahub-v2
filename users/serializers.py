"""
Serializers for Users app.
Handles user registration, authentication, and profile management.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from .models import InstructorApplication

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer."""

    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'role',
            'phone_number', 'bio', 'profile_picture', 'date_of_birth',
            'expertise', 'years_of_experience', 'website', 'social_links',
            'date_joined', 'is_active'
        )
        read_only_fields = ('id', 'role', 'date_joined')


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'password2', 'first_name', 'last_name', 'phone_number')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords don't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', ''),
            role='student'  # Default role
        )

        # Send welcome email
        from notifications.services import NotificationService
        NotificationService.send_registration_confirmation(user)

        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                              email=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid email or password.')
            if not user.is_active:
                raise serializers.ValidationError('Account is deactivated.')
        else:
            raise serializers.ValidationError('Must include "email" and "password".')

        attrs['user'] = user
        return attrs


class InstructorApplicationSerializer(serializers.ModelSerializer):
    """Serializer for instructor applications."""
    user = UserSerializer(read_only=True)

    class Meta:
        model = InstructorApplication
        fields = (
            'id', 'user', 'experience', 'expertise', 'education', 'motivation',
            'resume', 'certificates', 'status', 'reviewed_by', 'reviewed_at',
            'rejection_reason', 'created_at'
        )
        read_only_fields = ('id', 'user', 'status', 'reviewed_by', 'reviewed_at', 'rejection_reason', 'created_at')


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change."""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Passwords don't match."})
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
