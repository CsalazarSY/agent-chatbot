"""Hubspot Agent create function"""

# agents/hubspot/hubspot_agent.py
from typing import Optional, List, Callable
from autogen_core.memory import Memory

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Import ALL tool functions
from src.tools.hubspot.conversation.conversation_tools import (
    get_actor_details,
    get_actors_batch,
    get_channel_account_details,
    get_channel_details,
    list_channel_accounts,
    list_channels,
    get_inbox_details,
    list_inboxes,
    get_message_details,
    get_original_message_content,
    archive_thread,
    get_thread_details,
    get_thread_messages,
    list_threads,
    send_message_to_thread,
    update_thread,
)

# Import Ticket tools
from src.tools.hubspot.tickets.ticket_tools import (
    create_support_ticket_for_conversation,
)

# Import system message
from src.agents.hubspot.system_message import hubspot_agent_system_message

# Import Agent Name
from src.agents.agent_names import HUBSPOT_AGENT_NAME

# --- Collect all tool functions ---
# Conversation Tools
conversation_tools: List[Callable] = [
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

# Ticket Tools
ticket_tools: List[Callable] = [
    create_support_ticket_for_conversation,
]

# Combined list of all tools for the agent
all_hubspot_tools: List[Callable] = conversation_tools + ticket_tools


# --- Agent Creation Function ---
def create_hubspot_agent(
    model_client: OpenAIChatCompletionClient, memory: Optional[List[Memory]] = None
) -> AssistantAgent:
    """
    Creates and configures the HubSpot Agent with an expanded toolkit
    for managing conversations and tickets.

    Args:
        model_client: An initialized OpenAIChatCompletionClient instance.
        memory: Optional list of memory objects to attach to the agent.

    Returns:
        An configured AssistantAgent instance.
    """
    hubspot_assistant = AssistantAgent(
        name=HUBSPOT_AGENT_NAME,
        description="Interacts with HubSpot APIs. Manages conversation threads (get, list, update/archive [DevOnly]), messages (get, send COMMENT/MESSAGE), actors, channels, and inboxes. Its primary ticket-related function is to create specialized support tickets linked to conversations for handoffs. Returns raw dicts/lists or confirmation strings.",
        system_message=hubspot_agent_system_message,
        model_client=model_client,
        memory=memory,
        tools=all_hubspot_tools,
        reflect_on_tool_use=False,
    )
    return hubspot_assistant
