# config.py
import os
import asyncio
import httpx
import json # Added for potential use in refresh_sy_token error handling
from dotenv import load_dotenv
from hubspot import HubSpot

# Import the login function and constants needed for it
from agents.stickeryou.tools.sy_api import sy_perform_login, ERROR_PREFIX

# Load environment variables from .env file
load_dotenv()

# --- API Configuration ---
API_AUTH_TOKEN = os.getenv("API_AUTH_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL")
API_VERSION = os.getenv("API_VERSION", "v1") # Default to v1 if not set

# --- SY API Credentials for Dynamic Token ---
SY_API_USERNAME = os.getenv("SY_API_USERNAME")
SY_API_PASSWORD = os.getenv("SY_API_PASSWORD")
SY_API_AUTH_TOKEN_DYNAMIC: str | None = None # Global variable for dynamic token

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

# --- Dynamic SY Token Refresh Function ---
async def refresh_sy_token() -> bool:
    """
    Attempts to fetch a new SY API token using credentials from environment variables
    and updates the global SY_API_AUTH_TOKEN_DYNAMIC.

    Returns:
        bool: True if the token was successfully refreshed, False otherwise.
    """
    global SY_API_AUTH_TOKEN_DYNAMIC # Declare intent to modify the global variable

    print("...Attempting to refresh SY API token...")
    if not SY_API_USERNAME or not SY_API_PASSWORD:
        print("Error: SY_API_USERNAME or SY_API_PASSWORD not set in environment variables.")
        return False

    try:
        # Call the imported login function
        result = await sy_perform_login(username=SY_API_USERNAME, password=SY_API_PASSWORD)

        if isinstance(result, dict) and "token" in result:
            SY_API_AUTH_TOKEN_DYNAMIC = result.get("token")
            expiry = result.get("expirationMinutes", "N/A")
            print(f"Successfully refreshed SY API token. Expires in: {expiry} minutes.")
            return True
        elif isinstance(result, str) and result.startswith(ERROR_PREFIX):
            print(f"Error refreshing SY API token: {result}")
            SY_API_AUTH_TOKEN_DYNAMIC = None # Clear potentially stale token
            return False
        else:
            print(f"Unexpected result type during token refresh: {type(result)}")
            SY_API_AUTH_TOKEN_DYNAMIC = None
            return False

    except Exception as e:
        print(f"Exception during SY API token refresh: {e}")
        SY_API_AUTH_TOKEN_DYNAMIC = None
        return False

# --- Validation ---
def validate_api_config():
    """Basic validation for essential API config."""
    if not API_BASE_URL:
        raise ValueError("API_BASE_URL environment variable not set in .env file.")
    if not SY_API_USERNAME or not SY_API_PASSWORD:
        print(" Warning: SY_API_USERNAME or SY_API_PASSWORD not set. Dynamic token refresh will fail.")
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
    hubspot_client = HubSpot(access_token=HUBSPOT_API_TOKEN)
except Exception as e:
    print(f"\n!!! <- Error initializing HubSpot client: {e}")
    hubspot_client = None
    raise ValueError(f"Failed to initialize HubSpot client: {e}")