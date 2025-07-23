from django import template
from django.utils import timezone

register = template.Library()

@register.filter(name='currency')
def currency(value):
    """Format a number as currency"""
    try:
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return "$0.00"

@register.filter(name='format_time')
def format_time(value):
    """Format datetime to a readable string"""
    if not value:
        return ''
    try:
        now = timezone.now()
        diff = now - value
        
        if diff.days == 0:
            if diff.seconds < 3600:  # Less than an hour
                return 'Recently'
            return value.strftime('%I:%M %p')
        elif diff.days < 7:
            return value.strftime('%A')
        else:
            return value.strftime('%b %d')
    except:
        return str(value)