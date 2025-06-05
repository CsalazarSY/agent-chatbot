"""Defines and creates the Live Product Agent."""

# /src/agents/live_product/live_product_agent.py

from typing import Optional, List, Callable

from autogen_agentchat.agents import AssistantAgent
from autogen_core.memory import Memory
from autogen_ext.models.openai import OpenAIChatCompletionClient

from src.agents.live_product.system_message import (
    LIVE_PRODUCT_AGENT_SYSTEM_MESSAGE,
)
from src.agents.agent_names import LIVE_PRODUCT_AGENT_NAME

# Import specific tools for this agent
from src.tools.sticker_api.sy_api import sy_list_products, sy_list_countries

# List of tools for the LiveProductAgent
live_product_tools: List[Callable] = [
    sy_list_products,
    sy_list_countries,
]


def create_live_product_agent(
    model_client: OpenAIChatCompletionClient, memory: Optional[List[Memory]] = None
) -> AssistantAgent:
    """
    Creates and configures the Live Product Agent, responsible for fetching
    live product lists and country lists from the StickerYou API.

    Args:
        model_client: An initialized OpenAIChatCompletionClient instance.
        memory: Optional list of memory objects to attach to the agent.

    Returns:
        A configured AssistantAgent instance.
    """
    live_product_assistant = AssistantAgent(
        name=LIVE_PRODUCT_AGENT_NAME,
        description="Fetches live product lists and supported country lists from the StickerYou API. Returns processed string messages to the Planner, including raw JSON data snippets and potential error strings.",
        system_message=LIVE_PRODUCT_AGENT_SYSTEM_MESSAGE,
        model_client=model_client,
        memory=memory,
        tools=live_product_tools,
        reflect_on_tool_use=False,
    )
    return live_product_assistant
