"""Defines and creates the Planner Assistant Agent."""

# /src/agents/planner/planner_agent.py

# --- Standard Library Imports ---
from typing import Optional, List

# --- Third Party Imports ---
from autogen_agentchat.agents import AssistantAgent
from autogen_core.memory import Memory, ListMemory, MemoryContent, MemoryMimeType
from autogen_ext.models.openai import OpenAIChatCompletionClient

# --- First Party Imports ---
from src.agents.planner.system_message import PLANNER_ASSISTANT_SYSTEM_MESSAGE

# Import Agent Name
from src.agents.agent_names import PLANNER_AGENT_NAME
from src.services.time_service import is_business_hours


# --- Agent Creation Function ---
async def create_planner_agent(
    model_client: OpenAIChatCompletionClient, conversation_id: str
) -> AssistantAgent:
    """
    Creates and configures the Planner Assistant Agent with conversation-specific memory.

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

    on_business_hours = is_business_hours()
    await memory.add(
        MemoryContent(
            content=f"Is_Currently_Business_Hours: {on_business_hours}",
            mime_type=MemoryMimeType.TEXT,
            metadata={"priority": "critical", "source": "system_time"},
        )
    )

    planner_assistant = AssistantAgent(
        name=PLANNER_AGENT_NAME,
        description="The orchestrator. It coordinates between the StickerYou_Agent (for website/product info & FAQs), Live_Product_Agent (for live product IDs & countries), Price_Quote_Agent, HubSpot_Agent, and Order_Agent. It communicates with the User_Proxy_Agent to interact with the user.",
        system_message=PLANNER_ASSISTANT_SYSTEM_MESSAGE,
        model_client=model_client,
        memory=[memory],
        # tools=[end_planner_turn], # Tool is available via function calling in the new AutoGen versions
        reflect_on_tool_use=False,
    )
    return planner_assistant
