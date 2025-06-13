# /src/models/quick_replies/planner_references.py

# Contains example "Quick Replies: [...]" string constants for the Planner Agent
# to use in its system message examples, or if it needs to generate its own QRs.

# Example for Planner: Clarifying the user's primary goal at the start of a conversation.
PLANNER_GOAL_CLARIFICATION_QR = (
    "Quick Replies: ["
    '{{ "valueType": "user_goal", "label": "Get a Price Quote", "value": "get_quote" }}, '
    '{{ "valueType": "user_goal", "label": "Track My Order", "value": "track_order" }}, '
    '{{ "valueType": "user_goal", "label": "Product Information", "value": "product_info" }}, '
    '{{ "valueType": "user_goal", "label": "Speak to Customer Support", "value": "customer_support" }}, '
    '{{ "valueType": "user_goal", "label": "Other Inquiry", "value": "other_inquiry" }}'
    "]"
)

# Example for Planner: Offering Quick Quote or Custom Quote path when user intent is to get a price.
PLANNER_QUOTE_TYPE_SELECTION_QR = (
    "Quick Replies: ["
    '{{ "valueType": "quote_type", "label": "Quick Quote (Standard Items)", "value": "quick_quote" }}, '
    '{{ "valueType": "quote_type", "label": "Custom Quote (Specific Needs)", "value": "custom_quote" }}'
    "]"
)

# Example for Planner: Confirming understanding of the user's request before delegation.
PLANNER_CONFIRM_UNDERSTANDING_QR = (
    "Quick Replies: ["
    '{{ "valueType": "confirmation", "label": "Yes, that\'s correct. Proceed.", "value": "yes_proceed" }}, '
    '{{ "valueType": "confirmation", "label": "No, let me clarify.", "value": "no_clarify_further" }}'
    "]"
)

# Example for Planner: When a Quick Quote attempt fails, offering next steps.
PLANNER_QUICK_QUOTE_FAILED_OPTIONS_QR = (
    "Quick Replies: ["
    '{{ "valueType": "next_step_after_qq_fail", "label": "Try a Custom Quote", "value": "try_custom_quote" }}, '
    '{{ "valueType": "next_step_after_qq_fail", "label": "Explore other products", "value": "explore_products" }}, '
    '{{ "valueType": "next_step_after_qq_fail", "label": "Connect me with a specialist", "value": "talk_to_human" }}'
    "]"
)

# Example for Planner: When user asks for support, clarifying the type of support needed.
PLANNER_SUPPORT_TYPE_CLARIFICATION_QR = (
    "Quick Replies: ["
    '{{ "valueType": "support_type", "label": "Issue with an existing order", "value": "order_issue" }}, '
    '{{ "valueType": "support_type", "label": "Problem with the website", "value": "website_issue" }}, '
    '{{ "valueType": "support_type", "label": "Billing question", "value": "billing_question" }}, '
    '{{ "valueType": "support_type", "label": "Other support", "value": "other_support" }}'
    "]"
)

# Example for confirming if a summary is correct (could be used by Planner too)
PLANNER_GENERAL_CONFIRMATION_YES_NO_QR = (
    'Quick Replies: [{ "valueType": "summary_confirmation", "label": "Yes, that\'s correct", "value": "Yes" }, '
    '{ "valueType": "summary_confirmation", "label": "No, I need to change something", "value": "No" }]'
)

# Example for when Quick Quote fails due to actionable error (e.g., min quantity)
# Note: "[Corrected Value]" would be dynamically filled by the Planner based on PQA's error.
# This constant shows the structure.
PLANNER_ADJUST_OR_CUSTOM_QUOTE_QR = (
    'Quick Replies: [{ "valueType": "adjust_qq", "label": "Quote for [Corrected Value]", "value": "Quote for [Corrected Value]" }, '
    '{ "valueType": "start_cq", "label": "Start Custom Quote", "value": "Start Custom Quote" }]'
)
