"""Main CLI interface for the agent chatbot."""

# main.py
import asyncio
import json
import traceback
from typing import Optional

# --- Third Party Imports ---
import asyncio

# Import specific message types
from autogen_agentchat.messages import (
    BaseChatMessage,
    ToolCallExecutionEvent,
    TextMessage,
    ThoughtEvent,
)

# --- First Party Imports ---
# Centralized Agent Service
from src.agents.agents_services import (
    agent_service,
    AgentService,
)  # Keep AgentService for close_client
from src.agents.agent_names import (
    PLANNER_AGENT_NAME,
    USER_PROXY_AGENT_NAME,
)  # Ensure UserProxyAgent is also available if needed for prompts


# --- --- Main Execution --- --- #
async def main_cli():
    """Main CLI loop for interacting with the AgentService."""
    print("--- AutoGen Agent Chat CLI ---")
    print("Type 'exit' or 'quit' to end the session.")
    print("A new conversation will start if no ID is provided or found.")
    print("Continuing a conversation will load its previous state if an ID is entered.")

    conversation_id: Optional[str] = None

    try:
        while True:
            if conversation_id:
                prompt = f"User (ConvID: {conversation_id}): "
            else:
                prompt = f"User (New Conversation - or enter existing ID to continue): "

            user_input = input(prompt).strip()

            if user_input.lower() in ["exit", "quit"]:
                print("Exiting CLI.")
                break

            # Check if user entered a potential conversation ID to continue
            # This is a simple check; a more robust way might be a specific command
            if (
                not conversation_id and len(user_input) > 20 and "-" in user_input
            ):  # Basic check for UUID-like string
                try_conv_id = (
                    input(
                        f"It looks like you entered an ID. Continue with '{user_input}' as Conversation ID? (y/n): "
                    )
                    .strip()
                    .lower()
                )
                if try_conv_id == "y":
                    conversation_id = user_input
                    print(
                        f"Attempting to continue conversation with ID: {conversation_id}"
                    )
                    user_input = input(
                        f"Your message for {USER_PROXY_AGENT_NAME} (Conversation: {conversation_id}): "
                    ).strip()
                    if not user_input:
                        print(
                            "No message entered after setting ID. Please provide input."
                        )
                        continue
                # If not 'y', the original input will be treated as a new message for a new conversation

            if not user_input:
                print("No message entered. Try again or type 'exit'.")
                continue

            task_result, error_message, returned_conv_id = (
                await agent_service.run_chat_session(
                    user_message=user_input,
                    show_console=True,
                    conversation_id=conversation_id,
                )
            )

            if returned_conv_id:
                conversation_id = returned_conv_id

            if error_message:
                print(f"\n!!! CLI Error: {error_message}")
            elif task_result:
                # Output is largely handled by show_console=True in run_chat_session
                # but we can still print a final summary or stop reason if desired.
                # For now, the detailed log from show_console=True should suffice.
                # print(f"\n--- Task Result Summary ---")
                # print(f"Stop Reason: {task_result.stop_reason}")
                # if task_result.messages and hasattr(task_result.messages[-1], 'content'):
                #     print(f"Final Message from Planner: {task_result.messages[-1].content}")
                pass
            else:
                print("\n!!! Task finished without a clear result or error.")

    except KeyboardInterrupt:
        print("\n--- Session interrupted by user. Exiting. ---")
    except Exception as e:
        print(f"\n--- An unexpected error occurred in the CLI: {e} ---")
        traceback.print_exc()
    finally:
        print("--- Closing resources... ---")
        # Use the class method for closing, as AgentService instance might not be directly available
        # or the loop might exit before instance cleanup.
        await AgentService.close_client()
        print("--- CLI session ended. ---")


if __name__ == "__main__":
    asyncio.run(main_cli())
