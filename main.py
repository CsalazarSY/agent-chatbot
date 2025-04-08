# main.py
import asyncio
import json
import traceback

# AutoGen imports
from autogen_core import CancellationToken
from autogen_agentchat.ui import Console
# Import specific model client and ModelInfo
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelInfo

# Import the agents
from price.price_agent import create_price_agent

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
            temperature=0.1,
            timeout=600,
            # Crucial for local models needing tool support hint
            model_info=ModelInfo(
                vision=False,
                function_calling=True,  # Explicitly state function calling is expected
                json_output=False,  # Depending on model, might support True
                family="unknown",  # Or "llama" if known
                structured_output=True  # If model supports structured output schemas
            ),
        )
        print(f"<- Agent Definition: Model client created for {LLM_MODEL_NAME}")

    except Exception as e:
        print(f"Agent Definition Error creating model client: {e}")
        raise ValueError("Could not create OpenAIChatCompletionClient for agent.")

    # --- Create Agents ---
    price_assistant = create_price_agent(model_client)

    # --- Define Task ---
    initial_message_text = "Hi there, what's the cost for 300 white vinyl stickers? the size is 3 by 3 inches"
    # Could also use: initial_task = TextMessage(content=initial_message_text, source="user")
    print(f"Initiating task with message: \"{initial_message_text}\"")
    print("\n---------------- Chat Start ------------------\n")

    # --- Run Task ---
    cancellation_token = CancellationToken() # Allows for potential cancellation
    task_result = None # Initialize task_result

    try:
        # Use agent.run_stream() with Console for real-time output
        # Console() will print the stream and return the final TaskResult
        task_result = await Console(
            price_assistant.run_stream(
                task=initial_message_text, # Pass the initial message as the task
                cancellation_token=cancellation_token
            )
        )

        print("\n---------------- Chat End --------------------")
        print("Task finished streaming.")

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
                print(f"\nError closing model client: {e}")
        else:
            print("\n--- Model client was not initialized, skipping close ---")

    # --- Process Task Result ---
    print(f"\n\n\n\n\n ----------->>> Task Result Analysis <<<-----------")
    if task_result:
        print(f" - Stop Reason: {task_result.stop_reason}")
        print(f" - Number of Messages: {len(task_result.messages)}")

        # Check the final message
        if task_result.messages:
            final_message = task_result.messages[-1]
            # Extract content safely
            if hasattr(final_message, 'content'):
                 final_content = final_message.content if isinstance(final_message.content, str) else json.dumps(final_message.content)
            else:
                 final_content = f"[{type(final_message).__name__} with no 'content']"

            print(f"\n >>> Final Message Content:\n{'-'*20}\n{final_content}\n{'-'*20}")

            # Check for handoff string in the final message content
            if isinstance(final_content, str) and final_content.startswith("HANDOFF:"):
                print("\n>>> --- HANDOFF TRIGGERED --- <<<")
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