"""Product agent creation"""

# /src/agents/product/product_agent.py
import asyncio
import json
from typing import Optional

from autogen_agentchat.agents import AssistantAgent
from autogen_core.memory import ListMemory, MemoryContent, MemoryMimeType
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Import tools/functions
from src.tools.sticker_api.sy_api import sy_list_products, API_ERROR_PREFIX

# Import system message string
from src.agents.product.system_message import PRODUCT_ASSISTANT_SYSTEM_MESSAGE

# Import Agent Name
from src.agents.agent_names import PRODUCT_AGENT_NAME

# --- Tool list ---
all_product_tools = [sy_list_products]


# --- Agent Creation Function ---
async def create_product_agent(
    model_client: OpenAIChatCompletionClient,
) -> AssistantAgent:
    """
    Creates and configures the product Assistant Agent.
    Attempts to preload the product list into memory, splitting it into chunks.

    Args:
        model_client: An initialized OpenAIChatCompletionClient instance.

    Returns:
        An configured AssistantAgent instance.
    """
    # Number of chunks to split the product list into
    NUM_CHUNKS = 3

    product_list_memory: Optional[ListMemory] = None
    try:
        product_list_result = await sy_list_products()

        if isinstance(product_list_result, list):
            product_list_json = json.dumps(product_list_result)

            total_products = len(product_list_result)
            chunk_size = (
                total_products + NUM_CHUNKS - 1
            ) // NUM_CHUNKS  # Ceiling division

            product_list_memory = ListMemory()
            for i in range(NUM_CHUNKS):
                start_index = i * chunk_size
                end_index = min((i + 1) * chunk_size, total_products)
                if start_index >= total_products:
                    break  # Avoid creating empty chunks

                chunk = product_list_result[start_index:end_index]
                chunk_json = json.dumps(chunk)

                await product_list_memory.add(
                    MemoryContent(
                        content=chunk_json,  # Store the JSON string of the chunk directly
                        mime_type=MemoryMimeType.JSON,
                        metadata={
                            "source": "preloaded_product_list_chunk",
                            "chunk_index": i,
                            "total_chunks": NUM_CHUNKS,
                        },
                    )
                )
        elif isinstance(product_list_result, str) and product_list_result.startswith(
            API_ERROR_PREFIX
        ):
            print(f"    ! WARN: Failed to preload product list: {product_list_result}")
        else:
            print(
                f"    ! WARN: Unexpected result type from sy_list_products: {type(product_list_result)}. Cannot preload."
            )

    except Exception as e:
        print(f"    ! ERROR: Exception during product list preloading: {e}")

    product_assistant = AssistantAgent(
        name=PRODUCT_AGENT_NAME,
        description="Interprets product data from the live StickerYou API (using sy_list_products tool OR preloaded memory). Finds Product IDs based on descriptions, lists/filters products by criteria, counts products, and summarizes product details. Does NOT handle pricing.",
        system_message=PRODUCT_ASSISTANT_SYSTEM_MESSAGE,
        model_client=model_client,
        memory=[product_list_memory] if product_list_memory else None,
        tools=all_product_tools,
        reflect_on_tool_use=True,
    )
    return product_assistant
