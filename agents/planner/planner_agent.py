# agents/planner/planner_agent.py
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Import system message string
from agents.planner.system_message import planner_assistant_system_message

# --- Agent Creation Function ---
def create_planner_agent(model_client: OpenAIChatCompletionClient) -> AssistantAgent:
    """
    Creates and configures the Planner Assistant Agent.

    Args:
        model_client: An initialized OpenAIChatCompletionClient instance.

    Returns:
        An configured AssistantAgent instance.
    """
    if not model_client:
        raise ValueError("model_client must be provided to create_planner_agent")

    planner_assistant = AssistantAgent(
        name="planner_assistant",
        description="Workflow manager that coordinates between product lookup, pricing, and user communication",
        system_message=planner_assistant_system_message,
        model_client=model_client,
        reflect_on_tool_use=True
    )
    return planner_assistant