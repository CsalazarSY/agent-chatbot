# agents/hubspot/hubspot_agent.py

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

from agents.hubspot.tools.send_message import send_message_to_thread
from agents.hubspot.system_message import hubspot_agent_system_message

# --- Agent Creation Function ---
def create_hubspot_agent(model_client: OpenAIChatCompletionClient) -> AssistantAgent:
    """
    Creates and configures the HubSpot Agent.

    Args:
        model_client: An initialized OpenAIChatCompletionClient instance.

    Returns:
        An configured AssistantAgent instance.
    """
    if not model_client:
        raise ValueError("model_client must be provided to create_hubspot_agent")

    hubspot_assistant = AssistantAgent(
        name="hubspot_assistant",
        description="Handles the communication from the agents to HubSpot API",
        system_message=hubspot_agent_system_message,
        model_client=model_client,
        tools=[send_message_to_thread],
        reflect_on_tool_use=False
    )
    return hubspot_assistant