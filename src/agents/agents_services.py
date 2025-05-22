"""Centralized service for managing agent interactions and state."""

# /src/agents/agents_services.py
import traceback
import uuid  # Added for generating conversation IDs
import re  # Import regex module
from typing import Sequence, Optional, Dict, Union, ClassVar, Any

# AutoGen imports
from autogen_agentchat.ui import Console
from autogen_core.memory import ListMemory, MemoryContent, MemoryMimeType
from autogen_agentchat.agents import UserProxyAgent, AssistantAgent
from autogen_agentchat.base import TaskResult
from autogen_agentchat.conditions import (
    MaxMessageTermination,
    FunctionCallTermination,
    TextMentionTermination,
)
from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage, TextMessage
from autogen_agentchat.teams import SelectorGroupChat
from autogen_core import CancellationToken
from autogen_core.models import ModelInfo
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Agents
from src.agents.hubspot.hubspot_agent import create_hubspot_agent
from src.agents.planner.planner_agent import create_planner_agent
from src.agents.price_quote.price_quote_agent import create_price_quote_agent
from src.agents.product.product_agent import create_product_agent

# Import Agent Name
from src.agents.agent_names import (
    HUBSPOT_AGENT_NAME,
    PRICE_QUOTE_AGENT_NAME,
    PRODUCT_AGENT_NAME,
    PLANNER_AGENT_NAME,
    USER_PROXY_AGENT_NAME,
)

# Config imports
from config import (
    HUBSPOT_AS_STAGE_ID,
    HUBSPOT_DEFAULT_CHANNEL,
    HUBSPOT_DEFAULT_CHANNEL_ACCOUNT,
    HUBSPOT_DEFAULT_INBOX,
    HUBSPOT_DEFAULT_SENDER_ACTOR_ID,
    HUBSPOT_PIPELINE_ID_ASSISTED_SALES,
    HUBSPOT_PIPELINE_ID_CUSTOMER_SUCCESS,
    HUBSPOT_PIPELINE_ID_PROMO_RESELLER,
    LLM_BASE_URL,
    LLM_API_KEY,
    LLM_PRIMARY_MODEL_NAME,
    LLM_PRIMARY_MODEL_FAMILY,
    LLM_SECONDARY_MODEL_NAME,
    LLM_SECONDARY_MODEL_FAMILY,
)

# Define AgentType alias for clarity
AgentType = Union[AssistantAgent, UserProxyAgent]


