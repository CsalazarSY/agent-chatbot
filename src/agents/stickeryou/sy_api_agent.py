"""Configures and creates the StickerYou API Assistant Agent."""

# /src/agents/stickeryou/sy_api_agent.py

# --- Type Hint Imports ---
from typing import Optional, List, Callable
from autogen_core.memory import Memory

# --- Third Party Imports ---
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

# --- First Party Imports ---
# Import ALL tool functions
from src.tools.sticker_api.sy_api import (
    sy_get_design_preview,
    sy_list_orders_by_status_get,
    sy_list_orders_by_status_post,
    sy_get_order_details,
    sy_cancel_order,
    sy_get_order_item_statuses,
    sy_get_order_tracking,
    sy_list_products,
    sy_get_price_tiers,
    sy_get_specific_price,
    sy_list_countries,
    sy_verify_login,
    sy_perform_login,
)

# Import the updated system message string
from src.agents.stickeryou.system_message import SY_API_AGENT_SYSTEM_MESSAGE

# --- Agent Name Constant ---
SY_API_AGENT_NAME = "sy_api_assistant"

# --- Collect all tool functions ---
all_sy_api_tools: List[Callable] = [
    sy_get_design_preview,
    sy_list_orders_by_status_get,
    sy_list_orders_by_status_post,
    sy_get_order_details,
    sy_cancel_order,
    sy_get_order_item_statuses,
    sy_get_order_tracking,
    sy_list_products,
    sy_get_price_tiers,
    sy_get_specific_price,
    sy_list_countries,
    sy_verify_login,
    sy_perform_login,
]


# --- Agent Creation Function ---
def create_sy_api_agent(
    model_client: OpenAIChatCompletionClient, memory: Optional[List[Memory]] = None
) -> AssistantAgent:
    """
    Creates and configures the SY API Assistant Agent.

    Args:
        model_client: An initialized OpenAIChatCompletionClient instance.
        memory: Optional list of memory objects to attach to the agent.

    Returns:
        An configured AssistantAgent instance.
    """
    sy_api_assistant = AssistantAgent(
        name=SY_API_AGENT_NAME,
        description="Interacts with the StickerYou API for specific allowed endpoints: pricing (specific, tiers, countries), orders (details, tracking, item status, list by status GET, cancel [DevOnly]), and user login checks (InternalOnly). Returns Pydantic models or specific dicts/lists.",
        system_message=SY_API_AGENT_SYSTEM_MESSAGE,
        model_client=model_client,
        memory=memory,
        tools=all_sy_api_tools,
        reflect_on_tool_use=False,
    )
    return sy_api_assistant
