"""
This file contains the markdown definition of the custom quote form.
"""
# /src/models/custom_quote/form_fields_markdown.py
from .constants import (
    UseTypeEnum, BusinessCategoryEnum, LocationEnum, ProductGroupEnum,
    TypeOfClingEnum, TypeOfDecalEnum, TypeOfMagnetEnum, TypeOfPatchEnum,
    TypeOfLabelEnum, TypeOfStickerEnum, TypeOfTattooEnum, TypeOfTapeEnum,
    PreferredFormatEnum, TypeOfPackagingEnum, PouchSizeEnum, PouchLabelMaterialEnum,
    WhatSizeOfTapeEnum
)

CUSTOM_QUOTE_FORM_MARKDOWN_DEFINITION = f"""
**Custom Quote Form Structure & Rules:**

The following defines the fields, requirements, and conditional logic for collecting custom quote information.
- **'Required: Yes'**: This information must be provided by the user.
- **'Required: No'**: This information is optional.
- **'Conditional Logic'**: Describes when a field becomes relevant or required based on previous answers.
- **'List values'**: For Dropdown fields, these are the exact, fixed options the user must choose from. The Planner Agent MUST present these options to the user.

**I. Contact Information:**
*(Planner should ask for these details first)*
1.  **Display Label:** First name
    - **HubSpot Internal Name:** `firstname`
    - **Property Type:** Contact Property
    - **Field Type:** Text
    - **Required:** No
2.  **Display Label:** Last name
    - **HubSpot Internal Name:** `lastname`
    - **Property Type:** Contact Property
    - **Field Type:** Text
    - **Required:** No
3.  **Display Label:** Email
    - **HubSpot Internal Name:** `email`
    - **Property Type:** Contact Property
    - **Field Type:** Text
    - **Required:** Yes
4.  **Display Label:** Phone number
    - **HubSpot Internal Name:** `phone`
    - **Property Type:** Contact Property
    - **Field Type:** Phone number
    - **Required:** Yes
    - **Limits:** Must be between 7 and 20 characters.

**II. Initial Details:**
*(Planner asks after Contact Information)*
5.  **Display Label:** Request a support call
    - **HubSpot Internal Name:** `call_requested`
    - **Property Type:** Ticket Property
    - **Field Type:** Single Checkbox (Boolean: Yes/No)
    - **Required:** No
    - **Planner Question Hint:** "Would you like one of our team members to call you to discuss this quote?"
6.  **Display Label:** Personal or business use?
    - **HubSpot Internal Name:** `use_type`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes
    - **List values:** {', '.join(f"'{e}'" for e in UseTypeEnum.get_all_values())}
    - **Conditional Logic:** If this is '{UseTypeEnum.BUSINESS.value}', then fields 7, 8, 9, 10 become relevant.

**III. Business Details (Conditional):**
*(Planner asks these ONLY IF 'Personal or business use?' is '{UseTypeEnum.BUSINESS.value}')*
7.  **Display Label:** Company name
    - **HubSpot Internal Name:** `company`
    - **Property Type:** Contact Property
    - **Field Type:** Text
    - **Required:** No (but ask if `use_type` is Business)
8.  **Display Label:** Business Category
    - **HubSpot Internal Name:** `business_category`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** No (but ask if `use_type` is Business)
    - **List values:** {', '.join(f"'{e}'" for e in BusinessCategoryEnum.get_all_values())}
    - **Conditional Logic:** If this is '{BusinessCategoryEnum.OTHER.value}', then field 9 becomes relevant.
9.  **Display Label:** Business Category (Other)
    - **HubSpot Internal Name:** `other_business_category`
    - **Property Type:** Ticket Property
    - **Field Type:** Text
    - **Required:** No (but ask if `business_category` is '{BusinessCategoryEnum.OTHER.value}')
10. **Display Label:** Are you a promotional product distributor?
    - **HubSpot Internal Name:** `promotional_product_distributor_`
    - **Property Type:** Ticket Property
    - **Field Type:** Single Checkbox (Boolean: Yes/No)
    - **Required:** No (but ask if `use_type` is Business)

**IV. General Product & Quote Details:**
*(Planner asks after Business Details (if applicable) or Initial Details)*
11. **Display Label:** Location
    - **HubSpot Internal Name:** `location`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** No
    - **List values:** {', '.join(f"'{e}'" for e in LocationEnum.get_all_values())}
12. **Display Label:** Product:
    - **HubSpot Internal Name:** `product_group`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes
    - **List values:** {', '.join(f"'{e}'" for e in ProductGroupEnum.get_all_values())}
    - **Conditional Logic:** The selection here determines which of fields 13-24 (Type of X, Pouch Size, etc.) become relevant and required.

**V. Product Specifics (Conditional on 'Product:' selection):**
*(Planner asks the relevant field(s) from this section based on the answer to field 12 'Product:')*
13. **Display Label:** Type of Cling:
    - **HubSpot Internal Name:** `type_of_cling_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes (IF `product_group` is '{ProductGroupEnum.CLING.value}')
    - **List values:** {', '.join(f"'{e}'" for e in TypeOfClingEnum.get_all_values())}
14. **Display Label:** Type of Decal:
    - **HubSpot Internal Name:** `type_of_decal_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes (IF `product_group` is '{ProductGroupEnum.DECAL.value}')
    - **List values:** {', '.join(f"'{e}'" for e in TypeOfDecalEnum.get_all_values())}
15. **Display Label:** Type of Magnet:
    - **HubSpot Internal Name:** `type_of_magnet_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes (IF `product_group` is '{ProductGroupEnum.MAGNET.value}')
    - **List values:** {', '.join(f"'{e}'" for e in TypeOfMagnetEnum.get_all_values())}
16. **Display Label:** Type of Patch:
    - **HubSpot Internal Name:** `type_of_patch_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes (IF `product_group` is '{ProductGroupEnum.PATCH.value}')
    - **List values:** {', '.join(f"'{e}'" for e in TypeOfPatchEnum.get_all_values())}
17. **Display Label:** Type of Label:
    - **HubSpot Internal Name:** `type_of_label_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes (IF `product_group` is '{ProductGroupEnum.ROLL_LABEL.value}')
    - **List values:** {', '.join(f"'{e}'" for e in TypeOfLabelEnum.get_all_values())}
18. **Display Label:** Type of Sticker:
    - **HubSpot Internal Name:** `type_of_sticker_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes (IF `product_group` is '{ProductGroupEnum.STICKER.value}')
    - **List values:** {', '.join(f"'{e}'" for e in TypeOfStickerEnum.get_all_values())}
19. **Display Label:** Type of Tattoo:
    - **HubSpot Internal Name:** `type_of_tattoo_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes (IF `product_group` is '{ProductGroupEnum.TATTOO.value}')
    - **List values:** {', '.join(f"'{e}'" for e in TypeOfTattooEnum.get_all_values())}
20. **Display Label:** Type of Tape:
    - **HubSpot Internal Name:** `type_of_tape_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes (IF `product_group` is '{ProductGroupEnum.TAPE.value}')
    - **List values:** {', '.join(f"'{e}'" for e in TypeOfTapeEnum.get_all_values())}
21. **Display Label:** Preferred Format
    - **HubSpot Internal Name:** `preferred_format`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes (IF `product_group` is '{ProductGroupEnum.STICKER.value}' OR '{ProductGroupEnum.ROLL_LABEL.value}')
    - **List values:** {', '.join(f"'{e}'" for e in PreferredFormatEnum.get_all_values())}
22. **Display Label:** Type of Packaging:
    - **HubSpot Internal Name:** `type_of_packaging_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes (IF `product_group` is '{ProductGroupEnum.PACKAGING.value}')
    - **List values:** {', '.join(f"'{e}'" for e in TypeOfPackagingEnum.get_all_values())}
23. **Display Label:** Pouch Size:
    - **HubSpot Internal Name:** `pouch_size_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes (IF `product_group` is '{ProductGroupEnum.PACKAGING.value}')
    - **List values:** {', '.join(f"'{e}'" for e in PouchSizeEnum.get_all_values())}
24. **Display Label:** Pouch Label Material:
    - **HubSpot Internal Name:** `pouch_label_material_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** Yes (IF `product_group` is '{ProductGroupEnum.PACKAGING.value}')
    - **List values:** {', '.join(f"'{e}'" for e in PouchLabelMaterialEnum.get_all_values())}
25. **Display Label:** What size of tape?
    - **HubSpot Internal Name:** `what_size_of_tape_`
    - **Property Type:** Ticket Property
    - **Field Type:** Dropdown
    - **Required:** No (Ask IF `product_group` is '{ProductGroupEnum.TAPE.value}')
    - **List values:** {', '.join(f"'{e}'" for e in WhatSizeOfTapeEnum.get_all_values())}

**VI. Core Quote Specifications:**
*(Planner asks for these after all product-specific questions are resolved)*
26. **Display Label:** Total Quantity:
    - **HubSpot Internal Name:** `total_quantity_`
    - **Property Type:** Ticket Property
    - **Field Type:** Number
    - **Required:** Yes
27. **Display Label:** Width in Inches:
    - **HubSpot Internal Name:** `width_in_inches_`
    - **Property Type:** Ticket Property
    - **Field Type:** Number
    - **Required:** Yes
28. **Display Label:** Height in Inches:
    - **HubSpot Internal Name:** `height_in_inches_`
    - **Property Type:** Ticket Property
    - **Field Type:** Number
    - **Required:** Yes

**VII. Optional Additional Details:**
*(Planner asks these after core specifications)*
29. **Display Label:** Application Use:
    - **HubSpot Internal Name:** `application_use_`
    - **Property Type:** Ticket Property
    - **Field Type:** Text
    - **Required:** No
30. **Display Label:** Additional Instructions:
    - **HubSpot Internal Name:** `additional_instructions_`
    - **Property Type:** Ticket Property
    - **Field Type:** Text
    - **Required:** No
    - **Planner Note:** Mention to user: "Leave any further instructions necessary for our product experts including desired end-use. Make sure to check your spam/junk folder for our reply."
31. **Display Label:** Upload your design
    - **HubSpot Internal Name:** `upload_your_design`
    - **Property Type:** Ticket Property
    - **Field Type:** File
    - **Required:** No
    - **Planner Note:** Inform user: "Regarding your design, if you have one ready, our team will coordinate with you on how to best submit it after they review your quote request. For now, I don't need you to upload it here."

**VIII. System Generated Fields (For AI internal use only - DO NOT ask user for these):**
-   **Ticket name (Subject)** (`subject`, Ticket Property, Text, Required: Yes) - Planner generates based on collected info (e.g., "Custom Quote Request: [Product Group] - [User Last Name]").
-   **Ticket description (Content)** (`content`, Ticket Property, Text, Required: Yes) - Planner generates a structured summary of ALL collected and validated user responses corresponding to the Display Labels above.
-   **Type of Ticket** (`type_of_ticket`, Ticket Property, Dropdown, Hidden) - This can be set by the system or Planner. For custom quotes, this might be "Custom Quote Request" or a similar internal value.
"""