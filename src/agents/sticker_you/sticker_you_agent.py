"""Defines and creates the StickerYou Agent (Knowledge Base Expert)."""

# /src/agents/sticker_you_agent/sticker_you_agent.py

import os
from pathlib import Path
from typing import Optional, List

from autogen_agentchat.agents import AssistantAgent
from autogen_core.memory import Memory
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.memory.chromadb import (
    ChromaDBVectorMemory,
    PersistentChromaDBVectorMemoryConfig,
)

from config import (
    CHROMA_COLLECTION_NAME_CONFIG,
    CHROMA_DB_PATH_CONFIG,
    CHROMA_EMBEDDING_MODEL_NAME_CONFIG,
)
from src.agents.sticker_you.system_message import STICKER_YOU_AGENT_SYSTEM_MESSAGE
from src.agents.agent_names import STICKER_YOU_AGENT_NAME

# This agent primarily relies on its system message and the LLM's ability
# to understand RAG-injected context if that's how the knowledge base is implemented.
# It does not have explicit tools defined here for ChromaDB querying, as that's usually
# handled at a higher level (e.g., by modifying the message history or prompt before sending to LLM)
# or if it were a tool, it would be passed in. For now, we assume it's RAG-based.


def create_sticker_you_agent(
    model_client: OpenAIChatCompletionClient,
) -> AssistantAgent:
    """
    Creates and configures the StickerYou Agent, an expert on website content,
    product catalog information (from a knowledge base), and FAQs.

    Args:
        model_client: An initialized OpenAIChatCompletionClient instance.
        memory: Optional list of memory objects to attach to the agent.

    Returns:
        A configured AssistantAgent instance.
    """

    product_rag_memory: Optional[ChromaDBVectorMemory] = None

    db_path = Path(CHROMA_DB_PATH_CONFIG)  # This is now an absolute path from config.py
    db_parent_path = db_path.parent
    os.makedirs(db_parent_path, exist_ok=True)

    chroma_config = PersistentChromaDBVectorMemoryConfig(
        collection_name=CHROMA_COLLECTION_NAME_CONFIG,
        persistence_path=str(db_path),
        embedding_model_name="nomic-ai/modernbert-embed-base",
        k=3,
        score_threshold=0.35,
    )
    product_rag_memory = ChromaDBVectorMemory(config=chroma_config)

    # We are not clearing the memory here (`await product_rag_memory.clear()`)
    # because we assume the chromaRAG pipeline is responsible for populating and maintaining it.
    # This agent is a consumer of that pre-populated DB.

    sticker_you_assistant = AssistantAgent(
        name=STICKER_YOU_AGENT_NAME,
        description="Expert on StickerYou's knowledge base (website content, product details, FAQs). Analyzes KB content to answer Planner queries, indicating if info is not found, irrelevant, or if the query is out of scope.",
        system_message=STICKER_YOU_AGENT_SYSTEM_MESSAGE,
        model_client=model_client,
        memory=[product_rag_memory] if product_rag_memory else None,
        reflect_on_tool_use=False,
    )
    return sticker_you_assistant
