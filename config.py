''' Central config file to handle env vars'''
# pylint: disable=W0603:global-statement
# /src/config.py
import os
from dotenv import load_dotenv
from hubspot import HubSpot

from src.services.sy_refresh_token import refresh_sy_token

# Load environment variables from .env file
load_dotenv()

# --- API Configuration ---
API_BASE_URL = os.getenv("API_BASE_URL")
API_VERSION = os.getenv("API_VERSION", "v1") # Default to v1 if not set

# --- SY API Credentials for Dynamic Token ---
SY_API_USERNAME = os.getenv("SY_API_USERNAME")
SY_API_PASSWORD = os.getenv("SY_API_PASSWORD")
# Internal variable for dynamic token (Use UPPER_SNAKE_CASE for module-level state)
_SY_API_AUTH_TOKEN: str | None = None

# --- Centralized Token Refresh Trigger ---
# Import the service function *inside* the trigger function to avoid circular imports at module level
async def trigger_sy_token_refresh() -> bool:
    """Calls the refresh service and updates the internal dynamic token in this module.

    Returns:
        bool: True if token was successfully obtained and updated, False otherwise.
    """
    global _SY_API_AUTH_TOKEN # Need to modify the module-level variable
    try:
        print("...Config attempting SY token refresh...")
        new_token, expiry = await refresh_sy_token()
        if new_token:
            _SY_API_AUTH_TOKEN = new_token # Update internal variable
            print(f"--- Config updated SY token successfully. Expires in: {expiry} min. ---")
            return True
        else:
            _SY_API_AUTH_TOKEN = None # Ensure it's cleared on failure
            print("--- Config failed to update SY token. --- ")
            return False
    except ImportError:
        print("!!! ERROR: Could not import refresh_sy_token service in config trigger. Check path.")
        _SY_API_AUTH_TOKEN = None
        return False
    except Exception as e:
        print(f"!!! EXCEPTION in trigger_sy_token_refresh: {e}")
        _SY_API_AUTH_TOKEN = None # Ensure cleared on exception
        return False

# --- Token Accessor ---
def get_sy_api_token() -> str | None:
    """Returns the current dynamic StickerYou API token."""
    return _SY_API_AUTH_TOKEN

DEFAULT_COUNTRY_CODE = os.getenv("DEFAULT_COUNTRY_CODE", "US")
DEFAULT_CURRENCY_CODE = os.getenv("DEFAULT_CURRENCY_CODE", "USD")

# --- LLM Configuration ---
LLM_BASE_URL = os.getenv("LLM_BASE_URL")
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME")
LLM_MODEL_FAMILY = os.getenv("LLM_MODEL_FAMILY")

# --- HubSpot Configuration ---
HUBSPOT_API_TOKEN = os.getenv("HUBSPOT_API_TOKEN")
HUBSPOT_DEFAULT_SENDER_ACTOR_ID = os.getenv("HUBSPOT_DEFAULT_SENDER_ACTOR_ID")
HUBSPOT_DEFAULT_CHANNEL = os.getenv("HUBSPOT_DEFAULT_CHANNEL")
HUBSPOT_DEFAULT_CHANNEL_ACCOUNT = os.getenv("HUBSPOT_DEFAULT_CHANNEL_ACCOUNT")
HUBSPOT_DEFAULT_INBOX = os.getenv("HUBSPOT_DEFAULT_INBOX")

# --- Validation ---
def validate_api_config():
    """Basic validation for essential API config."""
    if not API_BASE_URL:
        raise ValueError("API_BASE_URL environment variable not set in .env file.")
    if not SY_API_USERNAME or not SY_API_PASSWORD:
        # Changed from Warning to Error - Credentials are now essential
        raise ValueError(
            "SY_API_USERNAME and SY_API_PASSWORD environment variables must be set "
            "for dynamic token authentication."
        )
    if not LLM_BASE_URL:
        raise ValueError("LLM_BASE_URL environment variable not set in .env file.")
    if not LLM_API_KEY:
        raise ValueError("LLM_API_KEY environment variable not set in .env file.")
    if not LLM_MODEL_NAME:
        raise ValueError("LLM_MODEL_NAME environment variable not set in .env file.")
    if not HUBSPOT_API_TOKEN:
        raise ValueError("HUBSPOT_API_TOKEN environment variable not set in .env file.")

# Run on import
validate_api_config()

# --- Initialize HubSpot Client ---
try:
    HUBSPOT_CLIENT = HubSpot(access_token=HUBSPOT_API_TOKEN)
except Exception as e:
    print(f"\n!!! <- Error initializing HubSpot client: {e}")
    HUBSPOT_CLIENT = None
    raise ValueError(f"Failed to initialize HubSpot client: {e}")
