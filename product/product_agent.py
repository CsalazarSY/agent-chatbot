# product/product_agent.py
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Import tools/functions
from product.tools.find_product_id import find_product_id

# Import system message string
from product.system_message import product_assistant_system_message

# --- Agent Creation Function ---
def create_product_agent(model_client: OpenAIChatCompletionClient) -> AssistantAgent:
    """
    Creates and configures the product Assistant Agent.

    Args:
        model_client: An initialized OpenAIChatCompletionClient instance.

    Returns:
        An configured AssistantAgent instance.
    """
    if not model_client:
        raise ValueError("model_client must be provided to create_product_agent")

    product_assistant = AssistantAgent(
        name="product_assistant",
        description="Finds product IDs based on descriptions. Precision tool for converting product descriptions (or names) to numerical IDs",
        system_message=product_assistant_system_message,
        model_client=model_client,
        tools=[find_product_id],
        reflect_on_tool_use=False
    )
    return product_assistant