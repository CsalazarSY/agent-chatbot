# agents/planner/planner_agent.py
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Import system message string
from agents.planner.system_message import planner_assistant_system_message

# --- Agent Name Constant ---
PLANNER_AGENT_NAME = "planner_assistant"

# --- Type Hint Imports ---
from typing import Optional, List
from autogen_core.memory import Memory

# --- Agent Creation Function ---
def create_planner_agent(model_client: OpenAIChatCompletionClient, memory: Optional[List[Memory]] = None) -> AssistantAgent:
    """
    Creates and configures the Planner Assistant Agent.

    Args:
        model_client: An initialized OpenAIChatCompletionClient instance.
        memory: Optional list of memory objects to attach to the agent.

    Returns:
        An configured AssistantAgent instance.
    """
    if not model_client:
        raise ValueError("model_client must be provided to create_planner_agent")

    planner_assistant = AssistantAgent(
        name=PLANNER_AGENT_NAME,
        description="Workflow manager that coordinates between product lookup, pricing, and user communication",
        system_message=planner_assistant_system_message,
        model_client=model_client,
        memory=memory,
        reflect_on_tool_use=True
    )
    return planner_assistant