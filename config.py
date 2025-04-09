# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- API Configuration ---
API_AUTH_TOKEN = os.getenv("API_AUTH_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL")
API_VERSION = os.getenv("API_VERSION", "v1") # Default to v1 if not set

DEFAULT_COUNTRY_CODE = os.getenv("DEFAULT_COUNTRY_CODE", "US")
DEFAULT_CURRENCY_CODE = os.getenv("DEFAULT_CURRENCY_CODE", "USD")

LLM_BASE_URL = os.getenv("LLM_BASE_URL")
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME")

# --- Validation ---
def validate_api_config():
    """Basic validation for essential API config."""
    if not API_BASE_URL:
        raise ValueError("API_BASE_URL environment variable not set in .env file.")
    if not API_AUTH_TOKEN:
        print(" Warning: API_AUTH_TOKEN is empty!")
    if not LLM_BASE_URL:
        raise ValueError("LLM_BASE_URL environment variable not set in .env file.")
    if not LLM_API_KEY:
        raise ValueError("LLM_API_KEY environment variable not set in .env file.")
    if not LLM_MODEL_NAME:
        raise ValueError("LLM_MODEL_NAME environment variable not set in .env file.")

validate_api_config()