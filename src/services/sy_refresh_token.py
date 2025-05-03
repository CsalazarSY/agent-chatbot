"""Refresh SY API token."""

# src/services/sy_refresh_token.py

# Import necessary components from the config and tools
from src.tools.sticker_api.dto_responses import LoginResponse
from src.tools.sticker_api.sy_api import sy_perform_login, API_ERROR_PREFIX

# Import config accessors/mutators
from config import SY_API_USERNAME, SY_API_PASSWORD, set_sy_api_token


async def refresh_sy_token() -> bool:
    """
    Attempts to fetch a new SY API token using credentials from environment variables
    and updates the token in the config module.

    Returns:
        bool: True if the token was successfully refreshed and updated, False otherwise.
    """
    print(".... Attempting to refresh SY API token ....")
    if not SY_API_USERNAME or not SY_API_PASSWORD:
        print(
            "Error: SY_API_USERNAME or SY_API_PASSWORD not set in environment variables."
        )
        set_sy_api_token(None)  # Ensure token is cleared in config
        return False

    try:
        # Call the imported login function
        result = await sy_perform_login(
            username=SY_API_USERNAME, password=SY_API_PASSWORD
        )

        if isinstance(result, LoginResponse):
            new_token = result.token
            expiry = result.expirationMinutes
            print(f"Successfully obtained SY API token. Expires in: {expiry} minutes.")
            # Update the token in config
            set_sy_api_token(new_token)
            return True  # Indicate success

        if isinstance(result, str) and result.startswith(API_ERROR_PREFIX):
            print(f"Error refreshing SY API token: {result}")
            set_sy_api_token(None)  # Ensure token is cleared in config
            return False

        print(f"Unexpected result type during token refresh: {type(result)}")
        set_sy_api_token(None)  # Ensure token is cleared in config
        return False

    except Exception as e:
        print(f"Exception during SY API token refresh: {e}")
        set_sy_api_token(None)  # Ensure token is cleared in config
        return False
