"""Central config file to handle env vars"""

# pylint: disable=W0603:global-statement, C0415
# /src/config.py
import os
from dotenv import load_dotenv
from hubspot import HubSpot
from pathlib import Path


# Load environment variables from .env file
load_dotenv()

# --- UTILITY FUNCTIONS ---
def get_required_env_variable(var_name: str) -> str:
    """
    Gets an environment variable and raises an error if it's not found.
    This ensures the return type is always 'str'.
    """
    value = os.getenv(var_name)
    if value is None or value.strip() == "":
        raise ValueError(f"FATAL: Required environment variable '{var_name}' is not set.")
    return value

# --- API Configuration ---
API_BASE_URL = get_required_env_variable("API_BASE_URL")
API_VERSION = os.getenv("API_VERSION", "v1")  # Default to v1 if not set

# --- SY API Credentials for Dynamic Token ---
SY_API_USERNAME = get_required_env_variable("SY_API_USERNAME")
SY_API_PASSWORD = get_required_env_variable("SY_API_PASSWORD")
SY_API_ORDER_TOKEN = get_required_env_variable("SY_API_ORDER_TOKEN")

# Internal variable for dynamic token
_SY_API_AUTH_TOKEN: str | None = None


# --- Token Accessors ---
def get_sy_api_token() -> str | None:
    """Returns the current dynamic StickerYou API token."""
    return _SY_API_AUTH_TOKEN


def set_sy_api_token(new_token: str | None):
    """Updates the internal dynamic StickerYou API token."""
    global _SY_API_AUTH_TOKEN
    if new_token:
        _SY_API_AUTH_TOKEN = new_token
    else:
        _SY_API_AUTH_TOKEN = None


DEFAULT_COUNTRY_CODE = os.getenv("DEFAULT_COUNTRY_CODE", "US")
DEFAULT_CURRENCY_CODE = os.getenv("DEFAULT_CURRENCY_CODE", "USD")

# --- LLM Configuration ---
LLM_BASE_URL = get_required_env_variable("LLM_BASE_URL")
LLM_API_KEY = get_required_env_variable("LLM_API_KEY")

# Primary LLM
LLM_PRIMARY_MODEL_NAME = get_required_env_variable("LLM_PRIMARY_MODEL_NAME")
LLM_PRIMARY_MODEL_FAMILY = get_required_env_variable("LLM_PRIMARY_MODEL_FAMILY")

# Secondary LLM
LLM_SECONDARY_MODEL_NAME = get_required_env_variable("LLM_SECONDARY_MODEL_NAME")
LLM_SECONDARY_MODEL_FAMILY = get_required_env_variable("LLM_SECONDARY_MODEL_FAMILY")

# --- ChromaDB RAG Configuration (for Knowledge base agent) ---
_CHROMA_DB_RELATIVE_PATH = get_required_env_variable("CHROMA_DB_PATH")
CHROMA_COLLECTION_NAME_CONFIG = get_required_env_variable("CHROMA_COLLECTION_NAME")
CHROMA_EMBEDDING_MODEL_NAME_CONFIG = get_required_env_variable("CHROMA_EMBEDDING_MODEL_NAME")

# Resolve to an absolute path
try:
    # config.py is in the project root, same level as .env
    # Construct path relative to the directory of THIS config file.
    project_root = Path(__file__).resolve().parent
    absolute_chroma_path = (project_root / _CHROMA_DB_RELATIVE_PATH).resolve(strict=False)
    CHROMA_DB_PATH_CONFIG = str(absolute_chroma_path)
except Exception as e:
    raise ValueError(f"Could not resolve CHROMA_DB_PATH '{_CHROMA_DB_RELATIVE_PATH}': {e}") from e


