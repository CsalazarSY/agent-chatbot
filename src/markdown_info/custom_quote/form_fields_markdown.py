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
- **'Required: Yes'**: This information must be asked and should be provided by the user.
- **'Required: No'**: This information is optional. If the user provides this information, you can store it, but you don't explicitly ask for it unless specified in a Guidance Note.
- **'Disabled'**: This field is disabled and should NOT be asked.
- **'Conditional Logic'**: Describes when a field becomes relevant or required based on previous answers.
- **'List values'**: For Dropdown fields, these are the exact, fixed options the user must choose from.
- **'PQA Guidance Note'**: Specific instructions for the Price Quote Agent on how to guide the Planner for this field.

**I. Product Information (Step 1)**
*(PQA starts here to identify the product)*
1.  **Display Label:** Product:
    - **HubSpot Internal Name:** `product_group`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes
    - **List values:** {', '.join(f"'{e}'" for e in ProductGroupEnum.get_all_values())}
    - **PQA Guidance Note:** Ask "What type of product are you looking for?".
2.  **Display Label:** Type of Sticker:
    - **HubSpot Internal Name:** `type_of_sticker_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes (IF `product_group` is '{ProductGroupEnum.STICKER.value}')
    - **List values:** {', '.join(f"'{e}'" for e in TypeOfStickerEnum.get_all_values())}
    - **PQA Guidance Note:** If Product is Sticker, ask for the specific type.
3.  **Display Label:** Type of Cling:
    - **HubSpot Internal Name:** `type_of_cling_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes (IF `product_group` is '{ProductGroupEnum.CLING.value}')
    - **List values:** {', '.join(f"'{e}'" for e in TypeOfClingEnum.get_all_values())}
    - **PQA Guidance Note:** If Product is Cling, ask for the specific type.
4.  **Display Label:** Type of Decal:
    - **HubSpot Internal Name:** `type_of_decal_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes (IF `product_group` is '{ProductGroupEnum.DECAL.value}')
    - **List values:** {', '.join(f"'{e}'" for e in TypeOfDecalEnum.get_all_values())}
    - **PQA Guidance Note:** If Product is Decal, ask for the specific type.
5.  **Display Label:** Type of Magnet:
    - **HubSpot Internal Name:** `type_of_magnet_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes (IF `product_group` is '{ProductGroupEnum.MAGNET.value}')
    - **List values:** {', '.join(f"'{e}'" for e in TypeOfMagnetEnum.get_all_values())}
    - **PQA Guidance Note:** If Product is Magnet, ask for the specific type.
6.  **Display Label:** Type of Patch:
    - **HubSpot Internal Name:** `type_of_patch_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes (IF `product_group` is '{ProductGroupEnum.PATCH.value}')
    - **List values:** {', '.join(f"'{e}'" for e in TypeOfPatchEnum.get_all_values())}
    - **PQA Guidance Note:** If Product is Patch, ask for the specific type.
7.  **Display Label:** Type of Label:
    - **HubSpot Internal Name:** `type_of_label_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes (IF `product_group` is '{ProductGroupEnum.ROLL_LABEL.value}')
    - **List values:** {', '.join(f"'{e}'" for e in TypeOfLabelEnum.get_all_values())}
    - **PQA Guidance Note:** If Product is Roll Label, ask for the specific type.
8.  **Display Label:** Type of Tattoo:
    - **HubSpot Internal Name:** `type_of_tattoo_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes (IF `product_group` is '{ProductGroupEnum.TATTOO.value}')
    - **List values:** {', '.join(f"'{e}'" for e in TypeOfTattooEnum.get_all_values())}
    - **PQA Guidance Note:** If Product is Tattoo, ask for the specific type.
9.  **Display Label:** Type of Tape:
    - **HubSpot Internal Name:** `type_of_tape_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes (IF `product_group` is '{ProductGroupEnum.PACKING_TAPE.value}')
    - **List values:** {', '.join(f"'{e}'" for e in TypeOfTapeEnum.get_all_values())}
    - **PQA Guidance Note:** If Product is Packing Tape, ask for the specific type.
10. **Display Label:** Type of Packaging:
    - **HubSpot Internal Name:** `type_of_packaging_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes (IF `product_group` is '{ProductGroupEnum.PACKAGING.value}')
    - **List values:** {', '.join(f"'{e}'" for e in TypeOfPackagingEnum.get_all_values())}
    - **PQA Guidance Note:** If Product is Packaging, ask for the specific type.
11. **Display Label:** Pouch Size:
    - **HubSpot Internal Name:** `pouch_size_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes (IF `product_group` is '{ProductGroupEnum.PACKAGING.value}')
    - **List values:** {', '.join(f"'{e}'" for e in PouchSizeEnum.get_all_values())}
    - **PQA Guidance Note:** If Product is Packaging, ask for the pouch size.
