"""Defines and creates the Order Agent."""

# --- Standard Library Imports ---
from typing import List, Callable

# --- Third Party Imports ---
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

# --- First Party Imports ---
from src.agents.orders.system_message import ORDER_AGENT_SYSTEM_MESSAGE
from src.agents.agent_names import ORDER_AGENT_NAME
from src.tools.wismoLabs.orders import get_wismo_order_status

order_tools: List[Callable] = [
    get_wismo_order_status,
]

# --- Agent Creation Function (No changes needed here, but shown for context) ---
def create_order_agent(
    model_client: OpenAIChatCompletionClient,
) -> AssistantAgent:
    """
    Creates and configures the Order Agent.

    Args:
        model_client: An initialized OpenAIChatCompletionClient instance.

    Returns:
        A configured AssistantAgent instance.
    """
    order_assistant = AssistantAgent(
        name=ORDER_AGENT_NAME,
        description=(
            "Interacts with WismoLabs API to fetch order status and tracking information using an order ID. Returns detailed JSON data on success or an error string on failure."
        ),
        system_message=ORDER_AGENT_SYSTEM_MESSAGE,
        model_client=model_client,
        tools=order_tools,
        reflect_on_tool_use=False,
    )
    return order_assistant