"""Centralized service for managing agent interactions and state."""

# /src/agents/agents_services.py
from typing import Sequence, Optional, Dict, Union, ClassVar
import traceback
import uuid  # Added for generating conversation IDs
import re  # Import regex module
import json  # Add json import

from src.services.json_utils import json_serializer_default
from src.services.redis_client import get_redis_client
from src.services.logger_config import log_message

# AutoGen imports
from autogen_agentchat.ui import Console
from autogen_core.memory import ListMemory, MemoryContent, MemoryMimeType
from autogen_agentchat.agents import UserProxyAgent, AssistantAgent
from autogen_agentchat.base import TaskResult
from autogen_agentchat.conditions import (
    MaxMessageTermination,
    TextMentionTermination,
)
from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage, TextMessage
from autogen_agentchat.teams import SelectorGroupChat
from autogen_core import CancellationToken
from autogen_core.models import ModelInfo
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Agents
from src.agents.hubspot.hubspot_agent import create_hubspot_agent
from src.agents.orders.order_agent import create_order_agent
from src.agents.planner.planner_agent import create_planner_agent
from src.agents.price_quote.price_quote_agent import create_price_quote_agent
from src.agents.sticker_you.sticker_you_agent import create_sticker_you_agent
from src.agents.live_product.live_product_agent import create_live_product_agent

# Import Agent Name
from src.agents.agent_names import (
    HUBSPOT_AGENT_NAME,
    ORDER_AGENT_NAME,
    PRICE_QUOTE_AGENT_NAME,
    PLANNER_AGENT_NAME,
    USER_PROXY_AGENT_NAME,
    STICKER_YOU_AGENT_NAME,
    LIVE_PRODUCT_AGENT_NAME,
)

