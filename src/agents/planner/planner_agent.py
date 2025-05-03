"""Defines and creates the Planner Assistant Agent."""

# agents/planner/planner_agent.py

# --- Standard Library Imports ---
from typing import Optional, List

# --- Third Party Imports ---
from autogen_agentchat.agents import AssistantAgent
from autogen_core.memory import Memory
from autogen_ext.models.openai import OpenAIChatCompletionClient

# --- First Party Imports ---
from src.agents.planner.system_message import PLANNER_ASSISTANT_SYSTEM_MESSAGE

# Import Agent Name
from src.agents.agent_names import PLANNER_AGENT_NAME


# --- Agent Creation Function ---
def create_planner_agent(
    model_client: OpenAIChatCompletionClient, memory: Optional[List[Memory]] = None
) -> AssistantAgent:
    """
    Creates and configures the Planner Assistant Agent.

    Args:
        model_client: An initialized OpenAIChatCompletionClient instance.
        memory: Optional list of memory objects to attach to the agent.

    Returns:
        An configured AssistantAgent instance.
    """

    planner_assistant = AssistantAgent(
        name=PLANNER_AGENT_NAME,
        description="The orchestrator, it coordinates between StickerYou API agent, Hubspot agent, Product Agent and the user",
        system_message=PLANNER_ASSISTANT_SYSTEM_MESSAGE,
        model_client=model_client,
        memory=memory,
        reflect_on_tool_use=True,
    )
    return planner_assistant
