# /src/services/time_service.py
from datetime import datetime
import pytz

from src.services.logger_config import log_message
from config import DEFAULT_TIMEZONE_CODE

def is_business_hours() -> bool:
    """
    Checks if the current time is within business hours (Mon-Fri, 9 AM - 5 PM ET).
    This is a placeholder for a potential external time API.
    """
    # Define the timezone from configuration
    timezone = pytz.timezone(DEFAULT_TIMEZONE_CODE)

    # Get the current time in that timezone
    now = datetime.now(timezone)

    # Check if it's a weekday (Monday=0, Sunday=6)
    is_weekday = now.weekday() < 5
    
    # Check if it's within 9 AM to 5 PM
    is_in_hours = 9 <= now.hour < 17
    
    return is_weekday and is_in_hours