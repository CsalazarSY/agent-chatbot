# agent_service.py
import traceback
from typing import Sequence, Optional, Dict, Union, ClassVar

# AutoGen imports
from autogen_agentchat.agents import UserProxyAgent, AssistantAgent
from autogen_agentchat.base import TaskResult
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage, TextMessage
from autogen_agentchat.teams import SelectorGroupChat
from autogen_core import CancellationToken
from autogen_core.models import ModelInfo
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.ui import Console

# Agents
from agents.hubspot.hubspot_agent import create_hubspot_agent
from agents.planner.planner_agent import create_planner_agent
from agents.price.price_agent import create_price_agent
from agents.product.product_agent import create_product_agent

# Config imports
from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL_NAME

# Define AgentType alias for clarity
AgentType = Union[AssistantAgent, UserProxyAgent]

class AgentService:
    """
    Manages the setup and execution of AutoGen chat sessions using shared class attributes
    to ensure shared state (model client, agents) across all instances.
    """
    # --- Class Attributes for Shared State ---
    model_client: ClassVar[Optional[OpenAIChatCompletionClient]] = None
    agents_dict: ClassVar[Dict[str, AgentType]] = {}

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
            user_proxy = UserProxyAgent(name="user_proxy", description="Represents the user initiating the request.")
            planner_assistant = create_planner_agent(AgentService.model_client)
            price_assistant = create_price_agent(AgentService.model_client)
            product_agent = create_product_agent(AgentService.model_client)
            hubspot_agent = create_hubspot_agent(AgentService.model_client)

            # Create agents dictionary using agent names as keys
            AgentService.agents_dict = {
                user_proxy.name: user_proxy,
                planner_assistant.name: planner_assistant,
                price_assistant.name: price_assistant,
                product_agent.name: product_agent,
                hubspot_agent.name: hubspot_agent,
            }
            AgentService._initialized = True

        except Exception as e:
            print(f"\n\n!!! CRITICAL ERROR during AgentService shared state initialization: {e}")
            traceback.print_exc()
            
            # Reset state on failure
            AgentService.model_client = None
            AgentService.agents_dict = {}
            AgentService._initialized = False
            raise e

    # --- Constructor ---
    def __init__(self):
        # Ensure shared state is initialized if it hasn't been already
        # This makes it robust even if initialization below wasn't called/failed
        if not AgentService._initialized:
             AgentService._initialize_shared_state()
        pass


    # --- Core Agent Logic Methods (Instance Methods accessing Class State) ---
    # Note: These are instance methods, but access shared state via AgentService.attribute

    # Next speaker selector
    def custom_speaker_selector(self, messages: Sequence[BaseAgentEvent | BaseChatMessage]) -> Optional[str]:
        """Determines the next speaker based on rules using shared agents."""
        if not AgentService._initialized: return None # Guard clause
        last_message = messages[-1]

        # User -> Planner
        if last_message.source == AgentService.agents_dict["user_proxy"].name:
            return AgentService.agents_dict["planner_assistant"].name

        # Any other agent -> Planner
        other_agent_names = [
            AgentService.agents_dict["product_assistant"].name, 
            AgentService.agents_dict["price_assistant"].name, 
            AgentService.agents_dict["hubspot_assistant"].name
        ]
        if last_message.source in other_agent_names:
            return AgentService.agents_dict["planner_assistant"].name
        
        # Let the LLM decide
        return None

    # Start a chat session
    async def run_chat_session(self, user_message: str, show_console: bool = False) -> tuple[Optional[TaskResult], Optional[str]]:
        """Runs a chat session using the shared client and agents."""
        if not AgentService._initialized or not AgentService.model_client:
            return None, "AgentService shared state not initialized properly."

        task_result = None
        error_message = None
        try:
            # Initial task
            initial_task = TextMessage(content=user_message, source=AgentService.agents_dict["user_proxy"].name)

            # Cancel task configuration
            cancellation_token = CancellationToken()
            max_message_termination = MaxMessageTermination(max_messages=30)
            text_termination = TextMentionTermination("TASK FAILED") | TextMentionTermination("TASK COMPLETE") | TextMentionTermination("TERMINATE")
            termination_condition = max_message_termination | text_termination

            # Create group chat
            group_chat = SelectorGroupChat(
                participants=list(AgentService.agents_dict.values()),
                model_client=AgentService.model_client,
                termination_condition=termination_condition,
                allow_repeated_speaker=False,
                selector_func=self.custom_speaker_selector,
            )

            # Run chat session
            if show_console:
                task_result = await Console(group_chat.run_stream(task=initial_task, cancellation_token=cancellation_token))
            else:
                task_result = await group_chat.run(task=initial_task, cancellation_token=cancellation_token)

        except Exception as e:
            error_message = f"Error during AutoGen task execution: {e}"
            print(f"\n\n!!! {error_message}")
            traceback.print_exc()
            task_result = None
        
        return task_result, error_message

    # --- Client Closing ---
    @classmethod
    async def close_client(cls):
        """Closes the shared underlying model client connection."""
        if cls.model_client:
            try:
                await cls.model_client.close()
                cls.model_client = None
            except Exception as e:
                print(f"--- Error closing shared model client: {e} ---")
        else:
            print("--- Shared Model Client already closed or never initialized. ---")

# --- Perform One-Time Initialization on Module Import ---
AgentService._initialize_shared_state()

# --- Create an instance for convenience ---
# Although all instances share state, having a standard variable makes imports cleaner.
agent_service = AgentService()