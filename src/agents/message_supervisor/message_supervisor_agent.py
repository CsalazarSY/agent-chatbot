"""Defines and creates the Message Supervisor Agent."""

# /src/agents/message_supervisor/message_supervisor_agent.py

# --- Third Party Imports ---
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

# --- First Party Imports ---
from src.agents.message_supervisor.system_message import (
    MESSAGE_SUPERVISOR_SYSTEM_MESSAGE,
)
from src.agents.agent_names import MESSAGE_SUPERVISOR_AGENT_NAME


# --- Agent Creation Function ---
def create_message_supervisor_agent(
    model_client: OpenAIChatCompletionClient,
) -> AssistantAgent:
    """
    Creates and configures the Message Supervisor Agent.

    Args:
        model_client: An initialized OpenAIChatCompletionClient instance.
                      (Typically the secondary client is sufficient for formatting).

    Returns:
        An configured AssistantAgent instance.
    """

    supervisor_assistant = AssistantAgent(
        name=MESSAGE_SUPERVISOR_AGENT_NAME,
        description="Formats final messages from Markdown or plain textto HTML for display.",
        system_message=MESSAGE_SUPERVISOR_SYSTEM_MESSAGE,
        model_client=model_client,
        memory=None,  # Stateless formatting agent
        tools=[],  # No tools needed
        reflect_on_tool_use=False,
    )
    return supervisor_assistant
