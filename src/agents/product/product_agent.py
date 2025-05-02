# agents/product/product_agent.py
from autogen_core.memory import Memory
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Import tools/functions
from src.tools.sticker_api.sy_api import sy_list_products

# Import system message string
from src.agents.product.system_message import PRODUCT_ASSISTANT_SYSTEM_MESSAGE

# --- Agent Name Constant ---
PRODUCT_AGENT_NAME = "product_assistant"

# --- Tool list ---
all_product_tools = [sy_list_products]

# --- Agent Creation Function ---
def create_product_agent(model_client: OpenAIChatCompletionClient) -> AssistantAgent:
    """
    Creates and configures the product Assistant Agent.

    Args:
        model_client: An initialized OpenAIChatCompletionClient instance.

    Returns:
        An configured AssistantAgent instance.
    """

    product_assistant = AssistantAgent(
        name=PRODUCT_AGENT_NAME,
        description="Finds product IDs by searching the live API product list. Lists available products by counting API results. Your only tool for product information.",
        system_message=PRODUCT_ASSISTANT_SYSTEM_MESSAGE,
        model_client=model_client,
        tools=all_product_tools,
        reflect_on_tool_use=True
    )
    return product_assistant