"""Configures and creates the Price Quote Assistant Agent."""

# /src/agents/price_quote/price_quote_agent.py

# --- Type Hint Imports ---
from typing import Optional, List, Callable
from autogen_core.memory import Memory

# --- Third Party Imports ---
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

# --- First Party Imports ---
# Import relevant pricing tool functions and internal auth functions
from src.tools.sticker_api.sy_api import (
    sy_get_specific_price,
    sy_get_price_tiers,
    sy_list_countries,
    sy_verify_login,  # Internal use for token checks
    sy_perform_login,  # Internal use for token refresh
)

# Import the updated system message string
from src.agents.price_quote.system_message import PRICE_QUOTE_AGENT_SYSTEM_MESSAGE

# Import Agent Name
from src.agents.agent_names import PRICE_QUOTE_AGENT_NAME

# --- Collect relevant tool functions ---
# Only pricing and internal auth tools
price_quote_tools: List[Callable] = [
    sy_get_specific_price,
    sy_get_price_tiers,
    sy_verify_login,
    sy_perform_login,
]


# --- Agent Creation Function ---
def create_price_quote_agent(
    model_client: OpenAIChatCompletionClient,
) -> AssistantAgent:
    """
    Creates and configures the Price Quote Assistant Agent.

    Args:
        model_client: An initialized OpenAIChatCompletionClient instance.
        memory: Optional list of memory objects to attach to the agent.

    Returns:
        An configured AssistantAgent instance.
    """
    price_quote_assistant = AssistantAgent(
        name=PRICE_QUOTE_AGENT_NAME,
        description="Dual-purpose agent that: 1) Interacts with the StickerYou API for pricing tasks (getting specific prices and tier pricing) and 2) Validates custom quote data against form definition rules before ticket creation. Also handles internal token management. Returns Pydantic models, specific dicts/lists, or validation results.",
        system_message=PRICE_QUOTE_AGENT_SYSTEM_MESSAGE,
        model_client=model_client,
        tools=price_quote_tools,
        reflect_on_tool_use=False,
    )
    return price_quote_assistant
