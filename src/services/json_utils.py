"""
 Utils for JSON serialization, particularly for handling types that the default
 encoder doesn't know, like datetime objects.
"""

from datetime import date, datetime
from typing import Any


def json_serializer_default(o: Any) -> str:
    """
    A custom JSON serializer function to handle types that the default
    encoder doesn't know, like datetime objects.
    """
    if isinstance(o, (datetime, date)):
        return o.isoformat()
    raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")