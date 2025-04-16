# agent_service.py
import traceback
import uuid # Added for generating conversation IDs
from typing import Sequence, Optional, Dict, Union, ClassVar, Any # Added Any for state

# AutoGen imports
from autogen_agentchat.agents import UserProxyAgent, AssistantAgent
from autogen_agentchat.base import TaskResult
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage, TextMessage, UserMessage
from autogen_agentchat.teams import SelectorGroupChat
from autogen_core import CancellationToken
from autogen_core.models import ModelInfo
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.ui import Console

# Agents
from agents.hubspot.hubspot_agent import create_hubspot_agent, HUBSPOT_AGENT_NAME
from agents.planner.planner_agent import create_planner_agent, PLANNER_AGENT_NAME
from agents.price.price_agent import create_price_agent, PRICE_AGENT_NAME
from agents.product.product_agent import create_product_agent, PRODUCT_AGENT_NAME

# Config imports
from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL_NAME

# Define AgentType alias for clarity
AgentType = Union[AssistantAgent, UserProxyAgent]

# Define User Proxy Name Constant
USER_PROXY_AGENT_NAME = "user_proxy"

class AgentService:
    """
    Manages the setup and execution of AutoGen chat sessions using shared class attributes
    to ensure shared state (model client, agents) across all instances.
    Handles conversation state persistence for stateless environments using a SINGLE shared chat instance.
    WARNING: This implementation is NOT concurrency-safe for multiple simultaneous conversations.
    """
    # --- Class Attributes for Shared State ---
    model_client: ClassVar[Optional[OpenAIChatCompletionClient]] = None
    agents_dict: ClassVar[Dict[str, AgentType]] = {} # Stores initialized agents
    conversation_states: ClassVar[Dict[str, Any]] = {} # In-memory state store (stores state dicts)

    _initialized: ClassVar[bool] = False # Flag for one-time initialization

    # --- Initialization Method ---
    @staticmethod
    def _initialize_shared_state():
        """Initializes the shared class attributes ONCE."""

        if AgentService._initialized:
            print("\n\n!!! AgentService already initialized. Skipping. !!!\n\n")
            return

        try:
            # Create model client
            AgentService.model_client = OpenAIChatCompletionClient(
                model=LLM_MODEL_NAME,
                base_url=LLM_BASE_URL,
                api_key=LLM_API_KEY,
                temperature=0,
                timeout=600,
                model_info=ModelInfo(
                    vision=False,
                    function_calling=True,
                    json_output=False,
                    family="gpt-4o",
                    structured_output=True
                ),
            )

            # Create agents using the class-level client
            planner_assistant = create_planner_agent(AgentService.model_client)
            price_assistant = create_price_agent(AgentService.model_client)
            product_agent = create_product_agent(AgentService.model_client)
            hubspot_agent = create_hubspot_agent(AgentService.model_client)

            # Create agents dictionary using agent names as keys - Stores shared agent instances
            AgentService.agents_dict = {
                PLANNER_AGENT_NAME: planner_assistant,
                PRICE_AGENT_NAME: price_assistant,
                PRODUCT_AGENT_NAME: product_agent,
                HUBSPOT_AGENT_NAME: hubspot_agent,
            }

            AgentService._initialized = True

        except Exception as e:
            print(f"\n\n!!! CRITICAL ERROR during AgentService shared state initialization: {e}")
            traceback.print_exc()

            # Reset state on failure
            AgentService.model_client = None
            AgentService.agents_dict = {}
            AgentService.conversation_states = {}
            AgentService._initialized = False
            raise e

    # --- Constructor ---
    def __init__(self):
        # Ensure shared state is initialized if it hasn't been already
        if not AgentService._initialized:
             AgentService._initialize_shared_state()
        pass

    # Termination Condition
    @staticmethod
    def _get_termination_condition():
        """Helper to define the termination condition."""
        max_message_termination = MaxMessageTermination(max_messages=30)
        text_termination = TextMentionTermination("TASK FAILED") | TextMentionTermination("TASK COMPLETE") | TextMentionTermination("<UserProxyAgent>")
        # The chat should naturally stop when UserProxyAgent turn comes and it has no input.
        return max_message_termination | text_termination

    # --- Core Agent Logic Methods ---

    # Next speaker selector
    @staticmethod
    def custom_speaker_selector(messages: Sequence[BaseAgentEvent | BaseChatMessage]) -> str: # Always returns a string
        """Determines the next speaker based on rules. Aims to be deterministic."""
        if not AgentService._initialized:
            # This case should be rare due to checks in run_chat_session
            print("<- WARN: custom_speaker_selector called before AgentService fully initialized. Defaulting to Planner.")
            return PLANNER_AGENT_NAME

        last_message = messages[-1]

        # Basic check for empty messages sequence
        if not messages:
            # This function determines the *next* speaker after a message. If called with no messages, it's ambiguous.
            print("Selector: No messages, defaulting to Planner.")
            return PLANNER_AGENT_NAME

        # If the last message was from the user (via API), Planner must process it.
        if last_message.source == USER_PROXY_AGENT_NAME:
            return PLANNER_AGENT_NAME

        # If any specialist agent spoke, Planner must process the result.
        specialist_agents = {PRODUCT_AGENT_NAME, PRICE_AGENT_NAME, HUBSPOT_AGENT_NAME}
        if last_message.source in specialist_agents:
            return PLANNER_AGENT_NAME

        # If the Planner just spoke, let the LLM decide the next step
        # (could be another delegation or concluding with <UserProxyAgent>, TASK COMPLETE, or TASK FAILED)
        if last_message.source == PLANNER_AGENT_NAME:
            return None

        # Fallback: let LLM decide (should be rare)
        print(f"Selector: Fallback (Last Source: {last_message.source}) -> {PLANNER_AGENT_NAME}")
        return None

    # Start or continue a chat session
    async def run_chat_session(self, user_message: str, show_console: bool = False, conversation_id: Optional[str] = None) -> tuple[Optional[TaskResult], Optional[str], Optional[str]]:
        """Runs or continues a chat session using the SHARED group_chat instance and agents, handling state."""
        if not AgentService._initialized or not AgentService.model_client:
            return None, "AgentService shared state (client) not initialized properly.", conversation_id

        task_result = None
        error_message = None
        current_conversation_id = conversation_id
        group_chat: Optional[SelectorGroupChat] = None # Will be instantiated per request
        saved_state_dict: Optional[Dict] = None

        try:
            # --- Ensure Conversation ID --- #
            if not current_conversation_id:
                current_conversation_id = str(uuid.uuid4())
                print(f"<--- Starting new conversation with ID: {current_conversation_id} --->")
            else:
                # --- Attempt to Load State --- #
                if current_conversation_id in AgentService.conversation_states:
                    print(f"<--- Loading state for conversation ID: {current_conversation_id} --->")
                    saved_state_dict = AgentService.conversation_states[current_conversation_id]
                else:
                    # ID provided, but no state found - treat as new conversation with this ID
                    print(f"<--- New conversation started with provided ID: {current_conversation_id} (no prior state found) --->")

            # --- Create GroupChat Instance for this request --- #
            active_participants = [
                AgentService.agents_dict[PLANNER_AGENT_NAME],
                AgentService.agents_dict[PRICE_AGENT_NAME],
                AgentService.agents_dict[PRODUCT_AGENT_NAME],
                AgentService.agents_dict[HUBSPOT_AGENT_NAME],
            ]
            group_chat = SelectorGroupChat(
                participants=active_participants,
                model_client=AgentService.model_client,
                termination_condition=AgentService._get_termination_condition(),
                allow_repeated_speaker=False,
                selector_func=AgentService.custom_speaker_selector,
            )

            # --- Load state into the NEW instance if it exists --- #
            if saved_state_dict:
                try:
                    await group_chat.load_state(saved_state_dict)
                    print(f"--- State loaded successfully into new chat instance. ---")
                except Exception as load_err:
                    error_message = f"Error loading state into new chat instance for {current_conversation_id}: {load_err}. Starting fresh."
                    print(f"!!! {error_message}")
                    await group_chat.reset() # Reset the new instance
                    # Optionally clear the invalid state from storage
                    AgentService.conversation_states.pop(current_conversation_id, None)

            # --- Prepare the next message --- #
            # The user_message represents the *next* input in the conversation
            # Manually create a message with the expected source name for the selector
            # Use TextMessage instead of UserMessage to avoid potential type issues with run_stream
            next_message = TextMessage(content=user_message, source=USER_PROXY_AGENT_NAME)

            cancellation_token = CancellationToken()

            if show_console:
                # Pass task as a list containing the single message
                task_result = await Console(group_chat.run_stream(task=next_message, cancellation_token=cancellation_token))
            else:
                # Run the chat. The `next_message` kicks off the next round.
                task_result = await group_chat.run(task=next_message, cancellation_token=cancellation_token)

            # --- Save State --- #
            # Save state from the instance we just ran
            final_state_dict = await group_chat.save_state()
            AgentService.conversation_states[current_conversation_id] = final_state_dict
            print(f"<--- Saved state for conversation ID: {current_conversation_id} --->")

        except Exception as e:
            error_message = f"Error during AutoGen task execution: {e}"
            print(f"\n\n!!! {error_message}")
            traceback.print_exc()
            task_result = None # Ensure result is None on error

        # Return result, error, and the ID used (new or existing)
        return task_result, error_message, current_conversation_id

    # --- Client Closing ---
    @classmethod
    async def close_client(cls):
        """Closes the shared underlying model client connection."""
        if cls.model_client:
            try:
                await cls.model_client.close()
                cls.model_client = None
                print("--- Shared Model Client closed successfully. ---")
            except Exception as e:
                print(f"--- Error closing shared model client: {e} ---")
        else:
            print("--- Shared Model Client already closed or never initialized. ---")


# --- Perform One-Time Initialization on Module Import ---
# Ensure this runs reliably
try:
    AgentService._initialize_shared_state()
except Exception as init_err:
     print(f"!!! FAILED to initialize AgentService state on module import: {init_err}")
     # Decide if the application should stop or continue in a degraded state

# --- Create an instance for convenience ---
agent_service = AgentService()