# Config imports
from config import (
    HUBSPOT_AS_STAGE_ID,
    HUBSPOT_CS_STAGE_ID,
    HUBSPOT_DEFAULT_CHANNEL,
    HUBSPOT_DEFAULT_CHANNEL_ACCOUNT,
    HUBSPOT_DEFAULT_INBOX,
    HUBSPOT_DEFAULT_SENDER_ACTOR_ID,
    HUBSPOT_PIPELINE_ID_ASSISTED_SALES,
    HUBSPOT_PIPELINE_ID_CUSTOMER_SUCCESS,
    HUBSPOT_PIPELINE_ID_PROMO_RESELLER,
    HUBSPOT_PR_STAGE_ID,
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

    _initialized: ClassVar[bool] = False  # Flag for one-time initialization

    # Agents (initialized once)
    user_proxy: ClassVar[Optional[UserProxyAgent]] = None
    planner_agent: ClassVar[Optional[AssistantAgent]] = None
    sticker_you_agent: ClassVar[Optional[AssistantAgent]] = None
    live_product_agent: ClassVar[Optional[AssistantAgent]] = None
    price_quote_agent: ClassVar[Optional[AssistantAgent]] = None
    hubspot_agent: ClassVar[Optional[AssistantAgent]] = None
    order_agent: ClassVar[Optional[AssistantAgent]] = None

    # --- Initialization Method ---
    @staticmethod
    def initialize_shared_state():
        """Initializes the shared class attributes ONCE."""

        if AgentService._initialized:
            log_message("AgentService already initialized. Skipping.", level=2, prefix="!!!")
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
            log_message(
                f"CRITICAL ERROR during AgentService shared state initialization: {e}",
                log_type="error",
                prefix="!!!",
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
            | TextMentionTermination(f"<{USER_PROXY_AGENT_NAME}>")
        )

    @staticmethod
    def get_termination_condition():
        """Helper to define the termination condition using FunctionCallTermination."""
        # Terminate after 30 messages
        max_message_termination = MaxMessageTermination(max_messages=30)
        # Terminate when the Planner calls 'end_planner_turn'
        # function_call_termination = FunctionCallTermination(
        #     function_name="end_planner_turn"
        # )
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
            log_message(
                "<- WARN: custom_speaker_selector called before AgentService fully initialized. Defaulting to Planner.",
                log_type="warning",
            )
            return PLANNER_AGENT_NAME

        # Ensure messages list is not empty
        if not messages:
            log_message("Selector: No messages, defaulting to Planner.", level=2)
            return PLANNER_AGENT_NAME

        last_message = messages[-1]

        # Rule 1: User Proxy spoke -> Planner processes
        if last_message.source == USER_PROXY_AGENT_NAME:
            return PLANNER_AGENT_NAME

        # Rule 2: Specialist spoke -> Planner processes
        specialist_agents = {
            PRICE_QUOTE_AGENT_NAME,
            STICKER_YOU_AGENT_NAME,
            LIVE_PRODUCT_AGENT_NAME,
            HUBSPOT_AGENT_NAME,
            ORDER_AGENT_NAME,
        }
        if last_message.source in specialist_agents:
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

                    if delegated_agent_name == PRICE_QUOTE_AGENT_NAME:
                        return PRICE_QUOTE_AGENT_NAME
                    elif delegated_agent_name == STICKER_YOU_AGENT_NAME:
                        return STICKER_YOU_AGENT_NAME
                    elif delegated_agent_name == LIVE_PRODUCT_AGENT_NAME:
                        return LIVE_PRODUCT_AGENT_NAME
                    elif delegated_agent_name == HUBSPOT_AGENT_NAME:
                        return HUBSPOT_AGENT_NAME
                    elif delegated_agent_name == ORDER_AGENT_NAME:
                        return ORDER_AGENT_NAME
                    else:
                        log_message(
                            f"<- WARN: Selector found delegation pattern but agent '{delegated_agent_name}' is unknown. Defaulting to Planner.",
                            log_type="warning",
                        )
                        return PLANNER_AGENT_NAME  # Fallback if agent name invalid
                else:
                    return None
            else:
                # Planner message content is not a string, unexpected.
                return None

        # Rule 4: Fallback - Let LLM decide (should be hit rarely now)
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
            else:
                # --- Attempt to Load State from Redis --- #
                async with get_redis_client() as redis:
                    # Prefix keys for good practice, e.g., "conv_state:<id>"
                    redis_key = f"conv_state:{current_conversation_id}"
                    saved_state_json = await redis.get(redis_key)
                    if saved_state_json:
                        saved_state_dict = json.loads(saved_state_json)
                    else:
                        # ID provided, but no state found - treat as new conversation with this ID
                        log_message(
                            f"<--- New conversation started with provided ID: {current_conversation_id} (no prior state found) --->",
                            level=1,
                        )
                        saved_state_dict = None

            # Create memory for this request, containing the conversation ID
            planner_memory = ListMemory()
            await planner_memory.add(
                MemoryContent(
                    content=f"Current_HubSpot_Thread_ID: {current_conversation_id}",
                    mime_type=MemoryMimeType.TEXT,
                    metadata={"priority": "critical", "source": "hubspot"},
                )
            )

            hubspot_agent_memory = ListMemory()
            await hubspot_agent_memory.add(
                MemoryContent(
                    content=f"Current_HubSpot_Thread_ID: {current_conversation_id}",
                    mime_type=MemoryMimeType.TEXT,
                    metadata={"priority": "critical", "source": "hubspot"},
                )
            )

            if HUBSPOT_DEFAULT_SENDER_ACTOR_ID:
                await hubspot_agent_memory.add(
                    MemoryContent(
                        content=f"Default_HubSpot_Sender_Actor_ID: {HUBSPOT_DEFAULT_SENDER_ACTOR_ID}",
                        mime_type=MemoryMimeType.TEXT,
                        metadata={
                            "priority": "normal",
                            "source": "system_config_hubspot_defaults",
                        },
                    )
                )
            if HUBSPOT_DEFAULT_CHANNEL:
                await hubspot_agent_memory.add(
                    MemoryContent(
                        content=f"Default_HubSpot_Channel_ID: {HUBSPOT_DEFAULT_CHANNEL}",
                        mime_type=MemoryMimeType.TEXT,
                        metadata={
                            "priority": "normal",
                            "source": "system_config_hubspot_defaults",
                        },
                    )
                )
            if HUBSPOT_DEFAULT_CHANNEL_ACCOUNT:
                await hubspot_agent_memory.add(
                    MemoryContent(
                        content=f"Default_HubSpot_Channel_Account_ID: {HUBSPOT_DEFAULT_CHANNEL_ACCOUNT}",
                        mime_type=MemoryMimeType.TEXT,
                        metadata={
                            "priority": "normal",
                            "source": "system_config_hubspot_defaults",
                        },
                    )
                )
            if HUBSPOT_DEFAULT_INBOX:
                await hubspot_agent_memory.add(
                    MemoryContent(
                        content=f"Default_HubSpot_Inbox_ID: {HUBSPOT_DEFAULT_INBOX}",
                        mime_type=MemoryMimeType.TEXT,
                        metadata={
                            "priority": "normal",
                            "source": "system_config_hubspot_defaults",
                        },
                    )
                )

            # Add Pipeline and Stage IDs to HubSpot agent's memory
            if HUBSPOT_PIPELINE_ID_ASSISTED_SALES:
                await hubspot_agent_memory.add(
                    MemoryContent(
                        content=f"HubSpot_Pipeline_ID_Assisted_Sales: {HUBSPOT_PIPELINE_ID_ASSISTED_SALES}",
                        mime_type=MemoryMimeType.TEXT,
                        metadata={
                            "priority": "normal",
                            "source": "system_config_hubspot_pipelines",
                        },
                    )
                )
            if HUBSPOT_AS_STAGE_ID:  # Assisted Sales Stage ID
                await hubspot_agent_memory.add(
                    MemoryContent(
                        content=f"HubSpot_Assisted_Sales_Stage_ID: {HUBSPOT_AS_STAGE_ID}",
                        mime_type=MemoryMimeType.TEXT,
                        metadata={
                            "priority": "normal",
                            "source": "system_config_hubspot_pipelines",
                        },
                    )
                )
            if HUBSPOT_PIPELINE_ID_PROMO_RESELLER:
                await hubspot_agent_memory.add(
                    MemoryContent(
                        content=f"HubSpot_Pipeline_ID_Promo_Reseller: {HUBSPOT_PIPELINE_ID_PROMO_RESELLER}",
                        mime_type=MemoryMimeType.TEXT,
                        metadata={
                            "priority": "normal",
                            "source": "system_config_hubspot_pipelines",
                        },
                    )
                )
            if HUBSPOT_PR_STAGE_ID:  # Promo Reseller Stage ID
                await hubspot_agent_memory.add(
                    MemoryContent(
                        content=f"HubSpot_Promo_Reseller_Stage_ID: {HUBSPOT_PR_STAGE_ID}",
                        mime_type=MemoryMimeType.TEXT,
                        metadata={
                            "priority": "normal",
                            "source": "system_config_hubspot_pipelines",
                        },
                    )
                )
            if HUBSPOT_PIPELINE_ID_CUSTOMER_SUCCESS:
                await hubspot_agent_memory.add(
                    MemoryContent(
                        content=f"HubSpot_Pipeline_ID_Customer_Success: {HUBSPOT_PIPELINE_ID_CUSTOMER_SUCCESS}",
                        mime_type=MemoryMimeType.TEXT,
                        metadata={
                            "priority": "normal",
                            "source": "system_config_hubspot_pipelines",
                        },
                    )
                )
            if HUBSPOT_CS_STAGE_ID:  # Customer Success Stage ID
                await hubspot_agent_memory.add(
                    MemoryContent(
                        content=f"HubSpot_Customer_Success_Stage_ID: {HUBSPOT_CS_STAGE_ID}",
                        mime_type=MemoryMimeType.TEXT,
                        metadata={
                            "priority": "normal",
                            "source": "system_config_hubspot_pipelines",
                        },
                    )
                )

            # Initialize all agents
            planner_agent = create_planner_agent(
                AgentService.primary_model_client, planner_memory
            )
            sticker_you_agent = create_sticker_you_agent(
                AgentService.secondary_model_client
            )
            live_product_agent = create_live_product_agent(
                AgentService.secondary_model_client
            )
            price_quote_agent = create_price_quote_agent(
                AgentService.primary_model_client
            )
            hubspot_agent = create_hubspot_agent(
                AgentService.secondary_model_client, hubspot_agent_memory
            )
            order_agent = create_order_agent(AgentService.secondary_model_client)

            # --- Create GroupChat Instance for this request --- #
            active_participants = [
                planner_agent,
                sticker_you_agent,
                live_product_agent,
                price_quote_agent,
                hubspot_agent,
                order_agent,
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
                    log_message(f"    - WARN: {error_message}", log_type="warning")
                    await group_chat.reset()  # Reset the new instance

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

            # --- Save State to Redis --- #
            final_state_dict = await group_chat.save_state()
            async with get_redis_client() as redis:
                redis_key = f"conv_state:{current_conversation_id}"
                # Serialize the state dictionary to a JSON string
                final_state_json = json.dumps(final_state_dict, default=json_serializer_default)
                # Save to Redis with an expiration time
                # This prevents old conversations from cluttering Redis forever.
                await redis.set(
                    redis_key, final_state_json, ex=86400
                )  # 86400 seconds = 24 hours

        except Exception as e:
            error_message = f"Error during AutoGen task execution: {e}"
            log_message(f"!!! {error_message}", log_type="error", prefix="")
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
                closed_primary = True
            except Exception as e:
                log_message(f"Error closing shared Primary Model Client: {e}", log_type="error")
        else:
            closed_primary = (
                True  # Considered 'closed' if never initialized or already None
            )

        if cls.secondary_model_client:
            try:
                await cls.secondary_model_client.close()
                cls.secondary_model_client = None
                closed_secondary = True
            except Exception as e:
                log_message(f"Error closing shared Secondary Model Client: {e}", log_type="error")
        else:
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
    log_message(f"FAILED to initialize AgentService state on module import: {init_err}", log_type="error")
    # Decide if the application should stop or continue in a degraded state

# --- Create an instance for convenience ---
agent_service = AgentService()
