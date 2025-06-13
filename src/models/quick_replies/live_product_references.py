# /src/models/quick_replies/live_product_references.py

# Contains example "Quick Replies: [...]" string constants for the Live Product Agent (LPA)
# to use in its system message examples or for internal reference.

# Example for product clarification when multiple products match
LPA_PRODUCT_CLARIFICATION_QR = 'Quick Replies: [{ "valueType": "product_clarification", "label": "Clear Static Cling", "value": "Clear Static Cling" }, { "valueType": "product_clarification", "label": "White Static Cling", "value": "White Static Cling" }]'

# Example for listing countries (a small subset for the example)
LPA_COUNTRY_SELECTION_QR = 'Quick Replies: [{ "valueType": "country_selection", "label": "United States", "value": "US" }, { "valueType": "country_selection", "label": "Canada", "value": "CA" }, { "valueType": "country_selection", "label": "United Kingdom", "value": "GB" }]'

# Example for confirming if the product identified by the agent is correct.
LPA_PRODUCT_CONFIRMATION_QR = (
    "Quick Replies: ["
    '{{ "valueType": "product_confirmation", "label": "Yes, that\'s the one!", "value": "yes_correct_product" }}, '
    '{{ "valueType": "product_confirmation", "label": "No, that\'s not it", "value": "no_incorrect_product" }}'
    "]"
)
