"""Product agent creation"""

# /src/agents/product/product_agent.py
from typing import Optional
import os  # Added for path
from pathlib import Path  # Added for path

from autogen_agentchat.agents import AssistantAgent

# Removed ListMemory, MemoryContent, MemoryMimeType as we are moving to ChromaDB
from autogen_ext.memory.chromadb import (
    ChromaDBVectorMemory,
    PersistentChromaDBVectorMemoryConfig,
)
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Import tools/functions
from src.tools.sticker_api.sy_api import sy_list_products

# Import system message string
from src.agents.product.system_message import PRODUCT_ASSISTANT_SYSTEM_MESSAGE

# Import Agent Name
from src.agents.agent_names import PRODUCT_AGENT_NAME

# Import ChromaDB config from main config file
from config import (
    CHROMA_DB_PATH_CONFIG,
    CHROMA_COLLECTION_NAME_CONFIG,
    CHROMA_EMBEDDING_MODEL_NAME_CONFIG,
)

# --- Tool list ---
all_product_tools = [sy_list_products]


# --- Agent Creation Function ---
async def create_product_agent(
    model_client: OpenAIChatCompletionClient,
) -> AssistantAgent:
    """
    Creates and configures the product Assistant Agent, now using ChromaDBVectorMemory.

    Args:
        model_client: An initialized OpenAIChatCompletionClient instance.

    Returns:
        An configured AssistantAgent instance.
    """
    product_rag_memory: Optional[ChromaDBVectorMemory] = None
    try:
        # Ensure the parent directory for ChromaDB exists (taken from config)
        if (
            not CHROMA_DB_PATH_CONFIG
            or not CHROMA_COLLECTION_NAME_CONFIG
            or not CHROMA_EMBEDDING_MODEL_NAME_CONFIG
        ):
            raise ValueError(
                "ChromaDB configuration missing in config.py or .env file."
            )

        db_path = Path(CHROMA_DB_PATH_CONFIG)
        # db_parent_path = db_path.parent
        # os.makedirs(db_parent_path, exist_ok=True)
        # print(f"    Initializing ChromaDBVectorMemory at: {db_path}")
        # print(
        #     f"    Using collection: {CHROMA_COLLECTION_NAME_CONFIG}, Embedding: {CHROMA_EMBEDDING_MODEL_NAME_CONFIG}"
        # )

        chroma_config = PersistentChromaDBVectorMemoryConfig(
            collection_name=CHROMA_COLLECTION_NAME_CONFIG,
            persistence_path=str(db_path),  # Ensure it's a string
            embedding_model_name=CHROMA_EMBEDDING_MODEL_NAME_CONFIG,
            k=5,  # Retrieve top 5 results by default, can be tuned
            score_threshold=0.4,  # Minimum similarity score for retrieval, can be tuned
        )
        product_rag_memory = ChromaDBVectorMemory(config=chroma_config)
        # We are not clearing the memory here (`await product_rag_memory.clear()`)
        # because we assume the chromaRAG pipeline is responsible for populating and maintaining it.
        # This agent is a consumer of that pre-populated DB.

    except Exception as e:
        print(f"    ! ERROR: Exception during ChromaDBVectorMemory initialization: {e}")
        import traceback

        traceback.print_exc()
        # Optionally, decide if the agent should be created without memory or raise error

    product_assistant = AssistantAgent(
        name=PRODUCT_AGENT_NAME,
        description="Interprets product data by querying a ChromaDB vector store (populated with website content) and can also use the live StickerYou API (sy_list_products tool) as a fallback. Finds Product IDs, lists/filters products, counts products, and summarizes product details. Does NOT handle pricing.",
        system_message=PRODUCT_ASSISTANT_SYSTEM_MESSAGE,  # This will need updates
        model_client=model_client,
        memory=[product_rag_memory] if product_rag_memory else None,
        tools=all_product_tools,  # sy_list_products can be a fallback or for specific live checks
        reflect_on_tool_use=True,
    )
    return product_assistant
