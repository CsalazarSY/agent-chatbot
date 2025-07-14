"""Service for extracting quick reply data from agent messages."""

# /src/services/get_quick_replies.py

import json
import re
from typing import Optional, Tuple

# Import the DTO for QuickReplyAttachment to validate the parsed structure
from src.tools.hubspot.conversation.dto_requests import (
    QuickReplyOption,
    QuickReplyAttachment,
)
from src.markdown_info.quick_replies.quick_reply_markdown import (
    QUICK_REPLIES_START_TAG,
    QUICK_REPLIES_END_TAG,
)
from src.services.logger_config import log_message


def extract_quick_replies(
    raw_reply_content: str,
) -> Tuple[str, Optional[QuickReplyAttachment]]:
    f"""
    Extracts a custom quick reply tag format from an agents message,
    parses it into a QuickReplyAttachment object, and returns the cleaned message
    and the attachment object.

    The expected format is:
    {QUICK_REPLIES_START_TAG}<value_type>:[JSON_ARRAY_OF_OBJECTS]{QUICK_REPLIES_END_TAG}
    e.g., {QUICK_REPLIES_START_TAG}<product_clarification>:[{{"label": "Option 1", "value": "value_1"}}, {{"label": "Option 2", "value": "value_2"}}]{QUICK_REPLIES_END_TAG}

    Args:
        raw_reply_content: The raw string content from the agent.

    Returns:
        A tuple containing:
            - cleaned_message_text: The message text with the quick reply block removed.
            - quick_reply_attachment: A QuickReplyAttachment object if valid quick
                                      replies were found, otherwise None.
    """
    cleaned_message_text = raw_reply_content
    quick_reply_attachment: Optional[QuickReplyAttachment] = None

    # Regex to find the custom quick reply block.
    # It captures the value_type and the JSON array string.
    pattern = re.compile(
        f"{re.escape(QUICK_REPLIES_START_TAG)}"  # Start tag
        r"<([^>:]+)>:"  # Capture group 1: value_type (anything not '>' or ':')
        r"\s*(\[.*?\])\s*"  # Capture group 2: the JSON array
        f"{re.escape(QUICK_REPLIES_END_TAG)}",  # End tag
        re.DOTALL,
    )

    match = pattern.search(raw_reply_content)

    if match:
        value_type = match.group(1).strip()
        json_array_str = match.group(2)
        # Remove the entire matched block from the original message
        cleaned_message_text = pattern.sub("", raw_reply_content).strip()

        try:
            options_list = json.loads(json_array_str)
            parsed_options = []

            if isinstance(options_list, list):
                for item in options_list:
                    # Expect item to be a dictionary {"label": "...", "value": "..."}
                    if not isinstance(item, dict):
                        continue  # Skip non-dictionary items

                    label = item.get("label")
                    value = item.get("value")

                    # Ensure both label and value are present
                    if label is not None and value is not None:
                        parsed_options.append(
                            QuickReplyOption(
                                valueType=value_type, label=str(label), value=str(value)
                            )
                        )

                if parsed_options:
                    quick_reply_attachment = QuickReplyAttachment(
                        quickReplies=parsed_options
                    )

        except json.JSONDecodeError as e:
            log_message(
                f"Failed to decode Quick Replies JSON: {e}. String was: {json_array_str}",
                level=3,
                log_type="error",
            )
        except Exception as e_gen:
            log_message(
                f"An unexpected error occurred while processing quick replies: {e_gen}. Tag was: {match.group(0)}",
                level=3,
                log_type="error",
            )

    return cleaned_message_text, quick_reply_attachment
