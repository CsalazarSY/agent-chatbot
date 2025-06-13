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
]


# --- Agent Creation Function ---
def create_price_quote_agent(
    model_client: OpenAIChatCompletionClient,
) -> AssistantAgent:
    """
    Creates and configures the Price Quote Assistant Agent.

    Args:
        model_client: An initialized OpenAIChatCompletionClient instance.

    Returns:
        An configured AssistantAgent instance.
    """
    price_quote_assistant = AssistantAgent(
        name=PRICE_QUOTE_AGENT_NAME,
        description="Provides product pricing using StickerYou API tools (specific price, price tiers). For custom quotes, guides the Planner by parsing user's raw responses (relayed by Planner), managing internal form data, determining next questions based on a predefined form structure, and validating the final data. Returns API data for pricing, or instructional commands to the Planner for custom quotes.",
        system_message=PRICE_QUOTE_AGENT_SYSTEM_MESSAGE,
        model_client=model_client,
        tools=price_quote_tools,
        reflect_on_tool_use=False,
    )
    return price_quote_assistant
