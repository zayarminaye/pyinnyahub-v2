"""
Serializers for Subscriptions app.
"""
from rest_framework import serializers
from .models import Subscription


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for subscriptions."""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = (
            'id', 'user', 'user_name', 'course', 'course_title',
            'access_type', 'is_active', 'is_global',
            'starts_at', 'expires_at', 'days_remaining',
            'is_expired', 'created_at'
        )
        read_only_fields = ('user', 'is_active', 'starts_at', 'expires_at')

    def get_is_expired(self, obj):
        return obj.is_expired()
