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
# Corrected import path
from src.agents.agents_services import agent_service
from src.agents.agent_names import PLANNER_AGENT_NAME  # Import planner name


# --- --- Main Execution --- --- #
async def main():
    """
    Main execution loop for the chatbot in CLI mode.
    """
    # --- Define Task ---
    conversation_id: Optional[str] = None  # Initialize conversation ID
    task_result = None
    error_message = None

    while True:
        # Prompt user for input, showing conversation ID if it exists
        if conversation_id:
            prompt = f"User (ConvID: {conversation_id}): "
        else:
            prompt = "User: "
        user_input = input(prompt)

        if user_input.lower() == "exit":
            print("Exiting chat.")
            break

        try:
            print("\n")
            task_result, error_message, returned_conversation_id = (
                await agent_service.run_chat_session(
                    user_input, show_console=True, conversation_id=conversation_id
                )
            )
            conversation_id = (
                returned_conversation_id  # Update conversation_id for the next loop
            )
            print("\n")

            # --- Process and Display Result --- #
            if error_message:
                print(f"    ERROR: {error_message}")
            elif task_result:
                # print(f"    - Stop Reason: {task_result.stop_reason}")
                # --- Find the message BEFORE the final 'end_planner_turn' tool call --- #
                reply_message: Optional[BaseChatMessage] = None
                messages = task_result.messages
                end_turn_event_index = -1

                # Find the index of the end_planner_turn execution event
                for i in range(len(messages) - 1, -1, -1):
                    current_msg = messages[i]
                    if isinstance(current_msg, ToolCallExecutionEvent):
                        if any(
                            exec_result.name == "end_planner_turn"
                            for exec_result in getattr(current_msg, "content", [])
                            if hasattr(exec_result, "name")
                        ):
                            end_turn_event_index = i
                            break

                # Search backwards for the Planner's message
                if end_turn_event_index > 0:
                    for i in range(end_turn_event_index - 1, -1, -1):
                        potential_reply_msg = messages[i]
                        if (
                            potential_reply_msg.source == PLANNER_AGENT_NAME
                            and isinstance(
                                potential_reply_msg, (TextMessage, ThoughtEvent)
                            )
                        ):
                            reply_message = potential_reply_msg
                            break  # Found it

                # Fallback
                if not reply_message and messages:
                    print(
                        "    - WARN: Did not find Planner message before end_turn event. Falling back to last message for display."
                    )
                    reply_message = messages[-1]
                # --- End of Finding Reply Message --- #

                if reply_message and hasattr(reply_message, "content"):
                    final_content = (
                        reply_message.content
                        if isinstance(reply_message.content, str)
                        else json.dumps(reply_message.content)
                    )
                    # Clean up internal tags for display
                    display_reply = final_content.replace(
                        "<UserProxyAgent>", ""
                    ).strip()
                    if display_reply.startswith("TASK COMPLETE:"):
                        display_reply = display_reply[len("TASK COMPLETE:") :].strip()
                    if display_reply.startswith("TASK FAILED:"):
                        display_reply = display_reply[len("TASK FAILED:") :].strip()
                    print(f"Agent: {display_reply}")  # Print cleaned reply
                else:
                    print(f"Agent: [{type(reply_message).__name__} with no content]")
            else:
                print("    TaskResult was not obtained.")

        except asyncio.CancelledError:
            print("--- Task Cancelled --- ")
            break

        except Exception as e:
            print(f"\n!!! ERROR during agent execution: {e}")
            traceback.print_exc()

        finally:
            # Ensure the client is closed on script exit, regardless of how main() finished
            print("\n--- Attempting final client cleanup ---")
            try:
                # Use asyncio.run for the class method if the loop is already stopped
                asyncio.run(agent_service.close_client())
            except RuntimeError as ex:
                if "cannot call run_in_executor from a running event loop" in str(
                    ex
                ) or "cannot run coroutine" in str(ex):
                    # If loop is running or already closed in an unexpected way, might need adjustment
                    # For simplicity, just print the issue. Proper handling might need event loop access.
                    print(
                        f"--- Could not run async close_client cleanly in finally: {ex} ---"
                    )
                else:
                    raise ex
            except Exception as e:
                print(f"--- Error during final client cleanup: {e} ---")

            print("--- Script Finished ---\n\n")


# --- Main Execution --- #
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n   Process interrupted by user.")
    except Exception as e:
        print(f"\n Top-level error: {e}")
        traceback.print_exc()
