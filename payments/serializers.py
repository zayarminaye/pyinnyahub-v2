"""
Serializers for Payments app.
"""
from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payments."""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.get_full_name', read_only=True)

    class Meta:
        model = Payment
        fields = (
            'id', 'user', 'user_name', 'course', 'course_title',
            'amount', 'access_type', 'receipt', 'transaction_id',
            'payment_method', 'notes', 'status', 'reviewed_by',
            'reviewed_by_name', 'reviewed_at', 'rejection_reason',
            'is_global', 'created_at'
        )
        read_only_fields = ('user', 'status', 'reviewed_by', 'reviewed_at', 'rejection_reason')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payments (file upload)."""

    class Meta:
        model = Payment
        fields = (
            'course', 'amount', 'access_type', 'receipt',
            'transaction_id', 'payment_method', 'notes', 'is_global'
        )

    def validate_receipt(self, value):
        """Validate receipt file size and type."""
        from django.conf import settings
        from core.utils import validate_file_size, validate_file_type

        max_size = settings.MAX_UPLOAD_SIZE
        allowed_types = settings.ALLOWED_RECEIPT_TYPES

        validate_file_size(value, max_size)
        validate_file_type(value, allowed_types)

        return value

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
