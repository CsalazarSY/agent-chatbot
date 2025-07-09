"""Defines and creates the Live Product Agent."""

# /src/agents/live_product/live_product_agent.py

from typing import List, Callable
from autogen_agentchat.agents import AssistantAgent
from autogen_core.memory import ListMemory, MemoryContent, MemoryMimeType
from autogen_ext.models.openai import OpenAIChatCompletionClient

from src.agents.live_product.system_message import LIVE_PRODUCT_AGENT_SYSTEM_MESSAGE
from src.agents.agent_names import LIVE_PRODUCT_AGENT_NAME

# Import the necessary tools from the API file
from src.tools.sticker_api.sy_api import (
    sy_list_products,
    get_live_countries,
    format_products_as_qr,
)
from src.services.logger_config import log_message

# List of tools for the LiveProductAgent
live_product_tools: List[Callable] = [
    get_live_countries,
    format_products_as_qr,
]

# --- Update Agent Creation Function ---
async def create_live_product_agent(
    model_client: OpenAIChatCompletionClient,
) -> AssistantAgent:
    """
    Creates and configures the Live Product Agent.
    This function is async to pre-load product data into memory on creation.
    """
    # 1. Fetch live product data
    product_data = await sy_list_products()
    lpa_memory = ListMemory()

    if isinstance(product_data, list):
        # 2. Populate memory with the raw JSON data
        await lpa_memory.add(
            MemoryContent(
                content={"product_data_list": product_data},
                mime_type=MemoryMimeType.JSON,
                metadata={"source": "stickeryou_API_live_product_list"},
            )
        )
    else:
        log_message(
            "LPA_CREATION_ERROR: Could not fetch live product list.", log_type="error"
        )

    # 3. Create the agent instance
    live_product_assistant = AssistantAgent(
        name=LIVE_PRODUCT_AGENT_NAME,
        description="Expert on a master JSON list of products held in its memory. It answers Planners queries by searching and filtering this internal data. It can return raw JSON or formatted Quick Replies. It can also give information about shipping countries.",
        system_message=LIVE_PRODUCT_AGENT_SYSTEM_MESSAGE,
        model_client=model_client,
        memory=[lpa_memory],
        tools=live_product_tools,
        reflect_on_tool_use=False,
    )
    return live_product_assistant
