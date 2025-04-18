# mcp_servers/sy_api/src/utils.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def load_sy_api_config():
    """Loads SY API configuration from environment variables."""
    config = {
        "base_url": os.getenv("SY_API_BASE_URL"),
        "api_version": os.getenv("SY_API_VERSION", "v1"), # Default to v1 if not set
        "auth_token": os.getenv("SY_API_AUTH_TOKEN"),
        "default_country_code": os.getenv("SY_DEFAULT_COUNTRY_CODE", "US"),
        "default_currency_code": os.getenv("SY_DEFAULT_CURRENCY_CODE", "USD"),
    }

    # Validate required configuration
    if not config["base_url"]:
        raise ValueError("SY_API_BASE_URL environment variable is not set.")
    if not config["auth_token"]:
        # Allow empty token for now, but maybe should raise error depending on API needs
        # print("Warning: SY_API_AUTH_TOKEN environment variable is not set.")
        pass

    # print("SY API Server Configuration Loaded:") # Commented out for stdio transport
    # print(f"  Base URL: {config['base_url']}")
    # print(f"  API Version: {config['api_version']}")
    # print(f"  Auth Token: {'*' * (len(config['auth_token']) - 4)}{config['auth_token'][-4:]}" if config['auth_token'] else "Not Set")
    # print(f"  Default Country Code: {config['default_country_code']}")
    # print(f"  Default Currency Code: {config['default_currency_code']}")

    return config

# Load config globally when module is imported
try:
    sy_api_config = load_sy_api_config()
except ValueError as e:
    # print(f"FATAL: SY API Configuration error: {e}") # Commented out
    # Allow server to start but tool will fail if config is missing
    sy_api_config = {
        "base_url": None,
        "api_version": "v1",
        "auth_token": None,
        "default_country_code": "US",
        "default_currency_code": "USD",
    } 