class AgentService:
    """
    Manages the setup and execution of AutoGen chat sessions using shared class attributes
    to ensure shared state (model client, agents) across all instances.
    """

    # --- Class Attributes for Shared State ---
    primary_model_client: ClassVar[Optional[OpenAIChatCompletionClient]] = None
    secondary_model_client: ClassVar[Optional[OpenAIChatCompletionClient]] = None

    conversation_states: ClassVar[Dict[str, Any]] = (
        {}
    )  # In-memory state store (stores state dicts)

    _initialized: ClassVar[bool] = False  # Flag for one-time initialization

    # --- Initialization Method ---
    @staticmethod
    def initialize_shared_state():
        """Initializes the shared class attributes ONCE."""

        if AgentService._initialized:
            print("\n!!! AgentService already initialized. Skipping. !!!")
            return

        try:
            # Create primary model client
            AgentService.primary_model_client = OpenAIChatCompletionClient(
                model=LLM_PRIMARY_MODEL_NAME,
                base_url=LLM_BASE_URL,
                api_key=LLM_API_KEY,
                temperature=0,
                timeout=600,
                model_info=ModelInfo(
                    vision=False,
                    function_calling=True,
                    json_output=False,
                    family=LLM_PRIMARY_MODEL_FAMILY,
                    structured_output=True,
                    multiple_system_messages=True,
                ),
            )

            # Create secondary model client
            AgentService.secondary_model_client = OpenAIChatCompletionClient(
                model=LLM_SECONDARY_MODEL_NAME,
                base_url=LLM_BASE_URL,
                api_key=LLM_API_KEY,
                temperature=0,
                timeout=600,
                model_info=ModelInfo(
                    vision=False,
                    function_calling=True,
                    json_output=False,
                    family=LLM_SECONDARY_MODEL_FAMILY,
                    structured_output=True,
                    multiple_system_messages=True,
                ),
            )

            AgentService._initialized = True

        except Exception as e:
            print(
                f"\n\n!!! CRITICAL ERROR during AgentService shared state initialization: {e}"
            )
            traceback.print_exc()

            # Reset state on failure
            AgentService.primary_model_client = None
            AgentService.secondary_model_client = None
            AgentService.conversation_states = {}
            AgentService._initialized = False
            raise e

    # --- Constructor ---
    def __init__(self):
        # Ensure shared state is initialized if it hasn't been already
        if not AgentService._initialized:
            AgentService.initialize_shared_state()

    # Termination Condition
    @staticmethod
    def get_text_termination_condition():
        """Helper to define the termination condition using string mentions."""
        return (
            TextMentionTermination("TASK FAILED")
            | TextMentionTermination("TASK COMPLETE")
            | TextMentionTermination("<UserProxyAgent>")
            | TextMentionTermination(f"<{USER_PROXY_AGENT_NAME}>")
        )

    @staticmethod
    def get_termination_condition():
        """Helper to define the termination condition using FunctionCallTermination."""
        # Terminate after 30 messages
        max_message_termination = MaxMessageTermination(max_messages=30)
        # Terminate when the Planner calls 'end_planner_turn'
        function_call_termination = FunctionCallTermination(
            function_name="end_planner_turn"
        )
        # Combine the conditions
        return max_message_termination | AgentService.get_text_termination_condition()

    # --- Core Agent Logic Methods ---

    # Next speaker selector
    @staticmethod
    def custom_speaker_selector(
        messages: Sequence[BaseAgentEvent | BaseChatMessage],
    ) -> str | None:
        """Determines the next speaker based on explicit rules and message content.

        Rules:
        1. If the last message is from the User Proxy, the Planner must speak next.
        2. If the last message is from a Specialist Agent (SY, Product, HubSpot),
           the Planner must speak next to process the result.
        3. If the last message is from the Planner:
           a. Check if it contains a delegation pattern like '<agent_name> : Call ...'.
           b. If yes, and 'agent_name' is a known Specialist Agent, that agent speaks next.
           c. If no delegation is found (e.g., the message ends with '<UserProxyAgent>' or is a question),
              the User Proxy speaks next (signalling the end of the turn).
        4. Fallback: If none of the above, let the LLM decide (should be rare).
        """
        if not AgentService._initialized:
            print(
                "<- WARN: custom_speaker_selector called before AgentService fully initialized. Defaulting to Planner."
            )
            return PLANNER_AGENT_NAME

        # Ensure messages list is not empty
        if not messages:
            print("Selector: No messages, defaulting to Planner.")
            return PLANNER_AGENT_NAME

        last_message = messages[-1]

        # Rule 1: User Proxy spoke -> Planner processes
        if last_message.source == USER_PROXY_AGENT_NAME:
            # print("Selector: User spoke, Planner next.")
            return PLANNER_AGENT_NAME

        # Rule 2: Specialist spoke -> Planner processes
        specialist_agents = {PRODUCT_AGENT_NAME, PRICE_QUOTE_AGENT_NAME, HUBSPOT_AGENT_NAME}
        if last_message.source in specialist_agents:
            # print(f"Selector: Specialist {last_message.source} spoke, Planner next.")
            return PLANNER_AGENT_NAME

        # Rule 3: Planner spoke -> Check for delegation or end of turn
        if last_message.source == PLANNER_AGENT_NAME:
            # Ensure content is a string before processing
            if isinstance(last_message.content, str):
                content = last_message.content.strip()
                # Regex: Matches '<', then captures word characters (\w+?), then '>' at the start.
                match = re.match(r"^<(\w+?)>", content)

                if match:
                    delegated_agent_name = match.group(1)  # Extracts the name inside <>

                    if delegated_agent_name == PRODUCT_AGENT_NAME:
                        return PRODUCT_AGENT_NAME
                    elif delegated_agent_name == PRICE_QUOTE_AGENT_NAME:
                        return PRICE_QUOTE_AGENT_NAME
                    elif delegated_agent_name == HUBSPOT_AGENT_NAME:
                        return HUBSPOT_AGENT_NAME
                    else:
                        print(
                            f"<- WARN: Selector found delegation pattern but agent '{delegated_agent_name}' is unknown. Defaulting to Planner."
                        )
                        return PLANNER_AGENT_NAME  # Fallback if agent name invalid
                else:
                    # Planner spoke, but no delegation found. Let LLM decide
                    # print("Selector: Planner spoke, no delegation found. Letting LLM decide (likely pause for user)." )
                    return None
            else:
                # Planner message content is not a string, unexpected.
                return None

        # Rule 4: Fallback - Let LLM decide (should be hit rarely now)
        # print(f"Selector: Fallback condition hit (Last speaker: {last_message.source}). Letting LLM decide.")
        return None

    # Start or continue a chat session
    async def run_chat_session(
        self,
        user_message: str,
        show_console: bool = False,
        conversation_id: Optional[str] = None,
    ) -> tuple[Optional[TaskResult], Optional[str], Optional[str]]:
        """Runs or continues a chat session using the SHARED group_chat instance and agents, handling state."""
        if (
            not AgentService._initialized
            or not AgentService.primary_model_client
            or not AgentService.secondary_model_client
        ):
            return (
                None,
                "AgentService shared state (clients) not initialized properly.",
                conversation_id,
            )

        task_result = None
        error_message = None
        current_conversation_id = conversation_id
        group_chat: Optional[SelectorGroupChat] = (
            None  # Will be instantiated per request
        )
        saved_state_dict: Optional[Dict] = None

        try:
            # --- Determine Conversation ID & Create Request Context --- #
            if not current_conversation_id:
                current_conversation_id = str(uuid.uuid4())
                # print(f"<--- Starting new conversation with ID: {current_conversation_id} --->")
            else:
                # --- Attempt to Load State --- #
                if current_conversation_id in AgentService.conversation_states:
                    # print(f"<--- Loading state for conversation ID: {current_conversation_id} --->")
                    saved_state_dict = AgentService.conversation_states[
                        current_conversation_id
                    ]
                else:
                    # ID provided, but no state found - treat as new conversation with this ID
                    print(
                        f"<--- New conversation started with provided ID: {current_conversation_id} (no prior state found) --->"
                    )

            # Create memory for this request, containing the conversation ID
            request_memory = ListMemory()
            await request_memory.add(
                MemoryContent(
                    content=f"Current_HubSpot_Thread_ID: {current_conversation_id}",
                    mime_type=MemoryMimeType.TEXT,
                    metadata={"priority": "critical", "source": "hubspot"},
                )
            )
            
            if HUBSPOT_DEFAULT_SENDER_ACTOR_ID:
                await request_memory.add(
                    MemoryContent(
                        content=f"Default_HubSpot_Sender_Actor_ID: {HUBSPOT_DEFAULT_SENDER_ACTOR_ID}",
                        mime_type=MemoryMimeType.TEXT,
                        metadata={"priority": "normal", "source": "system_config_hubspot_defaults"},
                    )
                )
            if HUBSPOT_DEFAULT_CHANNEL:
                await request_memory.add(
                    MemoryContent(
                        content=f"Default_HubSpot_Channel_ID: {HUBSPOT_DEFAULT_CHANNEL}",
                        mime_type=MemoryMimeType.TEXT,
                        metadata={"priority": "normal", "source": "system_config_hubspot_defaults"},
                    )
                )
            if HUBSPOT_DEFAULT_CHANNEL_ACCOUNT:
                await request_memory.add(
                    MemoryContent(
                        content=f"Default_HubSpot_Channel_Account_ID: {HUBSPOT_DEFAULT_CHANNEL_ACCOUNT}",
                        mime_type=MemoryMimeType.TEXT,
                        metadata={"priority": "normal", "source": "system_config_hubspot_defaults"},
                    )
                )
            if HUBSPOT_DEFAULT_INBOX:
                await request_memory.add(
                    MemoryContent(
                        content=f"Default_HubSpot_Inbox_ID: {HUBSPOT_DEFAULT_INBOX}",
                        mime_type=MemoryMimeType.TEXT,
                        metadata={"priority": "normal", "source": "system_config_hubspot_defaults"},
                    )
                )

            # Add Pipeline and Stage IDs
            if HUBSPOT_PIPELINE_ID_ASSISTED_SALES:
                await request_memory.add(
                    MemoryContent(
                        content=f"HubSpot_Pipeline_ID_Assisted_Sales: {HUBSPOT_PIPELINE_ID_ASSISTED_SALES}",
                        mime_type=MemoryMimeType.TEXT,
                        metadata={"priority": "normal", "source": "system_config_hubspot_pipelines"},
                    )
                )
            if HUBSPOT_AS_STAGE_ID: # Assisted Sales Stage ID
                await request_memory.add(
                    MemoryContent(
                        content=f"HubSpot_Assisted_Sales_Stage_ID_New_Request: {HUBSPOT_AS_STAGE_ID}",
                        mime_type=MemoryMimeType.TEXT,
                        metadata={"priority": "normal", "source": "system_config_hubspot_pipelines"},
                    )
                )
            if HUBSPOT_PIPELINE_ID_PROMO_RESELLER:
                await request_memory.add(
                    MemoryContent(
                        content=f"HubSpot_Pipeline_ID_Promo_Reseller: {HUBSPOT_PIPELINE_ID_PROMO_RESELLER}",
                        mime_type=MemoryMimeType.TEXT,
                        metadata={"priority": "normal", "source": "system_config_hubspot_pipelines"},
                    )
                )
            if HUBSPOT_PIPELINE_ID_CUSTOMER_SUCCESS:
                await request_memory.add(
                    MemoryContent(
                        content=f"HubSpot_Pipeline_ID_Customer_Success: {HUBSPOT_PIPELINE_ID_CUSTOMER_SUCCESS}",
                        mime_type=MemoryMimeType.TEXT,
                        metadata={"priority": "normal", "source": "system_config_hubspot_pipelines"},
                    )
                )

            # --- Create Agent Instances for this request --- #
            # Planner uses the primary (more capable) model
            planner_assistant = create_planner_agent(
                AgentService.primary_model_client, memory=[request_memory]
            )
            # Other agents use the secondary model
            hubspot_agent = create_hubspot_agent(
                AgentService.secondary_model_client, memory=[request_memory]
            )
            price_quote_agent = create_price_quote_agent(AgentService.primary_model_client)
            product_agent = await create_product_agent(
                AgentService.secondary_model_client
            )

            # --- Create GroupChat Instance for this request --- #
            active_participants = [
                planner_assistant,
                price_quote_agent,
                product_agent,
                hubspot_agent,
            ]
            group_chat = SelectorGroupChat(
                participants=active_participants,
                model_client=AgentService.primary_model_client,
                termination_condition=AgentService.get_termination_condition(),
                allow_repeated_speaker=False,
                selector_func=AgentService.custom_speaker_selector,
            )

            # --- Load state into the NEW instance if it exists --- #
            if saved_state_dict:
                try:
                    await group_chat.load_state(saved_state_dict)
                except Exception as load_err:
                    error_message = f"Error loading state into new chat instance for {current_conversation_id}: {load_err}. Starting fresh."
                    print(f"    - WARN: {error_message}")
                    await group_chat.reset()  # Reset the new instance
                    # Clear the invalid state from storage
                    AgentService.conversation_states.pop(current_conversation_id, None)

            # --- Prepare the next message --- #
            # The user_message represents the *next* input in the conversation
            # Manually create a message with the expected source name for the selector
            # Use TextMessage instead of UserMessage to avoid potential type issues with run_stream
            next_message = TextMessage(
                content=user_message, source=USER_PROXY_AGENT_NAME
            )

            cancellation_token = CancellationToken()

            # Run the chat - use run() for API flow, run_stream() wrapped in Console for terminal
            if show_console:
                task_result = await Console(
                    group_chat.run_stream(
                        task=next_message, cancellation_token=cancellation_token
                    )
                )
            else:
                # Run the chat. The `next_message` kicks off the next round.
                task_result = await group_chat.run(
                    task=next_message, cancellation_token=cancellation_token
                )

            # --- Save State --- #
            # Save state from the instance we just ran
            final_state_dict = await group_chat.save_state()
            AgentService.conversation_states[current_conversation_id] = final_state_dict

        except Exception as e:
            error_message = f"Error during AutoGen task execution: {e}"
            print(f"\n\n!!! {error_message}")
            traceback.print_exc()
            task_result = None  # Ensure result is None on error

        # Return result, error, and the ID used (new or existing)
        return task_result, error_message, current_conversation_id

    # --- Client Closing ---
    @classmethod
    async def close_client(cls):
        """Closes the shared underlying model client connection."""
        closed_primary = False
        closed_secondary = False

        if cls.primary_model_client:
            try:
                await cls.primary_model_client.close()
                cls.primary_model_client = None
                print("\n--- Shared Primary Model Client closed successfully. ---")
                closed_primary = True
            except Exception as e:
                print(f"\n--- Error closing shared Primary Model Client: {e} ---")
        else:
            print(
                "--- Shared Primary Model Client already closed or never initialized. ---"
            )
            closed_primary = (
                True  # Considered 'closed' if never initialized or already None
            )

        if cls.secondary_model_client:
            try:
                await cls.secondary_model_client.close()
                cls.secondary_model_client = None
                print("\n--- Shared Secondary Model Client closed successfully. ---")
                closed_secondary = True
            except Exception as e:
                print(f"\n--- Error closing shared Secondary Model Client: {e} ---")
        else:
            print(
                "--- Shared Secondary Model Client already closed or never initialized. ---"
            )
            closed_secondary = (
                True  # Considered 'closed' if never initialized or already None
            )

        # Optionally, reset the main initialized flag if both are successfully closed or were not set
        if closed_primary and closed_secondary:
            cls._initialized = (
                False  # Or handle this based on desired re-initialization logic
            )


# --- Perform One-Time Initialization on Module Import ---
# Ensure this runs reliably
try:
    AgentService.initialize_shared_state()
except Exception as init_err:
    print(f"!!! FAILED to initialize AgentService state on module import: {init_err}")
    # Decide if the application should stop or continue in a degraded state

# --- Create an instance for convenience ---
agent_service = AgentService()
