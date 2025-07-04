"""Central config file to handle env vars"""

# pylint: disable=W0603:global-statement, C0415
# /src/config.py
import os
from dotenv import load_dotenv
from hubspot import HubSpot
from pathlib import Path

from src.services.logger_config import log_message

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

# --- ChromaDB RAG Configuration (for ProductAgent) ---
# Get the relative path from .env
_CHROMA_DB_RELATIVE_PATH = os.getenv("CHROMA_DB_PATH")
CHROMA_COLLECTION_NAME_CONFIG = os.getenv("CHROMA_COLLECTION_NAME")
CHROMA_EMBEDDING_MODEL_NAME_CONFIG = os.getenv("CHROMA_EMBEDDING_MODEL_NAME")

# Resolve to an absolute path. If _CHROMA_DB_RELATIVE_PATH is None, this will be None.
CHROMA_DB_PATH_CONFIG: str | None = None
if _CHROMA_DB_RELATIVE_PATH:
    try:
        # config.py is in the project root, same level as .env
        # Construct path relative to the directory of THIS config file.
        project_root = Path(__file__).resolve().parent
        absolute_chroma_path = (project_root / _CHROMA_DB_RELATIVE_PATH).resolve(
            strict=False
        )
        CHROMA_DB_PATH_CONFIG = str(absolute_chroma_path)
        log_message(f"ChromaDB path: {CHROMA_DB_PATH_CONFIG}", prefix="!!!")
    except FileNotFoundError:
        # This block might be less likely to be hit if strict=False and we construct from __file__
        log_message(
            f"ChromaDB path '{_CHROMA_DB_RELATIVE_PATH}' from .env, relative to {project_root}, does not resolve to an existing location. This might cause issues.",
            prefix="!!! WARNING:",
            log_type="warning",
        )
        # Fallback to simple absolute if robust resolution fails
        CHROMA_DB_PATH_CONFIG = str(Path(_CHROMA_DB_RELATIVE_PATH).absolute())
    except Exception as e:
        log_message(
            f"ERROR resolving ChromaDB path '{_CHROMA_DB_RELATIVE_PATH}': {e}",
            prefix="!!! ERROR:",
            log_type="error",
        )
        CHROMA_DB_PATH_CONFIG = None  # Ensure it's None if resolution fails badly


# --- HubSpot Configuration ---
HUBSPOT_API_TOKEN = os.getenv("HUBSPOT_API_TOKEN")
HUBSPOT_API_SECRET = os.getenv("HUBSPOT_API_SECRET")
HUBSPOT_DEFAULT_SENDER_ACTOR_ID = os.getenv("HUBSPOT_DEFAULT_SENDER_ACTOR_ID")
HUBSPOT_DEFAULT_CHANNEL = os.getenv("HUBSPOT_DEFAULT_CHANNEL")
HUBSPOT_DEFAULT_CHANNEL_ACCOUNT = os.getenv("HUBSPOT_DEFAULT_CHANNEL_ACCOUNT")
HUBSPOT_DEFAULT_INBOX = os.getenv("HUBSPOT_DEFAULT_INBOX")

# --- HubSpot Pipeline & Stage IDs ---
HUBSPOT_PIPELINE_ID_SUPPORT = os.getenv("HUBSPOT_PIPELINE_ID_SUPPORT")
HUBSPOT_SUPPORT_STAGE_ID = os.getenv("HUBSPOT_SUPPORT_STAGE_ID")

# Assisted Sales Pipeline
HUBSPOT_PIPELINE_ID_ASSISTED_SALES = os.getenv("HUBSPOT_PIPELINE_ID_ASSISTED_SALES")
HUBSPOT_AS_STAGE_ID = os.getenv("HUBSPOT_AS_STAGE_ID")

# Promo Reseller Pipeline
HUBSPOT_PIPELINE_ID_PROMO_RESELLER = os.getenv("HUBSPOT_PIPELINE_ID_PROMO_RESELLER")
HUBSPOT_PR_STAGE_ID = os.getenv("HUBSPOT_PR_STAGE_ID")

