"""Central config file to handle env vars"""

# pylint: disable=W0603:global-statement, C0415
# /src/config.py
import os
from dotenv import load_dotenv
from hubspot import HubSpot

# Load environment variables from .env file
load_dotenv()

# --- API Configuration ---
API_BASE_URL = os.getenv("API_BASE_URL")
API_VERSION = os.getenv("API_VERSION", "v1")  # Default to v1 if not set

# --- SY API Credentials for Dynamic Token ---
SY_API_USERNAME = os.getenv("SY_API_USERNAME")
SY_API_PASSWORD = os.getenv("SY_API_PASSWORD")

# Internal variable for dynamic token
_SY_API_AUTH_TOKEN: str | None = None


# --- Token Accessors ---
def get_sy_api_token() -> str | None:
    """Returns the current dynamic StickerYou API token."""
    return _SY_API_AUTH_TOKEN


def set_sy_api_token(new_token: str | None):
    """Updates the internal dynamic StickerYou API token."""
    global _SY_API_AUTH_TOKEN  # Needed to use the module-level variable
    if new_token:
        _SY_API_AUTH_TOKEN = new_token
    else:
        _SY_API_AUTH_TOKEN = None


DEFAULT_COUNTRY_CODE = os.getenv("DEFAULT_COUNTRY_CODE", "US")
DEFAULT_CURRENCY_CODE = os.getenv("DEFAULT_CURRENCY_CODE", "USD")

# --- LLM Configuration ---
LLM_BASE_URL = os.getenv("LLM_BASE_URL")
LLM_API_KEY = os.getenv("LLM_API_KEY")

# Primary LLM
LLM_PRIMARY_MODEL_NAME = os.getenv("LLM_PRIMARY_MODEL_NAME")
LLM_PRIMARY_MODEL_FAMILY = os.getenv("LLM_PRIMARY_MODEL_FAMILY")

# Secondary LLM
LLM_SECONDARY_MODEL_NAME = os.getenv("LLM_SECONDARY_MODEL_NAME")
LLM_SECONDARY_MODEL_FAMILY = os.getenv("LLM_SECONDARY_MODEL_FAMILY")

# --- HubSpot Configuration ---
HUBSPOT_API_TOKEN = os.getenv("HUBSPOT_API_TOKEN")
HUBSPOT_API_SECRET = os.getenv("HUBSPOT_API_SECRET")
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
        raise ValueError(
            "SY_API_USERNAME and SY_API_PASSWORD environment variables must be set for dynamic token authentication."
        )
    if not LLM_BASE_URL:
        raise ValueError("LLM_BASE_URL environment variable not set in .env file.")
    # Validate Primary LLM
    if not LLM_API_KEY:
        raise ValueError("LLM_API_KEY environment variable not set in .env file.")
    if not LLM_PRIMARY_MODEL_NAME:
        raise ValueError(
            "LLM_PRIMARY_MODEL_NAME environment variable not set in .env file."
        )
    if not LLM_PRIMARY_MODEL_FAMILY:
        raise ValueError(
            "LLM_PRIMARY_MODEL_FAMILY environment variable not set in .env file."
        )
    # Validate Secondary LLM
    if not LLM_SECONDARY_MODEL_NAME:
        raise ValueError(
            "LLM_SECONDARY_MODEL_NAME environment variable not set in .env file."
        )
    if not LLM_SECONDARY_MODEL_FAMILY:
        raise ValueError(
            "LLM_SECONDARY_MODEL_FAMILY environment variable not set in .env file."
        )
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
