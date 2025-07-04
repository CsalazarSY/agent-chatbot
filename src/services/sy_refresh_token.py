"""Refresh SY API token."""

# src/services/sy_refresh_token.py

# Import necessary components from the config and tools
from pydantic import ValidationError
from src.tools.sticker_api.dtos.responses import LoginResponse
from src.tools.sticker_api.sy_api import sy_perform_login, API_ERROR_PREFIX
from src.services.logger_config import log_message

# Import config accessors/mutators
from config import SY_API_USERNAME, SY_API_PASSWORD, set_sy_api_token


async def refresh_sy_token() -> bool:
    """
    Attempts to fetch a new SY API token using credentials from environment variables
    and updates the token in the config module.

    Returns:
        bool: True if the token was successfully refreshed and updated, False otherwise.
    """
    log_message("Attempting to refresh SY API token", level=2, prefix="....")
    if not SY_API_USERNAME or not SY_API_PASSWORD:
        log_message(
            "SY_API_USERNAME or SY_API_PASSWORD not set in environment variables.",
            level=3,
            log_type="error",
        )
        set_sy_api_token(None)  # Ensure token is cleared in config
        return False

    try:
        # Call the imported login function
        result = await sy_perform_login(
            username=SY_API_USERNAME, password=SY_API_PASSWORD
        )

        # Check for error string first
        if isinstance(result, str) and result.startswith(API_ERROR_PREFIX):
            log_message(f"Error refreshing SY API token: {result}", level=3)
            set_sy_api_token(None)  # Ensure token is cleared in config
            return False

        # Check if the result is a dictionary (expected on success)
        if isinstance(result, dict):
            try:
                # Validate the dictionary against the Pydantic model
                login_response = LoginResponse.model_validate(result)
                # Access validated data
                new_token = login_response.token
                expiry = login_response.expirationMinutes
                log_message(
                    f"Successfully obtained SY API token. Expires in: {expiry} minutes."
                )
                # Update the token in config
                set_sy_api_token(new_token)
                return True  # Indicate success
            except ValidationError as e:
                log_message(
                    f"Error validating login response structure: {e}. Data: {result}",
                    level=3,
                    log_type="error",
                )
                set_sy_api_token(None)
                return False

        # Handle unexpected result types (not string error, not dict)
        log_message(
            f"Unexpected result type during token refresh: {type(result)}",
            level=3,
            log_type="error",
        )
        set_sy_api_token(None)  # Ensure token is cleared in config
        return False

    except Exception as e:
        log_message(f"Exception during SY API token refresh: {e}", level=3)
        set_sy_api_token(None)  # Ensure token is cleared in config
        return False
