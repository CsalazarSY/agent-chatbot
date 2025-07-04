"""Defines and creates the Message Supervisor Agent."""

# /src/agents/message_supervisor/message_supervisor_agent.py

# --- Third Party Imports ---
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelInfo

# --- First Party Imports ---
from src.agents.message_supervisor.system_message import (
    MESSAGE_SUPERVISOR_SYSTEM_MESSAGE,
)
from src.agents.agent_names import MESSAGE_SUPERVISOR_AGENT_NAME
from src.services.logger_config import log_message

# Import LLM config (assuming it's in the main config.py and .env is loaded)
from config import LLM_BASE_URL, LLM_API_KEY


# --- Agent Creation Function ---
def create_message_supervisor_agent() -> AssistantAgent:
    """
    Creates and configures the Message Supervisor Agent.
    This agent now creates its own dedicated OpenAICompletionClient.
    """

    # Configuration for the supervisor's dedicated LLM client
    # Ensure these environment variables are set for this model if different from primary/secondary
    supervisor_model_name = "google/gemini-2.0-flash-001"
    supervisor_model_family = "unknown"

    # Create a dedicated model client for the supervisor
    # It will use the general LLM_BASE_URL and LLM_API_KEY from config
    try:
        supervisor_model_client = OpenAIChatCompletionClient(
            model=supervisor_model_name,
            base_url=LLM_BASE_URL, 
            api_key=LLM_API_KEY,   
            temperature=0,         # Critical for deterministic formatting
            timeout=60,            # Reasonable timeout for a formatting task
            model_info=ModelInfo(
                vision=False,
                function_calling=False, # Supervisor doesn't use tools
                json_output=False,
                family=supervisor_model_family,
                structured_output=False, # Not expecting structured output, just HTML string
                multiple_system_messages=False, # Good to have if prompt is complex
            ),
        )
    except Exception as e:
        log_message(
            f"!!! CRITICAL ERROR: Failed to initialize model client for MessageSupervisorAgent: {e}",
            log_type="error",
        )
        raise RuntimeError(f"Could not create model client for MessageSupervisorAgent: {e}")


    supervisor_assistant = AssistantAgent(
        name=MESSAGE_SUPERVISOR_AGENT_NAME,
        description="Strictly formats input text (plain or Markdown, including specific system tags) into HTML. Does not alter content or answer questions.",
        system_message=MESSAGE_SUPERVISOR_SYSTEM_MESSAGE,
        model_client=supervisor_model_client, # Use the dedicated client
        reflect_on_tool_use=False,
    )
    return supervisor_assistant