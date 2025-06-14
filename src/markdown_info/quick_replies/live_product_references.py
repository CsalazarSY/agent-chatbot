# /src/markdown_info/quick_replies/live_product_references.py
from .quick_reply_markdown import (
    QUICK_REPLIES_START_TAG,
    QUICK_REPLIES_END_TAG,
)

# Contains example "Quick Replies: [...]" string constants for the Live Product Agent (LPA)
# to use in its system message examples or for internal reference.

# Example for product clarification when multiple products match
LPA_PRODUCT_CLARIFICATION_QR = f'{QUICK_REPLIES_START_TAG}<product_clarification>:["Clear Static Cling", "White Static Cling"]{QUICK_REPLIES_END_TAG}'

# Example for listing countries (a small subset for the example)
LPA_COUNTRY_SELECTION_QR = f'{QUICK_REPLIES_START_TAG}<country_selection>:["United States|US", "Canada|CA", "United Kingdom|GB"]{QUICK_REPLIES_END_TAG}'

# Example for confirming if the product identified by the agent is correct.
LPA_PRODUCT_CONFIRMATION_QR = f'{QUICK_REPLIES_START_TAG}<product_confirmation>:["Yes, that\'s the one!|yes_correct_product", "No, that\'s not it|no_incorrect_product"]{QUICK_REPLIES_END_TAG}'
