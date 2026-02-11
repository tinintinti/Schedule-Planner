
from datetime import datetime


def format_date(date_obj):
    """Format a date object to readable string"""
    if not date_obj:
        return ""
    try:
        if isinstance(date_obj, str):
            date_obj = datetime.strptime(date_obj, '%Y-%m-%d')
        return date_obj.strftime('%B %d, %Y')
    except:
        return str(date_obj)


def format_time(time_str):
    """Format time string to 12-hour format"""
    if not time_str:
        return ""
    try:
        time_obj = datetime.strptime(time_str, '%H:%M')
        return time_obj.strftime('%I:%M %p')
    except:
        return str(time_str)