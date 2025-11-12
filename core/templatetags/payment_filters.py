"""
Custom template filters for payment display formatting.
"""
from django import template

register = template.Library()


@register.filter
def format_payment_method(value):
    """
    Format payment method display names properly.

    Examples:
        kbz_pay -> KBZ Pay
        wave_money -> Wave Money
        aya_pay -> AYA Pay
        cb_pay -> CB Pay
        bank_transfer -> Bank Transfer
    """
    if not value:
        return "N/A"

    # Common payment method mappings
    payment_methods = {
        'kbz_pay': 'KBZ Pay',
        'kbzpay': 'KBZ Pay',
        'wave_money': 'Wave Money',
        'wavemoney': 'Wave Money',
        'wave': 'Wave Money',
        'aya_pay': 'AYA Pay',
        'ayapay': 'AYA Pay',
        'aya': 'AYA Pay',
        'cb_pay': 'CB Pay',
        'cbpay': 'CB Pay',
        'cb': 'CB Pay',
        'mpu': 'MPU',
        'visa': 'Visa',
        'mastercard': 'Mastercard',
        'bank_transfer': 'Bank Transfer',
        'banktransfer': 'Bank Transfer',
        'cash': 'Cash',
    }

    # Convert to lowercase for matching
    value_lower = value.lower().strip()

    # Check if it matches any known payment method
    if value_lower in payment_methods:
        return payment_methods[value_lower]

    # If not found, try to format nicely
    # Replace underscores and hyphens with spaces
    formatted = value.replace('_', ' ').replace('-', ' ')

    # Capitalize each word
    formatted = ' '.join(word.capitalize() for word in formatted.split())

    return formatted
