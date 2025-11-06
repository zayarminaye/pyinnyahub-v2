"""
Serializers for Payouts app.
"""
from rest_framework import serializers
from .models import Payout


class PayoutSerializer(serializers.ModelSerializer):
    """Serializer for payouts."""
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    processed_by_name = serializers.CharField(source='processed_by.get_full_name', read_only=True)

    class Meta:
        model = Payout
        fields = (
            'id', 'instructor', 'instructor_name', 'course', 'course_title',
            'payment', 'amount', 'commission', 'net_amount',
            'status', 'processed_by', 'processed_by_name', 'processed_at',
            'payment_method', 'transaction_id',
            'notes_to_instructor', 'created_at'
        )
        read_only_fields = (
            'instructor', 'course', 'payment', 'amount', 'commission',
            'net_amount', 'status', 'processed_by', 'processed_at'
        )
