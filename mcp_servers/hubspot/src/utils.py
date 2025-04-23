import os
from dotenv import load_dotenv
from hubspot import HubSpot

# Load environment variables from .env file
load_dotenv()

def load_hubspot_config():
    """Loads HubSpot configuration from environment variables."""
    config = {
        "api_token": os.getenv("HUBSPOT_API_TOKEN"),
        "default_channel": os.getenv("HUBSPOT_DEFAULT_CHANNEL"),
        "default_channel_account": os.getenv("HUBSPOT_DEFAULT_CHANNEL_ACCOUNT"),
        "default_sender_actor_id": os.getenv("HUBSPOT_DEFAULT_SENDER_ACTOR_ID"),
    }
    if not config["api_token"]:
        raise ValueError("HUBSPOT_API_TOKEN environment variable not set.")
    return config

def create_hubspot_client(api_token: str) -> HubSpot:
    """Initializes and returns the HubSpot API client."""
    try:
        client = HubSpot(access_token=api_token)
        return client
    except Exception as e:
        raise ValueError(f"Failed to initialize HubSpot client: {e}")

# Load config globally or pass it around as needed
try:
    hubspot_config = load_hubspot_config()
except ValueError as e:
    # Decide how to handle this - exit, or let it fail later?
    # For now, let it proceed and fail during lifespan if token is missing.
    hubspot_config = {"api_token": None}