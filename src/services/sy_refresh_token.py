"""Refresh SY API token."""

# src/services/sy_refresh_token.py
from typing import Optional

# Import necessary components from the config and tools
from src.tools.sticker_api.dto_responses import LoginResponse
from src.tools.sticker_api.sy_api import sy_perform_login, API_ERROR_PREFIX
from config import SY_API_USERNAME, SY_API_PASSWORD


async def refresh_sy_token() -> tuple[Optional[str], Optional[str]]:
    """
    Attempts to fetch a new SY API token using credentials from environment variables.

    Returns:
        tuple[Optional[str], Optional[str]]: A tuple containing:
            - The new auth token (str) if successful, None otherwise.
            - The token expiration time in minutes (str) if successful, None otherwise.
    """
    print(".... Attempting to refresh SY API token ....")
    if not SY_API_USERNAME or not SY_API_PASSWORD:
        print(
            "Error: SY_API_USERNAME or SY_API_PASSWORD not set in environment variables."
        )
        return None, None  # Return None for both token and expiry

    try:
        # Call the imported login function
        result = await sy_perform_login(
            username=SY_API_USERNAME, password=SY_API_PASSWORD
        )

        if isinstance(result, LoginResponse):
            new_token = result.token
            expiry = result.expirationMinutes
            print(f"Successfully refreshed SY API token. Expires in: {expiry} minutes.")
            # Return the new token and expiry
            return new_token, expiry

        if isinstance(result, str) and result.startswith(API_ERROR_PREFIX):
            print(f"Error refreshing SY API token: {result}")
            return None, None

        print(f"Unexpected result type during token refresh: {type(result)}")
        return None, None

    except Exception as e:
        print(f"Exception during SY API token refresh: {e}")
        return None, None
