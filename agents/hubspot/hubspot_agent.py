# agents/hubspot/hubspot_agent.py

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

from agents.hubspot.tools.send_message import send_message_to_thread
from agents.hubspot.system_message import hubspot_agent_system_message

# --- Type Hint Imports ---
from typing import Optional, List
from autogen_core.memory import Memory

# --- Agent Name Constant ---
HUBSPOT_AGENT_NAME = "hubspot_assistant"

# --- Agent Creation Function ---
def create_hubspot_agent(model_client: OpenAIChatCompletionClient, memory: Optional[List[Memory]] = None) -> AssistantAgent:
    """
    Creates and configures the HubSpot Agent.

    Args:
        model_client: An initialized OpenAIChatCompletionClient instance.
        memory: Optional list of memory objects to attach to the agent.

    Returns:
        An configured AssistantAgent instance.
    """
    hubspot_assistant = AssistantAgent(
        name=HUBSPOT_AGENT_NAME,
        description="Handles the communication from the agents to HubSpot API",
        system_message=hubspot_agent_system_message,
        model_client=model_client,
        memory=memory,
        tools=[send_message_to_thread],
        reflect_on_tool_use=False
    )
    return hubspot_assistant