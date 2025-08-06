"""Central place to define agent name constants to avoid circular imports."""

# /src/agents/agent_names.py

# Agent Names
HUBSPOT_AGENT_NAME = "HubSpot_Agent"
PRICE_QUOTE_AGENT_NAME = "Price_Quote_Agent"
PLANNER_AGENT_NAME = "Planner_Agent"
ORDER_AGENT_NAME = "Order_Agent"
STICKER_YOU_AGENT_NAME = "StickerYou_Agent"
LIVE_PRODUCT_AGENT_NAME = "Live_Product_Agent"

# User Proxy Name
USER_PROXY_AGENT_NAME = "User_Proxy_Agent"

# List of all agent names
ALL_AGENT_NAMES = [
    PLANNER_AGENT_NAME,
    PRICE_QUOTE_AGENT_NAME,
    HUBSPOT_AGENT_NAME,
    ORDER_AGENT_NAME,
    USER_PROXY_AGENT_NAME,
    STICKER_YOU_AGENT_NAME,
    LIVE_PRODUCT_AGENT_NAME,
]


def get_all_agent_names_as_string():
    """
    Returns a comma-separated string of all agent names.
    """
    return ", ".join(ALL_AGENT_NAMES)
