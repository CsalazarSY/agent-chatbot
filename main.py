# main.py
import asyncio
import json
import traceback

# Centralized Agent Service
from agents.agents_services import agent_service


# --- --- Main Execution --- --- #
async def main():
    # --- Define Task ---
    initial_message_text = input("Enter initial message: ")
    task_result = None
    error_message = None
    
    try:
        print("\n>>>>>>>>>>>>>> Chat Start <<<<<<<<<<<<<<")
        # Call the centralized service method
        task_result, error_message = await agent_service.run_chat_session(initial_message_text, show_console=True)
        print("\n>>>>>>>>>>>>>> Chat End <<<<<<<<<<<<<<")

    except asyncio.CancelledError:
        print("--- Task Cancelled ---")
        
    except Exception as e:
        # AgentService handles internal errors, this catches errors calling it
        print(f"\n\n!!! ERROR during task invocation: {e}")
        traceback.print_exc()

    ####### --- Process Task Result --- #######
    print(f"\n\n\n\n\n <<<----------->>> Task Result Analysis <<<----------->>>")
    if error_message:
        print(f"        - Task failed with error: {error_message}")
    elif task_result:
        print(f"        - Stop Reason: {task_result.stop_reason}")
        print(f"        - Number of Messages: {len(task_result.messages)}")

        # Check the final message
        if task_result.messages:
            final_message = task_result.messages[-1]
            # Extract content safely
            if hasattr(final_message, 'content'):
                 final_content = final_message.content if isinstance(final_message.content, str) else json.dumps(final_message.content)
            else:
                 final_content = f"[{type(final_message).__name__} with no 'content']"

            if task_result.stop_reason is None or "completed" in str(task_result.stop_reason).lower() or "finished" in str(task_result.stop_reason).lower():
                    print(">>> Task completed successfully. <<<")
                    print(f"        - Final Message: {final_content}")
        else:
            print(">>> No messages found in TaskResult. <<<")
    else:
         print(">>> TaskResult was not obtained (task might have failed before completion or service error) <<<")
    ####### --- End of Task Result Analysis --- #######


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

        print("\n--- Script Finished ---")