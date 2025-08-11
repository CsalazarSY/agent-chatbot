# /src/services/time_service.py
from datetime import datetime
import pytz

from src.services.logger_config import log_message

def is_business_hours() -> bool:
    """
    Checks if the current time is within business hours (Mon-Fri, 9 AM - 5 PM ET).
    This is a placeholder for a potential external time API.
    """
    # Define the timezone
    canada_timezone = pytz.timezone('Canada/Central')

    log_message(f"Current timezone is {canada_timezone}", level=1)

    # Get the current time in that timezone
    now = datetime.now(canada_timezone)

    log_message(f"Current time is {now}", level=2)

    # Check if it's a weekday (Monday=0, Sunday=6)
    is_weekday = now.weekday() < 5

    log_message(f"Current weekday status is {is_weekday} -> {now.weekday()}", level=2)

    
    # Check if it's within 9 AM to 5 PM
    is_in_hours = 9 <= now.hour < 17

    log_message(f"Current hour status is {is_in_hours} -> {now.hour}", level=2)
    
    return is_weekday and is_in_hours