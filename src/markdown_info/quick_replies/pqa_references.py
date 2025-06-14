"""
This file contains example "Quick Replies: [...]" string constants for the Price Quote Agent (PQA)
to use in its system message examples or for internal reference.
"""

# /src/markdown_info/quick_replies/pqa_references.py

from .quick_reply_markdown import (
    QUICK_REPLIES_START_TAG,
    QUICK_REPLIES_END_TAG,
)

# Example for selecting a Product Group (maps to ProductGroupEnum)
PQA_PRODUCT_GROUP_SELECTION_QR = f'{QUICK_REPLIES_START_TAG}<product_group>:["Stickers", "Labels", "Decals"]{QUICK_REPLIES_END_TAG}'

# Example for selecting Use Type (maps to UseTypeEnum)
PQA_USE_TYPE_SELECTION_QR = f'{QUICK_REPLIES_START_TAG}<use_type>:["Personal", "Business"]{QUICK_REPLIES_END_TAG}'

# Example for selecting a Material Type
PQA_MATERIAL_SELECTION_QR = f'{QUICK_REPLIES_START_TAG}<material_sy>:["Vinyl", "Holographic", "Clear"]{QUICK_REPLIES_END_TAG}'

# Example for a Yes/No question, like design assistance
PQA_DESIGN_ASSISTANCE_YES_NO_QR = f'{QUICK_REPLIES_START_TAG}<design_assistance_response>:["Yes", "No"]{QUICK_REPLIES_END_TAG}'
