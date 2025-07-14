"""
This file defines the standard string format for Quick Replies
that agents should append to their messages for the Planner.

The Planner will then relay this entire string (prefix + JSON array)
as part of its final message to the user.

The `extract_quick_replies` service will parse this string from the Planner's output.
"""

# /src/models/quick_replies/quick_reply_markdown.py

QUICK_REPLIES_START_TAG = "<QuickReplies>"
QUICK_REPLIES_END_TAG = "</QuickReplies>"

QUICK_REPLY_STRUCTURE_DEFINITION = f"""
When you need to offer the user a set of predefined choices, you should present these as Quick Replies.
To do this, append a special tag structure to your main message to the Planner.

The structure MUST be: {QUICK_REPLIES_START_TAG}<value_type>:[JSON_ARRAY_OF_OBJECTS]{QUICK_REPLIES_END_TAG}

- `<value_type>`: A string that categorizes the type of value being sent (e.g., "product_group", "country_selection"). It needs to be inside the brackets `<` and `>`.
- `[JSON_ARRAY_OF_OBJECTS]`: A valid JSON array of objects. Each object represents an option and must contain "label" and "value" keys.

Example:
{QUICK_REPLIES_START_TAG}<product_clarification>:[{{"label": "Option 1", "value": "value_1"}}, {{"label": "Option 2", "value": "value_2"}}]{QUICK_REPLIES_END_TAG}
"""

# A very generic example that can be referenced in system messages if needed, though specific examples are usually better.
GENERIC_QUICK_REPLY_EXAMPLE_STRING = f'{QUICK_REPLIES_START_TAG}<generic_type>:[{{"label": "Generic Option 1", "value": "generic_val_1"}}, {{"label": "Generic Option 2", "value": "generic_val_2"}}]{QUICK_REPLIES_END_TAG}'

# Full example of a message incorporating the quick reply structure.
# This shows how an agent might formulate a complete message with quick replies.
GENERIC_MESSAGE_WITH_QUICK_REPLIES = (
    "This is a message that requires the user to choose from a few options. "
    f"{GENERIC_QUICK_REPLY_EXAMPLE_STRING}"
)