12. **Display Label:** Pouch Label Material:
    - **HubSpot Internal Name:** `pouch_label_material_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes (IF `product_group` is '{ProductGroupEnum.PACKAGING.value}')
    - **List values:** {', '.join(f"'{e}'" for e in PouchLabelMaterialEnum.get_all_values())}
    - **PQA Guidance Note:** If Product is Packaging, ask for the pouch label material.
13. **Display Label:** What size of tape?
    - **HubSpot Internal Name:** `what_size_of_tape_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes (IF `product_group` is '{ProductGroupEnum.PACKING_TAPE.value}')
    - **List values:** {', '.join(f"'{e}'" for e in WhatSizeOfTapeEnum.get_all_values())}
    - **PQA Guidance Note:** If Product is Packing Tape, ask for the tape size.
14. **Display Label:** Preferred Format
    - **HubSpot Internal Name:** `preferred_format`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes (IF `product_group` is '{ProductGroupEnum.STICKER.value}' OR `product_group` is '{ProductGroupEnum.ROLL_LABEL.value}')
    - **List values:** {', '.join(f"'{e}'" for e in PreferredFormatEnum.get_all_values())}
    - **PQA Guidance Note:** If the product has format options, ask for the preferred format.

**II. Quote Information (Step 2)**
*(PQA collects size and quantity after product is identified)*
15. **Display Label:** Total Quantity:
    - **HubSpot Internal Name:** `total_quantity_`
    - **Property Type:** Ticket Property
    - **Field Type:** Number
    - **Required:** Yes
    - **PQA Guidance Note:** Ask "What is the total quantity you are looking for?".
16. **Display Label:** Dimensions
    - **HubSpot Internal Name:** `width_in_inches_`, `height_in_inches_`
    - **Property Type:** Ticket Property
    - **Field Type:** Number
    - **Required:** Yes
    - **PQA Guidance Note:** Ask for dimensions in a single question: "What are the dimensions for your product (e.g., '3x3 inches')?". The PQA will parse the user's response for width and height values.

**III. Contact Information (Step 3)**
*(PQA collects the single point of contact)*
17. **Display Label:** Email
    - **HubSpot Internal Name:** `email`
    - **Property Type:** Contact Property
    - **Field Type:** Text
    - **Required:** No (but one of email or phone is required)
    - **PQA Guidance Note:** Ask a single, clear question: "Perfect. And how can our team contact you with your quote? Please provide an email address or a phone number.".
18. **Display Label:** Phone number
    - **HubSpot Internal Name:** `phone`
    - **Property Type:** Contact Property
    - **Field Type:** Phone number
    - **Required:** No (but one of email or phone is required)
    - **Limits:** Must be between 7 and 20 characters.
    - **PQA Guidance Note:** This is collected via the same question as the email.

**IV. Final Confirmation Question (Step 4)**
*(The very last question)*
19. **Display Label:** Are you a promotional product distributor?
    - **HubSpot Internal Name:** `promotional_product_distributor_`
    - **Property Type:** Ticket Property
    - **Field Type:** Single Checkbox (Boolean: Yes/No)
    - **Required:** No
    - **PQA Guidance Note:** Ask this as the final question: "Got it. One last thing: to make sure we get you to the right team, are you a promotional product distributor?".

**V. Optional & Context-Populated Fields**
*(These fields are not asked for directly. The PQA should parse the user's conversation and populate these fields if the user provides the information voluntarily.)*
20. **Display Label:** First name
    - **HubSpot Internal Name:** `firstname`
    - **Required:** No
    - **PQA Guidance Note:** Do not ask for this. Populate only if the user offers it.
21. **Display Label:** Last name
    - **HubSpot Internal Name:** `lastname`
    - **Required:** No
    - **PQA Guidance Note:** Do not ask for this. Populate only if the user offers it.
22. **Display Label:** Upload your design
    - **HubSpot Internal Name:** `upload_your_design`
    - **Required:** No
    - **PQA Guidance Note:** Do not ask for this. The Planner will prompt the user for a file after the ticket is created. If a file is uploaded during the conversation, this field can be noted as 'File Provided'.
23. **Display Label:** Additional Instructions:
    - **HubSpot Internal Name:** `additional_instructions_`
    - **Required:** No
    - **PQA Guidance Note:** Do not ask for this directly. This field is a catch-all for any extra details the user provides during the conversation.

**VI. Disabled Fields (PQA MUST IGNORE):**
*(These fields are disabled and should not be asked for or processed)*
- `use_type`
- `company`
- `business_category`
- `other_business_category`
- `location`
- `call_requested`
- `application_use_`
- `hs_legal_communication_consent_checkbox`

**VII. System Generated Fields (For AI agents internal use only):**
- `subject`
- `content`
- `type_of_ticket`
"""