# --- HubSpot Configuration ---
HUBSPOT_API_TOKEN = get_required_env_variable("HUBSPOT_API_TOKEN")
HUBSPOT_API_SECRET = os.getenv("HUBSPOT_API_SECRET")
HUBSPOT_DEFAULT_SENDER_ACTOR_ID = os.getenv("HUBSPOT_DEFAULT_SENDER_ACTOR_ID")
HUBSPOT_DEFAULT_CHANNEL = os.getenv("HUBSPOT_DEFAULT_CHANNEL")
HUBSPOT_DEFAULT_CHANNEL_ACCOUNT = os.getenv("HUBSPOT_DEFAULT_CHANNEL_ACCOUNT")
HUBSPOT_DEFAULT_INBOX = os.getenv("HUBSPOT_DEFAULT_INBOX")

# --- HubSpot Pipeline & Stage IDs ---
HUBSPOT_PIPELINE_ID_SUPPORT = get_required_env_variable("HUBSPOT_PIPELINE_ID_SUPPORT")
HUBSPOT_SUPPORT_STAGE_ID = get_required_env_variable("HUBSPOT_SUPPORT_STAGE_ID")

# Assisted Sales Pipeline
HUBSPOT_PIPELINE_ID_ASSISTED_SALES = get_required_env_variable("HUBSPOT_PIPELINE_ID_ASSISTED_SALES")
HUBSPOT_AS_STAGE_ID = get_required_env_variable("HUBSPOT_AS_STAGE_ID")

# Promo Reseller Pipeline
HUBSPOT_PIPELINE_ID_PROMO_RESELLER = get_required_env_variable("HUBSPOT_PIPELINE_ID_PROMO_RESELLER")
HUBSPOT_PR_STAGE_ID = get_required_env_variable("HUBSPOT_PR_STAGE_ID")

# Customer Success Pipeline
HUBSPOT_PIPELINE_ID_CUSTOMER_SUCCESS = get_required_env_variable("HUBSPOT_PIPELINE_ID_CUSTOMER_SUCCESS")
HUBSPOT_CS_STAGE_ID = get_required_env_variable("HUBSPOT_CS_STAGE_ID")

# --- Redis Configuration ---
REDIS_HOST = get_required_env_variable("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6380"))
REDIS_PASSWORD = get_required_env_variable("REDIS_PASSWORD")

# --- WismoLabs API Credentials & Token ---
WISMOLABS_API_URL = get_required_env_variable("WISMOLABS_API_URL")
WISMOLABS_TRACKING_URL = os.getenv("WISMOLABS_TRACKING_URL")
WISMOLABS_USERNAME = get_required_env_variable("WISMOLABS_USERNAME")
WISMOLABS_PASSWORD = get_required_env_variable("WISMOLABS_PASSWORD")

# Internal variable for dynamic WismoLabs token
_WISMOLABS_API_AUTH_TOKEN: str | None = None

# --- Token Accessors ---
def get_wismo_api_token() -> str | None:
    """Returns the current dynamic WismoLabs API token."""
    return _WISMOLABS_API_AUTH_TOKEN


def set_wismo_api_token(new_token: str | None):
    """Updates the internal dynamic WismoLabs API token."""
    global _WISMOLABS_API_AUTH_TOKEN
    if new_token:
        _WISMOLABS_API_AUTH_TOKEN = new_token
    else:
        _WISMOLABS_API_AUTH_TOKEN = None

# --- Validation ---
def validate_api_config():
    """
    Basic validation for essential API config.
    Most required variables are now validated at import time by get_required_env_variable().
    This function performs additional checks for optional variables that become required in context.
    """
    # Verify ChromaDB path was resolved successfully
    if not CHROMA_DB_PATH_CONFIG:
        raise ValueError("CHROMA_DB_PATH could not be resolved to a valid path.")
    
    # All other required variables are validated by get_required_env_variable() calls above
    print("✓ All required environment variables are properly configured.")

# Run on import
validate_api_config()

# --- Initialize HubSpot Client ---
try:
    HUBSPOT_CLIENT = HubSpot(access_token=HUBSPOT_API_TOKEN)
except Exception as e:
    # Raise the error so the app fails fast if HubSpot can't be initialized.
    # The logging of this failure will be handled at the application's entry point.
    raise ValueError(f"Failed to initialize HubSpot client: {e}") from e
