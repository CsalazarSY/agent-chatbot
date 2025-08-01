import asyncio
import os
import json
import argparse
import traceback

# --- Import your existing modules ---
# This assumes retrieve_redis_chats.py is in your project's root directory.
from config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD
from src.services.redis_client import initialize_redis_pool, close_redis_pool, get_redis_client
from src.services.logger_config import log_message
from src.services.json_utils import json_serializer_default # We might not need this for loading, but good to have if needed


async def fetch_and_save_conversation(conversation_id: str, output_dir: str):
    """
    Fetches a single conversation state from Redis and saves it as a JSON file.
    """
    # Application saves keys with a prefix. We must use the same prefix.
    redis_key = f"conv_state:{conversation_id}"
    log_message(f"Attempting to fetch data for key: '{redis_key}'")

    try:
        async with get_redis_client() as redis:
            # Get the raw JSON string from Redis
            saved_state_json = await redis.get(redis_key)

            if saved_state_json is None:
                log_message(f"No data found for conversation ID: {conversation_id}", log_type="warning", prefix="!!")
                return

            # Parse the JSON string into a Python dictionary
            try:
                conversation_data = json.loads(saved_state_json)
            except json.JSONDecodeError as e:
                log_message(f"Failed to parse JSON for {conversation_id}: {e}", log_type="error", prefix="!!!")
                log_message("Saving the raw text content instead.", log_type="warning")
                # Fallback: save the raw string if it's not valid JSON
                conversation_data = {"raw_content": saved_state_json}


            # Convert the Python dictionary back to a nicely formatted JSON string (pretty-print)
            pretty_json_output = json.dumps(
                conversation_data,
                indent=2, # Use an indent of 2 spaces for readability
                default=json_serializer_default # Use your app's serializer for any complex objects
            )

            # Define the output file path. Using .json is better than .txt for this data.
            output_file_path = os.path.join(output_dir, f"{conversation_id}.json")

            # Write the pretty-printed JSON to the file
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(pretty_json_output)

            log_message(f"Successfully saved conversation {conversation_id} to {output_file_path}", prefix=">>>")

    except Exception as e:
        log_message(f"An unexpected error occurred for conversation ID {conversation_id}: {e}", log_type="error", prefix="!!!")
        log_message(traceback.format_exc())


async def main():
    """
    Main function to parse arguments and orchestrate the fetching process.
    """
    parser = argparse.ArgumentParser(
        description="Fetch conversation history from Redis and save locally as JSON files."
    )
    parser.add_argument(
        "conversation_ids",
        metavar="ID",
        type=str,
        nargs='+',  # This allows one or more IDs to be passed
        help="One or more conversation IDs to fetch from Redis."
    )
    args = parser.parse_args()

    # Define the directory where files will be saved
    output_directory = "retrieved_conversations"
    os.makedirs(output_directory, exist_ok=True)
    log_message(f"Output will be saved in the '{output_directory}/' directory.")

    try:
        # Initialize the connection pool, just like your main app
        await initialize_redis_pool()

        # Create a task for each conversation ID
        tasks = [fetch_and_save_conversation(conv_id, output_directory) for conv_id in args.conversation_ids]
        await asyncio.gather(*tasks)

    finally:
        # Ensure the connection pool is closed gracefully
        await close_redis_pool()
        log_message("Process finished.")


if __name__ == "__main__":
    asyncio.run(main())