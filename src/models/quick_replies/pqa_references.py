# /src/models/quick_replies/pqa_references.py

# Contains example "Quick Replies: [...]" string constants for the Price Quote Agent (PQA)
# to use in its system message examples or for internal reference.

# Example for selecting a Product Group (maps to ProductGroupEnum)
PQA_PRODUCT_GROUP_SELECTION_QR = 'Quick Replies: [{ "valueType": "product_group", "label": "Stickers", "value": "Stickers" }, { "valueType": "product_group", "label": "Labels", "value": "Labels" }, { "valueType": "product_group", "label": "Decals", "value": "Decals" }]'

# Example for selecting Use Type (maps to UseTypeEnum)
PQA_USE_TYPE_SELECTION_QR = 'Quick Replies: [{ "valueType": "use_type", "label": "Personal", "value": "Personal" }, { "valueType": "use_type", "label": "Business", "value": "Business" }]'

# Example for a Yes/No question, like design assistance
PQA_DESIGN_ASSISTANCE_YES_NO_QR = 'Quick Replies: [{ "valueType": "design_assistance_response", "label": "Yes, please", "value": "Yes" }, { "valueType": "design_assistance_response", "label": "No, thank you", "value": "No" }]'

# Example for confirming if a summary is correct
PQA_SUMMARY_CONFIRMATION_YES_NO_QR = 'Quick Replies: [{ "valueType": "summary_confirmation", "label": "Yes, that\'s correct", "value": "Yes" }, { "valueType": "summary_confirmation", "label": "No, I need to change something", "value": "No" }]'
