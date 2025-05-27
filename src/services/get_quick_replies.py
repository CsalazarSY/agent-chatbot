"""Service for extracting quick reply data from agent messages."""
# /src/services/get_quick_replies.py

import json
import re
from typing import Optional, Tuple, List, Dict, Any

# Import the DTO for QuickReplyAttachment to validate the parsed structure
from src.tools.hubspot.conversation.dto_requests import QuickReplyOption, QuickReplyAttachment

def extract_quick_replies(raw_reply_content: str) -> Tuple[str, Optional[QuickReplyAttachment]]:
    """
    Extracts quick reply JSON string from the end of an agent's message,
    parses it into a QuickReplyAttachment object, and returns the cleaned message
    and the attachment object.

    Args:
        raw_reply_content: The raw string content from the agent, which might
                           contain a quick reply definition at the end.

    Returns:
        A tuple containing:
            - cleaned_message_text: The message text with the quick reply definition removed.
            - quick_reply_attachment: A QuickReplyAttachment object if valid quick
                                      replies were found and parsed, otherwise None.
    """
    cleaned_message_text = raw_reply_content
    quick_reply_attachment_obj: Optional[QuickReplyAttachment] = None

    # Regex to find "Quick Replies: [...]" at the end of the string
    # It captures the JSON part (the list within the brackets)
    # The regex handles potential whitespace and ensures it's at the end.
    match = re.search(r"Quick Replies:\s*(\[.*?\])\s*$", raw_reply_content, re.DOTALL)

    if match:
        quick_reply_json_str = match.group(1)
        # Remove the matched part (including "Quick Replies: ") from the original message
        cleaned_message_text = raw_reply_content[:match.start()].strip()
        
        try:
            # Parse the JSON string into a list of dictionaries
            quick_reply_list_data = json.loads(quick_reply_json_str)
            
            # Validate and structure the data using Pydantic models
            if isinstance(quick_reply_list_data, list):
                parsed_options = []
                valid_options = True
                for item in quick_reply_list_data:
                    if isinstance(item, dict):
                        try:
                            option = QuickReplyOption(**item)
                            parsed_options.append(option)
                        except Exception as pydantic_err_option:
                            print(f"Error parsing individual quick reply option: {item}. Error: {pydantic_err_option}")
                            valid_options = False
                            break 
                    else:
                        print(f"Invalid item type in quick_reply_list_data: {type(item)}. Expected dict.")
                        valid_options = False
                        break
                
                if valid_options and parsed_options: # Ensure we have some valid options
                    quick_reply_attachment_obj = QuickReplyAttachment(quickReplies=parsed_options)
                elif not parsed_options:
                     print("No valid quick reply options were parsed from the JSON data.")
                # If valid_options is False, an error has already been printed.

            else:
                print(f"Parsed quick reply data is not a list: {type(quick_reply_list_data)}")

        except json.JSONDecodeError as e:
            print(f"Failed to decode Quick Replies JSON: {e}. String was: {quick_reply_json_str}")
        except Exception as e_gen:
            # Catch any other unexpected errors during parsing or Pydantic validation
            print(f"An unexpected error occurred while processing quick replies: {e_gen}. JSON string was: {quick_reply_json_str}")

    return cleaned_message_text, quick_reply_attachment_obj 