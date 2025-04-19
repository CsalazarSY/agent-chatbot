# main.py
import asyncio
import json
import traceback
from typing import Optional

# Centralized Agent Service
from agents.agents_services import agent_service


# --- --- Main Execution --- --- #
async def main():
    # --- Define Task ---
    conversation_id: Optional[str] = None # Initialize conversation ID
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
            task_result, error_message, returned_conversation_id = await agent_service.run_chat_session(
                user_input,
                show_console=True,
                conversation_id=conversation_id
            )
            conversation_id = returned_conversation_id # Update conversation_id for the next loop
            print("\n")

            # --- Process and Display Result --- #
            if error_message:
                print(f"    ERROR: {error_message}")
            elif task_result:
                # print(f"    - Stop Reason: {task_result.stop_reason}")
                # Display the last message content as the reply
                if task_result.messages:
                    final_message = task_result.messages[-1]
                    if hasattr(final_message, 'content'):
                        final_content = final_message.content if isinstance(final_message.content, str) else json.dumps(final_message.content)
                        # Clean up internal tags for display
                        display_reply = final_content.replace("<UserProxyAgent>", "").strip()
                        if display_reply.startswith("TASK COMPLETE:"): display_reply = display_reply[len("TASK COMPLETE:"):].strip()
                        if display_reply.startswith("TASK FAILED:"): display_reply = display_reply[len("TASK FAILED:"):].strip()
                    else:
                        print(f"Agent: [{type(final_message).__name__} with no content]")
                else:
                    print("Agent: (No message content returned)")
            else:
                 print("    TaskResult was not obtained.")

        except asyncio.CancelledError:
            print("--- Task Cancelled --- ")
            break

        except Exception as e:
            print(f"\n!!! ERROR during agent execution: {e}")
            traceback.print_exc()


# --- Main Execution --- #
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n   Process interrupted by user.")
    except Exception as e:
         print(f"\n Top-level error: {e}")
         traceback.print_exc()
    finally:
        # Ensure the client is closed on script exit, regardless of how main() finished
        print("\n--- Attempting final client cleanup ---")
        try:
            # Use asyncio.run for the class method if the loop is already stopped
            asyncio.run(agent_service.close_client())
        except RuntimeError as ex:
             if "cannot call run_in_executor from a running event loop" in str(ex) or \
                "cannot run coroutine" in str(ex):
                  # If loop is running or already closed in an unexpected way, might need adjustment
                  # For simplicity, just print the issue. Proper handling might need event loop access.
                  print(f"--- Could not run async close_client cleanly in finally: {ex} ---")
             else:
                  raise ex
        except Exception as e:
            print(f"--- Error during final client cleanup: {e} ---")

        print("--- Script Finished ---\n\n")