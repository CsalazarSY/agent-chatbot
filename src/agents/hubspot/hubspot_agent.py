"""Hubspot Agent create function"""

# agents/hubspot/hubspot_agent.py
from typing import Optional, List, Callable
from autogen_core.memory import Memory

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Hubspot Agent Tools
from src.tools.hubspot.conversation_tools import (
    send_message_to_thread,
    get_thread_details,
    get_thread_messages,
    list_threads,
    update_thread,
    archive_thread,
    get_actor_details,
    get_actors_batch,
    list_inboxes,
    get_inbox_details,
    list_channels,
    get_channel_details,
    list_channel_accounts,
    get_channel_account_details,
    get_message_details,
    get_original_message_content,
)
from src.agents.hubspot.system_message import hubspot_agent_system_message

# --- Agent Name Constant ---
HUBSPOT_AGENT_NAME = "hubspot_assistant"

# --- Collect all tool functions ---
all_hubspot_tools: List[Callable] = [
    send_message_to_thread,
    get_thread_details,
    get_thread_messages,
    list_threads,
    update_thread,
    archive_thread,
    get_actor_details,
    get_actors_batch,
    list_inboxes,
    get_inbox_details,
    list_channels,
    get_channel_details,
    list_channel_accounts,
    get_channel_account_details,
    get_message_details,
    get_original_message_content,
]


# --- Agent Creation Function ---
def create_hubspot_agent(
    model_client: OpenAIChatCompletionClient, memory: Optional[List[Memory]] = None
) -> AssistantAgent:
    """
    Creates and configures the HubSpot Agent with an expanded toolkit.

    Args:
        model_client: An initialized OpenAIChatCompletionClient instance.
        memory: Optional list of memory objects to attach to the agent.

    Returns:
        An configured AssistantAgent instance.
    """
    hubspot_assistant = AssistantAgent(
        name=HUBSPOT_AGENT_NAME,
        description="Interacts with the HubSpot Conversations API. Manages threads (get, list, update/archive [DevOnly]), messages (get, send COMMENT/MESSAGE), actors, channels, and inboxes. Primarily used for internal operations (like handoffs) or dev requests. Returns raw dicts/lists or confirmation strings.",
        system_message=hubspot_agent_system_message,
        model_client=model_client,
        memory=memory,
        tools=all_hubspot_tools,
        reflect_on_tool_use=False,
    )
    return hubspot_assistant
