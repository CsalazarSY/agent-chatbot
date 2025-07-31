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
)
from src.services.logger_config import log_message

# Import the quick reply labels data
from src.markdown_info.quick_replies.live_product_references import (
    LPA_PRODUCT_QUICK_REPLIES_LABELS,
)

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
        # Create a lookup map for quick and easy access to labels
        product_label_map = {
            item["productId"]: item["quick_reply_label"]
            for item in LPA_PRODUCT_QUICK_REPLIES_LABELS
        }

        enriched_product_data = []
        for product in product_data:
            if isinstance(product, dict):
                product_id = product.get("id")
                label = product_label_map.get(product_id)
                
                if label:
                    # Add the new fields to the product dictionary
                    product["quick_reply_label"] = label
                    # Set the value to be the same as the label for user clarity
                    product["quick_reply_value"] = label
                
                enriched_product_data.append(product)

        # 2. Populate memory with the enriched JSON data
        await lpa_memory.add(
            MemoryContent(
                content={"product_data_list": enriched_product_data},
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
        description="Expert on a master JSON list of products held in its memory. It answers Planner's queries by searching this data. If multiple products match a query, it returns a structured JSON object containing both the raw product data and a pre-formatted quick-reply string for clarification.",
        system_message=LIVE_PRODUCT_AGENT_SYSTEM_MESSAGE,
        model_client=model_client,
        memory=[lpa_memory],
        tools=[get_live_countries],
        reflect_on_tool_use=True,
    )
    return live_product_assistant
