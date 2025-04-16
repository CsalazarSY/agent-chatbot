# agents/price/price_agent.py
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Import tools/functions
from agents.price.tools.api import get_price

# Import system message string
from agents.price.system_message import price_assistant_system_message

# --- Agent Name Constant ---
PRICE_AGENT_NAME = "price_assistant"

# --- Agent Creation Function ---
def create_price_agent(model_client: OpenAIChatCompletionClient) -> AssistantAgent:
    """
    Creates and configures the Price Assistant Agent.

    Args:
        model_client: An initialized OpenAIChatCompletionClient instance.

    Returns:
        An configured AssistantAgent instance.
    """
    if not model_client:
        raise ValueError("model_client must be provided to create_price_agent")

    price_assistant = AssistantAgent(
        name=PRICE_AGENT_NAME,
        description="Gets specific price quotes when it has all parameters.",
        system_message=price_assistant_system_message,
        model_client=model_client,
        tools=[get_price],
        reflect_on_tool_use=True
    )
    return price_assistant