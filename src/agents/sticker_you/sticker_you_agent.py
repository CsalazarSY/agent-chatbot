# /src/agents/sticker_you_agent/sticker_you_agent.py

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

from src.tools.chromadb.query_tool import query_knowledge_base

from src.agents.sticker_you.system_message import STICKER_YOU_AGENT_SYSTEM_MESSAGE
from src.agents.agent_names import STICKER_YOU_AGENT_NAME


def create_sticker_you_agent(
    model_client: OpenAIChatCompletionClient,
) -> AssistantAgent:
    """
    Creates and configures the StickerYou Agent, equipped with a tool
    to directly query the ChromaDB knowledge base.
    """
    sticker_you_assistant = AssistantAgent(
        name=STICKER_YOU_AGENT_NAME,
        description="Expert on StickerYou's knowledge base (website content, product details, FAQs). Analyzes KB content to answer Planner queries, indicating if info is not found, irrelevant, or if the query is out of scope.",
        system_message=STICKER_YOU_AGENT_SYSTEM_MESSAGE,
        model_client=model_client,
        tools=[query_knowledge_base],
        reflect_on_tool_use=False,
    )
    return sticker_you_assistant