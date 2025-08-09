"""Hubspot Agent create function"""

# /src/agents/hubspot/hubspot_agent.py
from typing import Optional, List, Callable
from autogen_core.memory import Memory, ListMemory, MemoryContent, MemoryMimeType

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Import system message
from src.agents.hubspot.system_message import HUBSPOT_AGENT_SYSTEM_MESSAGE

# Import Agent Name
from src.agents.agent_names import HUBSPOT_AGENT_NAME

# Conversation and Ticket Tools
from src.tools.hubspot.conversation.conversation_tools import send_message_to_thread, get_thread_details
from src.tools.hubspot.tickets.ticket_tools import (
    update_ticket,
    move_ticket_to_human_assistance_pipeline,
)
from src.tools.hubspot.tickets.dto_responses import TicketDetailResponse

# Config imports for default values
from config import (
    HUBSPOT_DEFAULT_SENDER_ACTOR_ID,
    HUBSPOT_DEFAULT_CHANNEL,
    HUBSPOT_DEFAULT_CHANNEL_ACCOUNT,
    HUBSPOT_DEFAULT_INBOX,
    HUBSPOT_PIPELINE_ID_AICHAT,
    HUBSPOT_PIPELINE_STAGE_ID_AICHAT_OPEN,
    HUBSPOT_PIPELINE_STAGE_ID_AICHAT_ASSISTANCE_ON_HOURS,
    HUBSPOT_PIPELINE_STAGE_ID_AICHAT_ASSISTANCE_OFF_HOURS,
    HUBSPOT_PIPELINE_STAGE_ID_AICHAT_CLOSED,
)


# --- Collect all tool functions ---
# Conversation Tools
conversation_tools: List[Callable] = [
    send_message_to_thread,
]

# Ticket Tools
ticket_tools: List[Callable] = [
    update_ticket,
    move_ticket_to_human_assistance_pipeline,
]


# --- Agent Creation Function ---
async def create_hubspot_agent(
    model_client: OpenAIChatCompletionClient, conversation_id: str
) -> AssistantAgent:
    """
    Creates and configures the HubSpot Agent, initializing its memory with
    conversation-specific details and system configurations.

    Args:
        model_client: An initialized OpenAIChatCompletionClient instance.
        conversation_id: The current HubSpot conversation/thread ID.

    Returns:
        A configured AssistantAgent instance.
    """
    memory = ListMemory()

    # Add critical conversation ID to memory
    await memory.add(
        MemoryContent(
            content=f"Current_HubSpot_Thread_ID: {conversation_id}",
            mime_type=MemoryMimeType.TEXT,
            metadata={"priority": "critical", "source": "hubspot_thread"},
        )
    )

    # Look up and add associated ticket ID to memory
    try:
        thread_details = await get_thread_details(thread_id=conversation_id)
        if not isinstance(thread_details, str):
            if (hasattr(thread_details, 'threadAssociations') and 
                thread_details.threadAssociations and 
                thread_details.threadAssociations.associatedTicketId):
                
                ticket_id = thread_details.threadAssociations.associatedTicketId
                await memory.add(
                    MemoryContent(
                        content=f"Associated_HubSpot_Ticket_ID: {ticket_id}",
                        mime_type=MemoryMimeType.TEXT,
                        metadata={"priority": "critical", "source": "hubspot_ticket"},
                    )
                )
    except Exception as e:
        # If we can't get the ticket ID, continue without it
        # The agent can still function for other operations
        pass

    # Add default system configurations to memory
    defaults_to_add = {
        "Default_HubSpot_Sender_Actor_ID": HUBSPOT_DEFAULT_SENDER_ACTOR_ID,
        "Default_HubSpot_Channel_ID": HUBSPOT_DEFAULT_CHANNEL,
        "Default_HubSpot_Channel_Account_ID": HUBSPOT_DEFAULT_CHANNEL_ACCOUNT,
        "Default_HubSpot_Inbox_ID": HUBSPOT_DEFAULT_INBOX,
    }
    for key, value in defaults_to_add.items():
        if value:
            await memory.add(
                MemoryContent(
                    content=f"{key}: {value}",
                    mime_type=MemoryMimeType.TEXT,
                    metadata={
                        "priority": "normal",
                        "source": "system_config_hubspot_defaults",
                    },
                )
            )

    # Add the single pipeline and its stages to memory
    pipeline_info = {
        "HubSpot_Pipeline_ID_AI_Chat": HUBSPOT_PIPELINE_ID_AICHAT,
        "HubSpot_Stage_ID_AI_Chat_Open": HUBSPOT_PIPELINE_STAGE_ID_AICHAT_OPEN,
        "HubSpot_Stage_ID_AI_Chat_Assistance_On_Hours": HUBSPOT_PIPELINE_STAGE_ID_AICHAT_ASSISTANCE_ON_HOURS,
        "HubSpot_Stage_ID_AI_Chat_Assistance_Off_Hours": HUBSPOT_PIPELINE_STAGE_ID_AICHAT_ASSISTANCE_OFF_HOURS,
        "HubSpot_Stage_ID_AI_Chat_Closed": HUBSPOT_PIPELINE_STAGE_ID_AICHAT_CLOSED,
    }
    for key, value in pipeline_info.items():
        if value:
            await memory.add(
                MemoryContent(
                    content=f"{key}: {value}",
                    mime_type=MemoryMimeType.TEXT,
                    metadata={
                        "priority": "normal",
                        "source": "system_config_hubspot_pipelines",
                    },
                )
            )

    hubspot_assistant = AssistantAgent(
        name=HUBSPOT_AGENT_NAME,
        description="Interacts with HubSpot APIs. Manages conversation threads and updates existing tickets. Has access to all necessary context (conversation IDs, pipeline IDs, etc.) and can look up ticket associations as needed. Returns raw dicts/lists or confirmation strings.",
        system_message=HUBSPOT_AGENT_SYSTEM_MESSAGE,
        model_client=model_client,
        memory=[memory],
        tools=conversation_tools + ticket_tools,
        reflect_on_tool_use=False,
    )
    return hubspot_assistant
