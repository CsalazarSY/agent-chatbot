"""Defines and creates the StickerYou Agent (Knowledge Base Expert)."""

# /src/agents/sticker_you_agent/sticker_you_agent.py

import os
from pathlib import Path
from typing import Optional

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.memory.chromadb import (
    ChromaDBVectorMemory,
    PersistentChromaDBVectorMemoryConfig,
    CustomEmbeddingFunctionConfig
)

# Import custom embedding function class
from src.services.chromadb.custom_embedding_function import ModernBertEmbeddingFunction

from config import (
    CHROMA_COLLECTION_NAME_CONFIG,
    CHROMA_DB_PATH_CONFIG,
    # We still need the model name to pass to our custom function
    CHROMA_EMBEDDING_MODEL_NAME_CONFIG,
)
from src.agents.sticker_you.system_message import STICKER_YOU_AGENT_SYSTEM_MESSAGE
from src.agents.agent_names import STICKER_YOU_AGENT_NAME


def create_sticker_you_agent(
    model_client: OpenAIChatCompletionClient,
) -> AssistantAgent:
    """
    Creates and configures the StickerYou Agent using a custom embedding function
    to ensure compatibility with the ingested ChromaDB data.
    """
    product_rag_memory: Optional[ChromaDBVectorMemory] = None

    db_path = Path(CHROMA_DB_PATH_CONFIG)
    db_parent_path = db_path.parent
    os.makedirs(db_parent_path, exist_ok=True)

    # 1. Instantiate our custom embedding function.
    custom_embed_config = CustomEmbeddingFunctionConfig(
        function=ModernBertEmbeddingFunction,
        params={"model_name": CHROMA_EMBEDDING_MODEL_NAME_CONFIG},
    )

    # 2. Create the memory configuration.
    chroma_config = PersistentChromaDBVectorMemoryConfig(
        collection_name=CHROMA_COLLECTION_NAME_CONFIG,
        persistence_path=str(db_path),
        embedding_function_config=custom_embed_config,
        k=3,
        score_threshold=0.35,
    )
    
    # The standard ChromaDBVectorMemory class will now use our function.
    product_rag_memory = ChromaDBVectorMemory(config=chroma_config)

    sticker_you_assistant = AssistantAgent(
        name=STICKER_YOU_AGENT_NAME,
        description="Expert on StickerYou's knowledge base (website content, product details, FAQs). Analyzes KB content to answer Planner queries, indicating if info is not found, irrelevant, or if the query is out of scope.",
        system_message=STICKER_YOU_AGENT_SYSTEM_MESSAGE,
        model_client=model_client,
        memory=[product_rag_memory] if product_rag_memory else None,
        reflect_on_tool_use=False,
    )
    return sticker_you_assistant