# Customer Success Pipeline
HUBSPOT_PIPELINE_ID_CUSTOMER_SUCCESS = os.getenv("HUBSPOT_PIPELINE_ID_CUSTOMER_SUCCESS")
HUBSPOT_CS_STAGE_ID = os.getenv("HUBSPOT_CS_STAGE_ID")

# --- WismoLabs Configuration ---
WISMOLABS_API_URL = os.getenv("WISMOLABS_API_URL")
WISMOLABS_CONSULT_URL = os.getenv("WISMOLABS_CONSULT_URL")

# --- Redis Configuration ---
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT", 6380)
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")


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
    # Validate ChromaDB RAG Config
    if not _CHROMA_DB_RELATIVE_PATH:  # Check the original env var first
        raise ValueError("CHROMA_DB_PATH environment variable not set in .env file.")
    if not CHROMA_DB_PATH_CONFIG:  # Then check the resolved path
        raise ValueError(
            f"CHROMA_DB_PATH '{_CHROMA_DB_RELATIVE_PATH}' could not be resolved to a valid path."
        )
    if not CHROMA_COLLECTION_NAME_CONFIG:
        raise ValueError(
            "CHROMA_COLLECTION_NAME environment variable not set in .env file."
        )
    if not CHROMA_EMBEDDING_MODEL_NAME_CONFIG:
        raise ValueError(
            "CHROMA_EMBEDDING_MODEL_NAME environment variable not set in .env file."
        )
    if not HUBSPOT_PIPELINE_ID_SUPPORT:
        raise ValueError(
            "HUBSPOT_PIPELINE_ID_SUPPORT environment variable not set in .env file."
        )
    if not HUBSPOT_SUPPORT_STAGE_ID:
        raise ValueError(
            "HUBSPOT_SUPPORT_STAGE_ID environment variable not set in .env file."
        )
    if not HUBSPOT_PIPELINE_ID_ASSISTED_SALES:
        raise ValueError(
            "HUBSPOT_PIPELINE_ID_ASSISTED_SALES environment variable not set in .env file."
        )
    if not HUBSPOT_AS_STAGE_ID:
        raise ValueError(
            "HUBSPOT_AS_STAGE_ID environment variable not set in .env file."
        )
    if not HUBSPOT_PIPELINE_ID_PROMO_RESELLER:
        raise ValueError(
            "HUBSPOT_PIPELINE_ID_PROMO_RESELLER environment variable not set in .env file."
        )
    if not HUBSPOT_PR_STAGE_ID:
        raise ValueError(
            "HUBSPOT_PR_STAGE_ID environment variable not set in .env file."
        )
    if not HUBSPOT_PIPELINE_ID_CUSTOMER_SUCCESS:
        raise ValueError(
            "HUBSPOT_PIPELINE_ID_CUSTOMER_SUCCESS environment variable not set in .env file."
        )
    if not HUBSPOT_CS_STAGE_ID:
        raise ValueError(
            "HUBSPOT_CS_STAGE_ID environment variable not set in .env file."
        )
    if not REDIS_HOST or not REDIS_PASSWORD:
        raise ValueError(
            "REDIS_HOST and REDIS_PASSWORD environment variables must be set."
        )
    if not WISMOLABS_API_URL:
        raise ValueError("WISMOLABS_API_URL environment variable not set in .env file.")


# Run on import
validate_api_config()

# --- Initialize HubSpot Client ---
try:
    HUBSPOT_CLIENT = HubSpot(access_token=HUBSPOT_API_TOKEN)
except Exception as e:
    log_message(
        f"Error initializing HubSpot client: {e}", prefix="\n!!! <-", log_type="error"
    )
    HUBSPOT_CLIENT = None
    raise ValueError(f"Failed to initialize HubSpot client: {e}")
