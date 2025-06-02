"""Defines and creates the Order Agent."""

# /src/agents/orders/order_agent.py

# --- Standard Library Imports ---
from typing import Optional, List, Callable

# --- Third Party Imports ---
from autogen_agentchat.agents import AssistantAgent
from autogen_core.memory import Memory
from autogen_ext.models.openai import OpenAIChatCompletionClient

# --- First Party Imports ---
from src.agents.orders.system_message import ORDER_AGENT_SYSTEM_MESSAGE
from src.agents.agent_names import ORDER_AGENT_NAME
from src.tools.wismoLabs.orders import get_order_status_by_details

# --- Collect all tool functions ---
order_tools: List[Callable] = [
    get_order_status_by_details,
]


# --- Agent Creation Function ---
def create_order_agent(
    model_client: OpenAIChatCompletionClient, memory: Optional[List[Memory]] = None
) -> AssistantAgent:
    """
    Creates and configures the Order Agent.

    Args:
        model_client: An initialized OpenAIChatCompletionClient instance.
        memory: Optional list of memory objects to attach to the agent.

    Returns:
        A configured AssistantAgent instance.
    """
    order_assistant = AssistantAgent(
        name=ORDER_AGENT_NAME,
        description=(
            "Interacts with WismoLabs API to fetch order status and tracking information. Returns JSON data on success or an error string on failure."
        ),
        system_message=ORDER_AGENT_SYSTEM_MESSAGE,
        model_client=model_client,
        memory=memory,
        tools=order_tools,
        reflect_on_tool_use=False,
    )
    return order_assistant
