"""
This file contains the markdown definition of the custom quote form.
"""

from src.agents.agent_names import PLANNER_AGENT_NAME
from src.tools.hubspot.tickets.constants import TypeOfTicketEnum
from .constants import (
    ProductGroupEnum,
    TypeOfClingEnum,
    TypeOfDecalEnum,
    TypeOfMagnetEnum,
    TypeOfPatchEnum,
    TypeOfLabelEnum,
    TypeOfStickerEnum,
    TypeOfTattooEnum,
    TypeOfTapeEnum,
    TypeOfPackagingEnum,
    PreferredFormatEnum,
    PouchSizeEnum,
    PouchLabelMaterialEnum,
    WhatSizeOfTapeEnum,
    # Keeping disabled enums for reference in disabled fields section
    UseTypeEnum,
    BusinessCategoryEnum,
    LocationEnum,
)

CUSTOM_QUOTE_FORM_MARKDOWN_DEFINITION = f"""
**Custom Quote Form Structure & Rules:**

The following defines the fields, requirements, and conditional logic for collecting custom quote information.
- **'Required: Yes'**: This information must be provided by the user.
- **'Required: No'**: This information is optional.
- **'Disabled'**: This field is disabled and should NOT be asked by the PQA.
- **'Conditional Logic'**: Describes when a field becomes relevant or required based on previous answers.
- **'List values'**: For Dropdown fields, these are the exact, fixed options the user must choose from. The Planner Agent MUST present these options to the user.
- **'PQA Guidance Note'**: Specific instructions for the Price Quote Agent on how to guide the Planner for this field. PQA should use these notes to formulate its instructions to the Planner.

**I. Product Selection & Specifications:**
*(PQA starts here - prioritizing product details for immediate quote relevance)*
1.  **Display Label:** Product:
    - **HubSpot Internal Name:** `product_group`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes
    - **List values:** {', '.join(f"'{e}'" for e in ProductGroupEnum.get_all_values())}
    - **Conditional Logic:** The selection here determines which of fields in Section II become relevant and required.
    - **PQA Guidance Note:** This is the first and most important question. PQA will instruct Planner to ask about 'What type of product are you looking to order?', presenting the available options clearly. The answer drives all subsequent product-specific questions.

**II. Product Type Specifics (Conditional on Product Selection):**
*(PQA asks the relevant fields from this section based on the Product answer)*
2.  **Display Label:** Type of Cling:
    - **HubSpot Internal Name:** `type_of_cling_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes (IF `product_group` is '{ProductGroupEnum.CLING.value}')
    - **List values:** {', '.join(f"'{e}'" for e in TypeOfClingEnum.get_all_values())}
    - **PQA Guidance Note:** If Product is Cling, PQA will immediately ask for 'What type of cling are you looking for?', presenting the available options.
3.  **Display Label:** Type of Decal:
    - **HubSpot Internal Name:** `type_of_decal_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes (IF `product_group` is '{ProductGroupEnum.DECAL.value}')
    - **List values:** {', '.join(f"'{e}'" for e in TypeOfDecalEnum.get_all_values())}
    - **PQA Guidance Note:** If Product is Decal, PQA will immediately ask for 'What type of decal are you looking for?', presenting the available options.
4.  **Display Label:** Type of Magnet:
    - **HubSpot Internal Name:** `type_of_magnet_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes (IF `product_group` is '{ProductGroupEnum.MAGNET.value}')
    - **List values:** {', '.join(f"'{e}'" for e in TypeOfMagnetEnum.get_all_values())}
    - **PQA Guidance Note:** If Product is Magnet, PQA will immediately ask for 'What type of magnet are you looking for?', presenting the available options.
5.  **Display Label:** Type of Patch:
    - **HubSpot Internal Name:** `type_of_patch_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes (IF `product_group` is '{ProductGroupEnum.PATCH.value}')
    - **List values:** {', '.join(f"'{e}'" for e in TypeOfPatchEnum.get_all_values())}
    - **PQA Guidance Note:** If Product is Patch, PQA will immediately ask for 'What type of patch are you looking for?', presenting the available options.
6.  **Display Label:** Type of Label:
    - **HubSpot Internal Name:** `type_of_label_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes (IF `product_group` is '{ProductGroupEnum.ROLL_LABEL.value}')
    - **List values:** {', '.join(f"'{e}'" for e in TypeOfLabelEnum.get_all_values())}
    - **PQA Guidance Note:** If Product is Roll Label, PQA will immediately ask for 'What type of label are you looking for?', presenting the available options.
7.  **Display Label:** Type of Sticker:
    - **HubSpot Internal Name:** `type_of_sticker_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes (IF `product_group` is '{ProductGroupEnum.STICKER.value}')
    - **List values:** {', '.join(f"'{e}'" for e in TypeOfStickerEnum.get_all_values())}
    - **PQA Guidance Note:** If Product is Sticker, PQA will immediately ask for 'What type of sticker are you looking for?', presenting the available options.
8.  **Display Label:** Type of Tattoo:
    - **HubSpot Internal Name:** `type_of_tattoo_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes (IF `product_group` is '{ProductGroupEnum.TATTOO.value}')
    - **List values:** {', '.join(f"'{e}'" for e in TypeOfTattooEnum.get_all_values())}
    - **PQA Guidance Note:** If Product is Tattoo, PQA will immediately ask for 'What type of tattoo are you looking for?', presenting the available options.
9.  **Display Label:** Type of Tape:
    - **HubSpot Internal Name:** `type_of_tape_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes (IF `product_group` is '{ProductGroupEnum.PACKING_TAPE.value}')
    - **List values:** {', '.join(f"'{e}'" for e in TypeOfTapeEnum.get_all_values())}
    - **PQA Guidance Note:** If Product is Tape, PQA will immediately ask for 'What type of tape are you looking for?', presenting the available options.
10. **Display Label:** Type of Packaging:
    - **HubSpot Internal Name:** `type_of_packaging_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes (IF `product_group` is '{ProductGroupEnum.PACKAGING.value}')
    - **List values:** {', '.join(f"'{e}'" for e in TypeOfPackagingEnum.get_all_values())}
    - **PQA Guidance Note:** If Product is Packaging, PQA will immediately ask for 'What type of packaging are you looking for?', presenting the available options.

**III. Additional Product Specifications (Conditional):**
*(PQA asks these based on specific product selections)*
11. **Display Label:** Preferred Format
    - **HubSpot Internal Name:** `preferred_format`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes (IF `product_group` is '{ProductGroupEnum.STICKER.value}' OR `product_group` is '{ProductGroupEnum.ROLL_LABEL.value}')
    - **List values:** {', '.join(f"'{e}'" for e in PreferredFormatEnum.get_all_values())}
    - **PQA Guidance Note:** If Product is Sticker or Roll Label, PQA will ask 'What format would you prefer?', presenting the available options.
12. **Display Label:** Pouch Size:
    - **HubSpot Internal Name:** `pouch_size_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes (IF `product_group` is '{ProductGroupEnum.PACKAGING.value}')
    - **List values:** {', '.join(f"'{e}'" for e in PouchSizeEnum.get_all_values())}
    - **PQA Guidance Note:** If Product is Packaging, PQA will ask 'What pouch size do you need?', presenting the available options.
13. **Display Label:** Pouch Label Material:
    - **HubSpot Internal Name:** `pouch_label_material_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes (IF `product_group` is '{ProductGroupEnum.PACKAGING.value}')
    - **List values:** {', '.join(f"'{e}'" for e in PouchLabelMaterialEnum.get_all_values())}
    - **PQA Guidance Note:** If Product is Packaging, PQA will ask 'What material would you like for the pouch label?', presenting the available options.
14. **Display Label:** What size of tape?
    - **HubSpot Internal Name:** `what_size_of_tape_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** No (but PQA should guide Planner to ask IF `product_group` is '{ProductGroupEnum.PACKING_TAPE.value}')
    - **List values:** {', '.join(f"'{e}'" for e in WhatSizeOfTapeEnum.get_all_values())}
    - **PQA Guidance Note:** If Product is Tape, PQA will ask 'What size tape do you need?', presenting the available options.

**IV. Core Quote Specifications:**
*(PQA guides Planner after product details are established)*
15. **Display Label:** Total Quantity:
    - **HubSpot Internal Name:** `total_quantity_`
    - **Property Type:** Ticket Property
    - **Field Type:** Number
    - **Required:** Yes
    - **PQA Guidance Note:** PQA will ask 'How many do you need?' or 'What's the total quantity you're looking for?' as a standalone question for clarity.
16. **Display Label:** Width in Inches:
    - **HubSpot Internal Name:** `width_in_inches_`
    - **Property Type:** Ticket Property
    - **Field Type:** Number
    - **Required:** Yes
    - **PQA Guidance Note:** PQA will ask 'What width do you need (in inches)?' as a separate question for precision.
17. **Display Label:** Height in Inches:
    - **HubSpot Internal Name:** `height_in_inches_`
    - **Property Type:** Ticket Property
    - **Field Type:** Number
    - **Required:** Yes
    - **PQA Guidance Note:** PQA will ask 'What height do you need (in inches)?' as a separate question for precision.

**V. Design & Application Details:**
*(PQA collects design-related information)*
18. **Display Label:** Upload your design
    - **HubSpot Internal Name:** `upload_your_design`
    - **Property Type:** Ticket Property
    - **Field Type:** File (Conceptually for PQA; actual file handling is via chat)
    - **Required:** No
    - **PQA Guidance Note:** PQA will ask 'Do you have a design file you'd like to upload? If so, please share it now. If not, let me know and I can help you with design options!' This creates a natural conversation flow for design handling.
19. **Display Label:** Application Use:
    - **HubSpot Internal Name:** `application_use_`
    - **Property Type:** Ticket Property
    - **Field Type:** Text
    - **Required:** No
    - **PQA Guidance Note:** PQA will ask 'What will you be using these for?' or 'How do you plan to use these products?' as a conversational question to understand context.
20. **Display Label:** Additional Instructions:
    - **HubSpot Internal Name:** `additional_instructions_`
    - **Property Type:** Ticket Property
    - **Field Type:** Textarea
    - **Required:** No
    - **PQA Guidance Note:** PQA will ask 'Is there anything else you'd like me to know about your order or any special requirements?' This captures any additional details the user wants to share.
21. **Display Label:** Are you a promotional product distributor?
    - **HubSpot Internal Name:** `promotional_product_distributor_`
    - **Property Type:** Ticket Property
    - **Field Type:** Single Checkbox (Boolean: Yes/No)
    - **Required:** No
    - **PQA Guidance Note:** PQA will ask this as one of the final questions before requesting contact info: 'One quick question for our team: Are you a promotional product distributor?' This helps with pricing and service classification.

**VI. Contact Information (Collected at the End):**
*(PQA collects essential contact info only when ready to finalize quote)*
22. **Display Label:** Email
    - **HubSpot Internal Name:** `email`
    - **Property Type:** Contact Property
    - **Field Type:** Text
    - **Required:** No (but one of email or phone is required)
    - **PQA Guidance Note:** PQA will ask 'How can our team contact you with your quote? Please provide an email address or phone number.' PQA must parse the response and populate either the `email` or `phone` field based on what the user provides.
23. **Display Label:** Phone number
    - **HubSpot Internal Name:** `phone`
    - **Property Type:** Contact Property
    - **Field Type:** Phone number
    - **Required:** No (but one of email or phone is required)
    - **Limits:** Must be between 7 and 20 characters.
    - **PQA Guidance Note:** See guidance for the `email` field. PQA should collect whichever contact method the user prefers to provide.

**VII. Optional Support & Services:**
*(PQA may ask these contextually based on conversation flow)*
24. **Display Label:** Request a support call
    - **HubSpot Internal Name:** `call_requested`
    - **Property Type:** Ticket Property
    - **Field Type:** Single Checkbox (Boolean: Yes/No)
    - **Required:** No
    - **PQA Guidance Note:** PQA may ask this contextually if the user seems to need more help or if the quote is complex: 'Would you like one of our specialists to call you to discuss the details?'

**VIII. Disabled Fields (DO NOT ASK):**
*(These fields are disabled and PQA should completely ignore them)*
25. **Display Label:** First name
    - **HubSpot Internal Name:** `firstname`
    - **Property Type:** Contact Property
    - **Field Type:** Text
    - **Required:** No (Disabled - Do not ask)
    - **PQA Guidance Note:** This field is disabled. PQA should NOT ask for the user's first name. Focus on product details instead.
26. **Display Label:** Last name
    - **HubSpot Internal Name:** `lastname`
    - **Property Type:** Contact Property
    - **Field Type:** Text
    - **Required:** No (Disabled - Do not ask)
    - **PQA Guidance Note:** This field is disabled. PQA should NOT ask for the user's last name. Focus on product details instead.
27. **Display Label:** Personal or business use?
    - **HubSpot Internal Name:** `use_type`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** No (Disabled - Do not ask)
    - **List values:** {', '.join(f"'{e}'" for e in UseTypeEnum.get_all_values())}
    - **PQA Guidance Note:** This field is disabled. PQA should NOT ask whether it's personal or business use. This unnecessarily complicates the conversation flow.
28. **Display Label:** Company name
    - **HubSpot Internal Name:** `company`
    - **Property Type:** Contact Property
    - **Field Type:** Text
    - **Required:** No (Disabled - Do not ask)
    - **PQA Guidance Note:** This field is disabled. PQA should NOT ask for company name unless the user volunteers this information.
29. **Display Label:** Business Category
    - **HubSpot Internal Name:** `business_category`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** No (Disabled - Do not ask)
    - **List values:** {', '.join(f"'{e}'" for e in BusinessCategoryEnum.get_all_values())}
    - **PQA Guidance Note:** This field is disabled. PQA should NOT ask about business category.
30. **Display Label:** Business Category (Other)
    - **HubSpot Internal Name:** `other_business_category`
    - **Property Type:** Ticket Property
    - **Field Type:** Text
    - **Required:** No (Disabled - Do not ask)
    - **PQA Guidance Note:** This field is disabled. PQA should NOT ask for other business category details.
31. **Display Label:** Location
    - **HubSpot Internal Name:** `location`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** No (Disabled - Do not ask)
    - **List values:** {', '.join(f"'{e}'" for e in LocationEnum.get_all_values())}
    - **PQA Guidance Note:** This field is disabled. PQA should NOT ask about location unless specifically needed for shipping calculations.

**IX. Additional Disabled Fields (DO NOT ASK):**
*(These fields exist in HubSpot but are not part of the active conversational flow)*
32. **Display Label:** Consent to communicate
    - **HubSpot Internal Name:** `hs_legal_communication_consent_checkbox`
    - **Property Type:** Contact Property
    - **Field Type:** Single Checkbox (Boolean: Yes/No)
    - **Required:** No (Disabled - Do not ask)
    - **PQA Guidance Note:** This field is disabled. PQA should NOT ask for consent. This is handled by other business processes.
33. **Display Label:** Have you ordered with us before?
    - **HubSpot Internal Name:** `have_you_ordered_with_us_before_`
    - **Property Type:** Ticket Property
    - **Field Type:** Single Checkbox (Boolean: Yes/No)
    - **Required:** No (Disabled - Do not ask)
    - **List values:** 'Yes', 'No'
    - **PQA Guidance Note:** This field is disabled. PQA should NOT ask about previous orders.
34. **Display Label:** How did you find us?
    - **HubSpot Internal Name:** `how_did_you_find_us_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** No (Disabled - Do not ask)
    - **List values:** 'Google Search', 'Social Media', 'Email', 'PPAI/ASI', 'Tradeshow', 'StickerYou Store', 'Existing customer', 'Banner Ads', 'Referral from Another Customer', 'Catalog', 'Live Chat', 'General Inquiry Form'
    - **PQA Guidance Note:** This field is disabled. PQA should NOT ask how the user found the company.
35. **Display Label:** Number of colours in design:
    - **HubSpot Internal Name:** `number_of_colours_in_design_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** No (Disabled - Do not ask)
    - **List values:** '1', '2', '3'
    - **PQA Guidance Note:** This field is disabled. PQA should NOT ask about number of colors in design.
36. **Display Label:** Preferred Format Stickers
    - **HubSpot Internal Name:** `preferred_format_stickers`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** No (Disabled - Do not ask)
    - **List values:** 'Pages', 'Kiss-Cut Singles', 'Die-Cut Singles'
    - **PQA Guidance Note:** This field is disabled. PQA should NOT ask about this (likely duplicate of 'Preferred Format').
37. **Display Label:** Upload your vector artwork
    - **HubSpot Internal Name:** `upload_your_vector_artwork`
    - **Property Type:** Ticket Property
    - **Field Type:** File (Conceptual for PQA; actual file handling is via chat)
    - **Required:** No (Disabled - Do not ask)
    - **PQA Guidance Note:** This field is disabled. PQA should NOT ask specifically for vector artwork (covered by general design upload).
38. **Display Label:** What kind of content would you like to hear about?
    - **HubSpot Internal Name:** `what_kind_of_content_would_you_like_to_hear_about_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** No (Disabled - Do not ask)
    - **List values:** 'Business Products and News', 'Consumer Products and News', 'Products and Sweet Deals for Parents', 'Not sure yet - send me everything!'
    - **PQA Guidance Note:** This field is disabled. PQA should NOT ask about content preferences.

**X. System Generated Fields (For AI agents internal use only - DO NOT ask user for these):**
*(The PQA and Planner agents automatically generate these based on the conversation)*
39. **Label:** Subject
    - **HubSpot Internal Name:** `subject`
    - **Property Type:** Ticket Property
    - **Field Type:** Text
    - **Required:** Yes (Agent Generated - Do not ask user)
    - **PQA Guidance Note:** The Planner Agent automatically generates this based on the product type and key details (e.g., "Custom Quote Request - 500 Vinyl Stickers 3x3 inches"). This should NOT be asked to the user.
40. **Label:** Content
    - **HubSpot Internal Name:** `content`
    - **Property Type:** Ticket Property
    - **Field Type:** Text (HubSpot may render this as Rich Text)
    - **Required:** Yes (Agent Generated - Do not ask user)
    - **PQA Guidance Note:** The Planner Agent generates a brief, human-readable summary of the request for this field. This should NOT be asked to the user.
41. **Label:** Type of Ticket
    - **HubSpot Internal Name:** `type_of_ticket`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown (Single choice among the following values: {', '.join(f"'{e}'" for e in TypeOfTicketEnum.get_all_values())})
    - **Required:** Yes (Agent Generated - Do not ask user)
    - **List values:** {', '.join(f"'{e}'" for e in TypeOfTicketEnum.get_all_values())}
    - **PQA Guidance Note:** The {PLANNER_AGENT_NAME} automatically sets this to "{TypeOfTicketEnum.QUOTE.value}" for custom quote requests. This should NOT be asked to the user.
"""
