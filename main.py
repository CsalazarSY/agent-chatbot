# main.py
import asyncio
import json
import traceback
from typing import Sequence

# AutoGen imports
from autogen_core import CancellationToken
from autogen_core.models import ModelInfo
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import UserProxyAgent
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination, HandoffTermination
from autogen_agentchat.messages import TextMessage, BaseAgentEvent, BaseChatMessage

# Import the agents
from agents.price.price_agent import create_price_agent
from agents.planner.planner_agent import create_planner_agent
from agents.product.product_agent import create_product_agent
from agents.hubspot.hubspot_agent import create_hubspot_agent

# Import Agent config variables
from config import LLM_MODEL_NAME, LLM_BASE_URL, LLM_API_KEY

# --- --- Main Execution --- --- #
async def main():
    # --- Define LLM Client Setup ---
    try:
        # Define the shared model client for the agents
        model_client = OpenAIChatCompletionClient(
            model=LLM_MODEL_NAME,
            base_url=LLM_BASE_URL,
            api_key=LLM_API_KEY,
            temperature=0,
            timeout=600,
            # Crucial for local models needing tool support hint and other platforms that are not OpenAI
            model_info=ModelInfo(
                vision=False,
                function_calling=True,  # Explicitly state function calling is expected
                json_output=False,  # Depending on model, might support True
                family="gpt-4o",
                structured_output=True  # If model supports structured output schemas
            ),
        )
        print(f"<- Agent Definition: Model client created for {LLM_MODEL_NAME}")

    except Exception as e:
        print(f"<- Agent Definition Error creating model client: {e}")
        raise ValueError("Could not create OpenAIChatCompletionClient for agent.")

    # --- Create Agents ---
    planner_assistant = create_planner_agent(model_client)
    price_assistant = create_price_agent(model_client)
    product_agent = create_product_agent(model_client)
    hubspot_agent = create_hubspot_agent(model_client)

    # User Agent
    user_proxy = UserProxyAgent(
        name="user",
        description="Represents the user initiating the request and providing information when asked by the PlannerAgent.",
    )

    # Agents list
    agent_list = [user_proxy, planner_assistant, product_agent, price_assistant, hubspot_agent]

    # --- --- Custom Speaker Selector Function --- ---
    def custom_speaker_selector(
            messages: Sequence[BaseAgentEvent | BaseChatMessage]
    ) -> (str | None):
        """
        Determines the next speaker based on last message and workflow rules, using agent name attributes.
        """
        last_message = messages[-1]

        # Rule 1: If last message is from user, Planner starts/resumes.
        if last_message.source == user_proxy.name:
            return planner_assistant.name

        # Rule 2: If last message is from a tool agent, Planner processes it.
        other_agents = [product_agent.name, price_assistant.name, hubspot_agent.name]
        if last_message.source in other_agents:
            return planner_assistant.name

        # Rule 3: If last message is from Planner
        if last_message.source == planner_assistant.name:
            return None

        # Default fallback if none of the above rules match - let the LLM choose based on description
        return None

    # --- --- End of Custom Speaker Selector Function --- ---

    # --- Define Task ---
    # Possible messages
    # 1. "Can you give me the price for 158 clear vinyl die-cut stickers? the size is 3x3 inches." # Match ID 30
    # 2. "How much for 200 glow-in-the-dark waterproof sized 4x4 inches?" # No match - Handoff trigger
    # 3. "Quote for durable roll labels" # Should ask for more input
    # 4. "Cost for stickers 3x3?" # Ambiguous need to refine the agents to ask
    initial_message_text = "Quote for durable roll labels" # Should ask for more input
    initial_task = TextMessage(content=initial_message_text, source=user_proxy.name)
    print(f"<- Initiating task with message: \"{initial_message_text}\"")
    print("\n---------------- Chat Start ------------------\n")

    # --- Cancellation config ---
    cancellation_token = CancellationToken()
    max_message_termination = MaxMessageTermination(max_messages=30)
    text_termination = TextMentionTermination("TASK FAILED") | TextMentionTermination("TASK COMPLETE") | TextMentionTermination("TERMINATE")
    handoff_termination = HandoffTermination(target=hubspot_agent.name)
    termination = max_message_termination | text_termination

    # --- Run task ---
    task_result = None # Initialize task_result
    try:
        # Define the group chat with LLM-based speaker selection
        # The RouterAgent's prompt guides selection via "NEXT: <AgentName>"
        group_chat = SelectorGroupChat(
            participants=agent_list,
            model_client=model_client,
            termination_condition=termination,
            allow_repeated_speaker=False,
            selector_func=custom_speaker_selector,
        )

        # Use agent.run_stream() with Console for real-time output
        # Console() will print the stream and return the final TaskResult
        task_result = await Console(
            group_chat.run_stream(
                task=initial_task,
                cancellation_token=cancellation_token
            )
        )

        print("\n---------------- Chat End --------------------\n")

    except asyncio.CancelledError:
        print("\n--- Task Cancelled ---")
    except Exception as e:
        print(f"\n\n!!! ERROR during task execution: {e} !!!")
        traceback.print_exc()
    finally:
        if model_client:
            try:
                # Use await for the async close method
                await model_client.close()
                print("\n--- Model client closed successfully ---")
            except Exception as e:
                print(f"\n--- Error closing model client: {e} ---")
        else:
            print("\n--- Model client was not initialized, skipping close ---")

    # --- Process Task Result ---
    print(f"\n\n\n\n\n <<<----------->>> Task Result Analysis <<<----------->>>")
    if task_result:
        print(f"    - Stop Reason: {task_result.stop_reason}")
        print(f"    - Number of Messages: {len(task_result.messages)}")

        # Check the final message
        if task_result.messages:
            final_message = task_result.messages[-1]
            # Extract content safely
            if hasattr(final_message, 'content'):
                 final_content = final_message.content if isinstance(final_message.content, str) else json.dumps(final_message.content)
            else:
                 final_content = f"[{type(final_message).__name__} with no 'content']"

            print(f"\n>>>> Final Message Content:\n{'-'*20}\n{final_content}\n{'-'*20}")

            # Check for handoff string in the final message content
            if isinstance(final_content, str) and final_content.startswith("HANDOFF:"):
                print("\n>>>> --- HANDOFF TRIGGERED --- <<<<")
                print(f"Reason: {final_content}")
            else:
                 # Check if stop reason indicates success or normal completion
                if task_result.stop_reason is None or "completed" in str(task_result.stop_reason).lower() or "finished" in str(task_result.stop_reason).lower():
                     print("\n>>> Task completed successfully without explicit HANDOFF trigger. <<<")
                else:
                     print(f"\n>>> Task stopped for reason: {task_result.stop_reason}. <<<")
        else:
            print("\n>>> No messages found in TaskResult. <<<")
    else:
         print("\n>>> TaskResult was not obtained (task might have error early). <<<")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
    except Exception as e:
         print(f"\n Top-level error: {e}")
         traceback.print_exc()
    finally:
        print("\n--- Script Finished ---")