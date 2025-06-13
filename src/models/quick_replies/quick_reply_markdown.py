# /src/models/quick_replies/quick_reply_markdown.py

# This file defines the standard string format for Quick Replies
# that agents should append to their messages for the Planner.

# The Planner will then relay this entire string (prefix + JSON array)
# as part of its final message to the user.
# The `extract_quick_replies` service will parse this string from the Planner's output.

QUICK_REPLY_STRUCTURE_DEFINITION = """
When you need to offer the user a set of predefined choices, you should instruct the Planner
to present these as Quick Replies. To do this, append a special string to your main message
to the Planner. This string MUST start EXACTLY with "Quick Replies: " followed by a valid
JSON array string. Each object in the JSON array represents one quick reply option and
MUST contain the following keys:
- "valueType": A string that categorizes the type of value being sent (e.g., "product_group", "product_clarification", "country_selection", "yes_no_response"). This helps the system or client process the selection.
- "label": The text that will be displayed on the quick reply button for the user.
- "value": The actual value that will be sent back if the user clicks this option.

Generic Example Format:
Quick Replies: [{ "valueType": "example_type", "label": "Option 1 Text", "value": "option_1_value" }, { "valueType": "example_type", "label": "Option 2 Text", "value": "option_2_value" }]

Ensure the JSON array string is correctly formatted.
"""

# A very generic example that can be referenced in system messages if needed,
# though specific examples are usually better.
GENERIC_QUICK_REPLY_EXAMPLE_STRING = 'Quick Replies: [{ "valueType": "generic_type", "label": "Generic Option 1", "value": "generic_val_1" }, { "valueType": "generic_type", "label": "Generic Option 2", "value": "generic_val_2" }]'

# Full example of a message incorporating the quick reply structure.
# This shows how an agent might formulate a complete message with quick replies.
GENERIC_MESSAGE_WITH_QUICK_REPLIES = (
    "This is a message that requires the user to choose from a few options. "
    f"{GENERIC_QUICK_REPLY_EXAMPLE_STRING}"
)
