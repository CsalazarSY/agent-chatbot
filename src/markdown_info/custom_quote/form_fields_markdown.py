"""
This file contains the markdown definition of the custom quote form.
"""

from src.constants import (
    HubSpotFieldType,
    HubSpotPropertyType,
    HubSpotPropertyName,
    ProductCategoryEnum,
    StickerFormatEnum,
    StickerPageSingleDesignFinishEnum,
    StickerDieCutFinishEnum,
    StickerKissCutFinishEnum,
    StickerRollsFinishEnum,
    StickerPageMultipleDesignsFinishEnum,
    StickerTransfersFinishEnum,
    LabelsFormatEnum,
    LabelsPageSingleDesignFinishEnum,
    LabelsKissCutFinishEnum,
    LabelsRollsFinishEnum,
    LabelsPageMultipleDesignsFinishEnum,
    LabelsImageTransfersFinishEnum,
    ImageTransfersFinishEnum,
    DecalsFormatEnum,
    DecalsWallWindowFinishEnum,
    DecalsFloorOutdoorFinishEnum,
    DecalsImageTransfersFinishEnum,
    TempTattoosFormatEnum,
    TempTattoosPageSingleDesignFinishEnum,
    TempTattoosKissCutFinishEnum,
    TempTattoosPageMultipleDesignsFinishEnum,
    IronOnsFormatEnum,
    IronOnsPageSingleDesignFinishEnum,
    IronOnsPageMultipleDesignsFinishEnum,
    IronOnsTransfersFinishEnum,
    MagnetsFinishEnum,
    ClingsFinishEnum,
    PouchesColor,
    PouchesSizeEnum,
    PouchesLabelMaterialEnum,
)

CUSTOM_QUOTE_FORM_MARKDOWN_DEFINITION = f"""
**Custom Quote Form Structure & Rules:**

The following defines the fields, requirements, and conditional logic for collecting custom quote information.
- **'Required: Yes'**: This information must be asked and should be provided by the user.
- **'Required: No'**: This information is optional. If the user provides this information, you can store it, but you don't explicitly ask for it unless specified in a Guidance Note.
- **'Conditional Logic'**: Describes when a field becomes relevant or required based on previous answers.
- **'List values'**: For Dropdown fields, these are the exact, fixed options the user must choose from.
- **'PQA Guidance Note'**: Specific instructions for the Price Quote Agent on how to guide the Planner for this field.

**I. Product Information (Step 1)**
*(PQA starts here to identify the product)*

1.  **Display Label:** Product Category
    - **HubSpot Internal Name:** `{HubSpotPropertyName.PRODUCT_CATEGORY.value}`
    - **Property Type:** {HubSpotPropertyType.TICKET_PROPERTY.value}
    - **Field Type:** {HubSpotFieldType.DROPDOWN.value}
    - **Required:** Yes
    - **List values:** {', '.join(f"'{e}'" for e in ProductCategoryEnum.get_all_values())}
    - **PQA Guidance Note:** Ask "What type of product are you looking for?".

---
### Stickers
2.  **Display Label:** Sticker Format
    - **HubSpot Internal Name:** `{HubSpotPropertyName.STICKER_FORMAT.value}`
    - **Property Type:** {HubSpotPropertyType.TICKET_PROPERTY.value}
    - **Field Type:** {HubSpotFieldType.DROPDOWN.value}
    - **Required:** Yes (IF `{HubSpotPropertyName.PRODUCT_CATEGORY.value}` is '{ProductCategoryEnum.STICKERS.value}')
    - **List values:** {', '.join(f"'{e}'" for e in StickerFormatEnum.get_all_values())}
    - **PQA Guidance Note:** If Product Category is Stickers, ask for the format.

3.  **Display Label:** Finish (for Sticker Page - Single Design)
    - **HubSpot Internal Name:** `{HubSpotPropertyName.STICKER_PAGE_SINGLE_DESIGN_FINISH.value}`
    - **Property Type:** {HubSpotPropertyType.TICKET_PROPERTY.value}
    - **Field Type:** {HubSpotFieldType.DROPDOWN.value}
    - **Required:** Yes (IF `{HubSpotPropertyName.STICKER_FORMAT.value}` is '{StickerFormatEnum.PAGE_SINGLE_DESIGN.value}')
    - **List values:** {', '.join(f"'{e}'" for e in StickerPageSingleDesignFinishEnum.get_all_values())}
    - **PQA Guidance Note:** Ask for the finish.

4.  **Display Label:** Finish (for Sticker Die-Cut)
    - **HubSpot Internal Name:** `{HubSpotPropertyName.STICKER_DIE_CUT_FINISH.value}`
    - **Property Type:** {HubSpotPropertyType.TICKET_PROPERTY.value}
    - **Field Type:** {HubSpotFieldType.DROPDOWN.value}
    - **Required:** Yes (IF `{HubSpotPropertyName.STICKER_FORMAT.value}` is '{StickerFormatEnum.DIE_CUT.value}')
    - **List values:** {', '.join(f"'{e}'" for e in StickerDieCutFinishEnum.get_all_values())}
    - **PQA Guidance Note:** Ask for the finish.

5.  **Display Label:** Finish (for Sticker Kiss-Cut)
    - **HubSpot Internal Name:** `{HubSpotPropertyName.STICKER_KISS_CUT_FINISH.value}`
    - **Property Type:** {HubSpotPropertyType.TICKET_PROPERTY.value}
    - **Field Type:** {HubSpotFieldType.DROPDOWN.value}
    - **Required:** Yes (IF `{HubSpotPropertyName.STICKER_FORMAT.value}` is '{StickerFormatEnum.KISS_CUT.value}')
    - **List values:** {', '.join(f"'{e}'" for e in StickerKissCutFinishEnum.get_all_values())}
    - **PQA Guidance Note:** Ask for the finish.

6.  **Display Label:** Finish (for Sticker Rolls)
    - **HubSpot Internal Name:** `{HubSpotPropertyName.STICKER_ROLLS_FINISH.value}`
    - **Property Type:** {HubSpotPropertyType.TICKET_PROPERTY.value}
    - **Field Type:** {HubSpotFieldType.DROPDOWN.value}
    - **Required:** Yes (IF `{HubSpotPropertyName.STICKER_FORMAT.value}` is '{StickerFormatEnum.ROLLS.value}')
    - **List values:** {', '.join(f"'{e}'" for e in StickerRollsFinishEnum.get_all_values())}
    - **PQA Guidance Note:** Ask for the finish.

7.  **Display Label:** Finish (for Sticker Page - Multiple Designs)
    - **HubSpot Internal Name:** `{HubSpotPropertyName.STICKER_PAGE_MULTIPLE_DESIGNS_FINISH.value}`
    - **Property Type:** {HubSpotPropertyType.TICKET_PROPERTY.value}
    - **Field Type:** {HubSpotFieldType.DROPDOWN.value}
    - **Required:** Yes (IF `{HubSpotPropertyName.STICKER_FORMAT.value}` is '{StickerFormatEnum.PAGE_MULTIPLE_DESIGNS.value}')
    - **List values:** {', '.join(f"'{e}'" for e in StickerPageMultipleDesignsFinishEnum.get_all_values())}
    - **PQA Guidance Note:** Ask for the finish.

8.  **Display Label:** Finish (for Sticker Transfers)
    - **HubSpot Internal Name:** `{HubSpotPropertyName.STICKER_TRANSFERS_FINISH.value}`
    - **Property Type:** {HubSpotPropertyType.TICKET_PROPERTY.value}
    - **Field Type:** {HubSpotFieldType.DROPDOWN.value}
    - **Required:** Yes (IF `{HubSpotPropertyName.STICKER_FORMAT.value}` is '{StickerFormatEnum.TRANSFERS.value}')
    - **List values:** {', '.join(f"'{e}'" for e in StickerTransfersFinishEnum.get_all_values())}
    - **PQA Guidance Note:** Ask for the finish.

---
### Labels
9.  **Display Label:** Labels Format
    - **HubSpot Internal Name:** `{HubSpotPropertyName.LABELS_FORMAT.value}`
    - **Property Type:** {HubSpotPropertyType.TICKET_PROPERTY.value}
    - **Field Type:** {HubSpotFieldType.DROPDOWN.value}
    - **Required:** Yes (IF `{HubSpotPropertyName.PRODUCT_CATEGORY.value}` is '{ProductCategoryEnum.LABELS.value}')
    - **List values:** {', '.join(f"'{e}'" for e in LabelsFormatEnum.get_all_values())}
    - **PQA Guidance Note:** If Product Category is Labels, ask for the format. The finish is determined by this selection.

10. **Display Label:** Finish (for Labels Page - Single Design)
    - **HubSpot Internal Name:** `{HubSpotPropertyName.LABELS_PAGE_SINGLE_DESIGN_FINISH.value}`
    - **Property Type:** {HubSpotPropertyType.TICKET_PROPERTY.value}
    - **Field Type:** {HubSpotFieldType.DROPDOWN.value}
    - **Required:** Yes (IF `{HubSpotPropertyName.LABELS_FORMAT.value}` is '{LabelsFormatEnum.PAGE_SINGLE_DESIGN.value}')
    - **List values:** {', '.join(f"'{e}'" for e in LabelsPageSingleDesignFinishEnum.get_all_values())}
    - **PQA Guidance Note:** Ask for the finish.

11. **Display Label:** Finish (for Labels Kiss-Cut)
    - **HubSpot Internal Name:** `{HubSpotPropertyName.LABELS_KISS_CUT_FINISH.value}`
    - **Property Type:** {HubSpotPropertyType.TICKET_PROPERTY.value}
    - **Field Type:** {HubSpotFieldType.DROPDOWN.value}
    - **Required:** Yes (IF `{HubSpotPropertyName.LABELS_FORMAT.value}` is '{LabelsFormatEnum.KISS_CUT.value}')
    - **List values:** {', '.join(f"'{e}'" for e in LabelsKissCutFinishEnum.get_all_values())}
    - **PQA Guidance Note:** Ask for the finish.

12. **Display Label:** Finish (for Labels Rolls)
    - **HubSpot Internal Name:** `{HubSpotPropertyName.LABELS_ROLLS_FINISH.value}`
    - **Property Type:** {HubSpotPropertyType.TICKET_PROPERTY.value}
    - **Field Type:** {HubSpotFieldType.DROPDOWN.value}
    - **Required:** Yes (IF `{HubSpotPropertyName.LABELS_FORMAT.value}` is '{LabelsFormatEnum.ROLLS.value}')
    - **List values:** {', '.join(f"'{e}'" for e in LabelsRollsFinishEnum.get_all_values())}
    - **PQA Guidance Note:** Ask for the finish.

13. **Display Label:** Finish (for Labels Page - Multiple Designs)
    - **HubSpot Internal Name:** `{HubSpotPropertyName.LABELS_PAGE_MULTIPLE_DESIGNS_FINISH.value}`
    - **Property Type:** {HubSpotPropertyType.TICKET_PROPERTY.value}
    - **Field Type:** {HubSpotFieldType.DROPDOWN.value}
    - **Required:** Yes (IF `{HubSpotPropertyName.LABELS_FORMAT.value}` is '{LabelsFormatEnum.PAGE_MULTIPLE_DESIGNS.value}')
    - **List values:** {', '.join(f"'{e}'" for e in LabelsPageMultipleDesignsFinishEnum.get_all_values())}
    - **PQA Guidance Note:** Ask for the finish.

14. **INTERNAL FIELD - DO NOT ASK USER**
    - **HubSpot Internal Name:** `{HubSpotPropertyName.LABELS_IMAGE_TRANSFERS_FINISH.value}`
    - **Conditional Logic:** Automatically set to '{LabelsImageTransfersFinishEnum.TRANSFER_LABEL_PERMANENT_GLOSSY.value}' **IF `{HubSpotPropertyName.LABELS_FORMAT.value}` is '{LabelsFormatEnum.IMAGE_TRANSFERS.value}'.**
    - **PQA Guidance Note:** This field is auto-populated by you. Do not ask the user for this information.

---
### Image Transfers
15. **Display Label:** Finish (for Image Transfers)
    - **HubSpot Internal Name:** `{HubSpotPropertyName.IMAGE_TRANSFERS_FINISH.value}`
    - **Property Type:** {HubSpotPropertyType.TICKET_PROPERTY.value}
    - **Field Type:** {HubSpotFieldType.DROPDOWN.value}
    - **Required:** Yes (IF `{HubSpotPropertyName.PRODUCT_CATEGORY.value}` is '{ProductCategoryEnum.IMAGE_TRANSFERS.value}')
    - **List values:** {', '.join(f"'{e}'" for e in ImageTransfersFinishEnum.get_all_values())}
    - **PQA Guidance Note:** For Image Transfers, ask for the finish. No format selection is needed.

---
### Decals
16. **Display Label:** Decals Format
    - **HubSpot Internal Name:** `{HubSpotPropertyName.DECALS_FORMAT.value}`
    - **Property Type:** {HubSpotPropertyType.TICKET_PROPERTY.value}
    - **Field Type:** {HubSpotFieldType.DROPDOWN.value}
    - **Required:** Yes (IF `{HubSpotPropertyName.PRODUCT_CATEGORY.value}` is '{ProductCategoryEnum.DECALS.value}')
    - **List values:** {', '.join(f"'{e}'" for e in DecalsFormatEnum.get_all_values())}
    - **PQA Guidance Note:** If Product Category is Decals, ask for the format. The finish is determined by this selection.

17. **Display Label:** Finish (for Decals Wall & Window)
    - **HubSpot Internal Name:** `{HubSpotPropertyName.DECALS_WALL_WINDOW_FINISH.value}`
    - **Property Type:** {HubSpotPropertyType.TICKET_PROPERTY.value}
    - **Field Type:** {HubSpotFieldType.DROPDOWN.value}
    - **Required:** Yes (IF `{HubSpotPropertyName.DECALS_FORMAT.value}` is '{DecalsFormatEnum.WALL_WINDOW.value}')
    - **List values:** {', '.join(f"'{e}'" for e in DecalsWallWindowFinishEnum.get_all_values())}
    - **PQA Guidance Note:** Ask for the finish.

18. **Display Label:** Finish (for Decals Floor & Outdoor)
    - **HubSpot Internal Name:** `{HubSpotPropertyName.DECALS_FLOOR_OUTDOOR_FINISH.value}`
    - **Property Type:** {HubSpotPropertyType.TICKET_PROPERTY.value}
    - **Field Type:** {HubSpotFieldType.DROPDOWN.value}
    - **Required:** Yes (IF `{HubSpotPropertyName.DECALS_FORMAT.value}` is '{DecalsFormatEnum.FLOOR_OUTDOOR.value}')
    - **List values:** {', '.join(f"'{e}'" for e in DecalsFloorOutdoorFinishEnum.get_all_values())}
    - **PQA Guidance Note:** Ask for the finish.

19. **INTERNAL FIELD - DO NOT ASK USER**
    - **HubSpot Internal Name:** `{HubSpotPropertyName.DECALS_IMAGE_TRANSFERS_FINISH.value}`
    - **Conditional Logic:** Automatically set to '{DecalsImageTransfersFinishEnum.TRANSFER_DECAL_PERMANENT_GLOSSY.value}' **IF `{HubSpotPropertyName.DECALS_FORMAT.value}` is '{DecalsFormatEnum.IMAGE_TRANSFERS.value}'.**
    - **PQA Guidance Note:** This field is auto-populated by you. Do not ask the user for this information.

---
### Temp Tattoos
20. **Display Label:** Temp Tattoos Format
    - **HubSpot Internal Name:** `{HubSpotPropertyName.TEMP_TATTOOS_FORMAT.value}`
    - **Property Type:** {HubSpotPropertyType.TICKET_PROPERTY.value}
    - **Field Type:** {HubSpotFieldType.DROPDOWN.value}
    - **Required:** Yes (IF `{HubSpotPropertyName.PRODUCT_CATEGORY.value}` is '{ProductCategoryEnum.TEMP_TATTOOS.value}')
    - **List values:** {', '.join(f"'{e}'" for e in TempTattoosFormatEnum.get_all_values())}
    - **PQA Guidance Note:** If Product Category is Temp Tattoos, ask for the format. The finish for all Temp Tattoos is '{TempTattoosKissCutFinishEnum.REMOVABLE_CLEAR_MATTE.value}' and should be populated automatically without asking the user.

21. **INTERNAL FIELD - DO NOT ASK USER**
    - **HubSpot Internal Name:** `{HubSpotPropertyName.TEMP_TATTOOS_PAGE_SINGLE_DESIGN_FINISH.value}`
    - **Conditional Logic:** Automatically set to '{TempTattoosPageSingleDesignFinishEnum.REMOVABLE_CLEAR_MATTE.value}' **IF `{HubSpotPropertyName.TEMP_TATTOOS_FORMAT.value}` is '{TempTattoosFormatEnum.PAGE_SINGLE_DESIGN.value}'.**
    - **PQA Guidance Note:** This field is auto-populated by you. Do not ask the user for this information.

22. **INTERNAL FIELD - DO NOT ASK USER**
    - **HubSpot Internal Name:** `{HubSpotPropertyName.TEMP_TATTOOS_KISS_CUT_FINISH.value}`
    - **Conditional Logic:** Automatically set to '{TempTattoosKissCutFinishEnum.REMOVABLE_CLEAR_MATTE.value}' **IF `{HubSpotPropertyName.TEMP_TATTOOS_FORMAT.value}` is '{TempTattoosFormatEnum.KISS_CUT.value}'.**
    - **PQA Guidance Note:** This field is auto-populated by you. Do not ask the user for this information.

23. **INTERNAL FIELD - DO NOT ASK USER**
    - **HubSpot Internal Name:** `{HubSpotPropertyName.TEMP_TATTOOS_PAGE_MULTIPLE_DESIGNS_FINISH.value}`
    - **Conditional Logic:** Automatically set to '{TempTattoosPageMultipleDesignsFinishEnum.REMOVABLE_CLEAR_MATTE.value}' **IF `{HubSpotPropertyName.TEMP_TATTOOS_FORMAT.value}` is '{TempTattoosFormatEnum.PAGE_MULTIPLE_DESIGNS.value}'.**
    - **PQA Guidance Note:** This field is auto-populated by you. Do not ask the user for this information.

---
### Iron-Ons
24. **Display Label:** Iron-Ons Format
    - **HubSpot Internal Name:** `{HubSpotPropertyName.IRON_ONS_FORMAT.value}`
    - **Property Type:** {HubSpotPropertyType.TICKET_PROPERTY.value}
    - **Field Type:** {HubSpotFieldType.DROPDOWN.value}
    - **Required:** Yes (IF `{HubSpotPropertyName.PRODUCT_CATEGORY.value}` is '{ProductCategoryEnum.IRON_ONS.value}')
    - **List values:** {', '.join(f"'{e}'" for e in IronOnsFormatEnum.get_all_values())}
    - **PQA Guidance Note:** If Product Category is Iron-Ons, ask for the format. The finish is determined by this selection.

25. **INTERNAL FIELD - DO NOT ASK USER**
    - **HubSpot Internal Name:** `{HubSpotPropertyName.IRON_ONS_PAGE_SINGLE_DESIGN_FINISH.value}`
    - **Conditional Logic:** Automatically set to '{IronOnsPageSingleDesignFinishEnum.IRON_ONS_SINGLES.value}' **IF `{HubSpotPropertyName.IRON_ONS_FORMAT.value}` is '{IronOnsFormatEnum.PAGE_SINGLE_DESIGN.value}'.**
    - **PQA Guidance Note:** This field is auto-populated by you. Do not ask the user for this information.

26. **INTERNAL FIELD - DO NOT ASK USER**
    - **HubSpot Internal Name:** `{HubSpotPropertyName.IRON_ONS_PAGE_MULTIPLE_DESIGNS_FINISH.value}`
    - **Conditional Logic:** Automatically set to '{IronOnsPageMultipleDesignsFinishEnum.IRON_ONS_MULTIPLE.value}' **IF `{HubSpotPropertyName.IRON_ONS_FORMAT.value}` is '{IronOnsFormatEnum.PAGE_MULTIPLE_DESIGNS.value}'.**
    - **PQA Guidance Note:** This field is auto-populated by you. Do not ask the user for this information.

27. **Display Label:** Finish (for Iron-Ons Transfers)
    - **HubSpot Internal Name:** `{HubSpotPropertyName.IRON_ONS_TRANSFERS_FINISH.value}`
    - **Property Type:** {HubSpotPropertyType.TICKET_PROPERTY.value}
    - **Field Type:** {HubSpotFieldType.DROPDOWN.value}
    - **Required:** Yes (IF `{HubSpotPropertyName.IRON_ONS_FORMAT.value}` is '{IronOnsFormatEnum.TRANSFERS.value}')
    - **List values:** {', '.join(f"'{e}'" for e in IronOnsTransfersFinishEnum.get_all_values())}
    - **PQA Guidance Note:** If the chosen format is '{IronOnsFormatEnum.TRANSFERS.value}', ask the user to select a finish from the list.

---
### Magnets
28. **Display Label:** Finish (for Magnets)
    - **HubSpot Internal Name:** `{HubSpotPropertyName.MAGNETS_FINISH.value}`
    - **Property Type:** {HubSpotPropertyType.TICKET_PROPERTY.value}
    - **Field Type:** {HubSpotFieldType.DROPDOWN.value}
    - **Required:** Yes (IF `{HubSpotPropertyName.PRODUCT_CATEGORY.value}` is '{ProductCategoryEnum.MAGNETS.value}')
    - **List values:** {', '.join(f"'{e}'" for e in MagnetsFinishEnum.get_all_values())}
    - **PQA Guidance Note:** For Magnets, ask for the finish. No format selection is needed.

---
### Clings
29. **Display Label:** Finish (for Clings)
    - **HubSpot Internal Name:** `{HubSpotPropertyName.CLINGS_FINISH.value}`
    - **Property Type:** {HubSpotPropertyType.TICKET_PROPERTY.value}
    - **Field Type:** {HubSpotFieldType.DROPDOWN.value}
    - **Required:** Yes (IF `{HubSpotPropertyName.PRODUCT_CATEGORY.value}` is '{ProductCategoryEnum.CLINGS.value}')
    - **List values:** {', '.join(f"'{e}'" for e in ClingsFinishEnum.get_all_values())}
    - **PQA Guidance Note:** For Clings, ask for the finish. No format selection is needed.

---
### Pouches
30. **Display Label:** Pouch Color
    - **HubSpot Internal Name:** `{HubSpotPropertyName.POUCHES_POUCH_COLOR.value}`
    - **Property Type:** {HubSpotPropertyType.TICKET_PROPERTY.value}
    - **Field Type:** {HubSpotFieldType.DROPDOWN.value}
    - **Required:** Yes (IF `{HubSpotPropertyName.PRODUCT_CATEGORY.value}` is '{ProductCategoryEnum.POUCHES.value}')
    - **List values:** {', '.join(f"'{e}'" for e in PouchesColor.get_all_values())}
    - **PQA Guidance Note:** If Product Category is Pouches, ask for the pouch color.

31. **Display Label:** Pouch Size
    - **HubSpot Internal Name:** `{HubSpotPropertyName.POUCHES_POUCH_SIZE.value}`
    - **Property Type:** {HubSpotPropertyType.TICKET_PROPERTY.value}
    - **Field Type:** {HubSpotFieldType.DROPDOWN.value}
    - **Required:** Yes (IF `{HubSpotPropertyName.PRODUCT_CATEGORY.value}` is '{ProductCategoryEnum.POUCHES.value}')
    - **List values:** {', '.join(f"'{e}'" for e in PouchesSizeEnum.get_all_values())}
    - **PQA Guidance Note:** If Product Category is Pouches, ask for the pouch size.

32. **Display Label:** Label Material
    - **HubSpot Internal Name:** `{HubSpotPropertyName.POUCHES_LABEL_MATERIAL.value}`
    - **Property Type:** {HubSpotPropertyType.TICKET_PROPERTY.value}
    - **Field Type:** {HubSpotFieldType.DROPDOWN.value}
    - **Required:** Yes (IF `{HubSpotPropertyName.PRODUCT_CATEGORY.value}` is '{ProductCategoryEnum.POUCHES.value}')
    - **List values:** {', '.join(f"'{e}'" for e in PouchesLabelMaterialEnum.get_all_values())}
    - **PQA Guidance Note:** If Product Category is Pouches, ask for the label material.

---
### Products Requiring No Additional Options
If the user selects one of the following Product Categories, do not ask for Format or Finish. Proceed directly to **II. Quote Information**.
- **Badges**
- **Patches**

**II. Quote Information (Step 2)**
*(PQA collects size and quantity after product is identified)*
33. **Display Label:** Total Quantity:
    - **HubSpot Internal Name:** `{HubSpotPropertyName.TOTAL_QUANTITY.value}`
    - **Property Type:** {HubSpotPropertyType.TICKET_PROPERTY.value}
    - **Field Type:** {HubSpotFieldType.NUMBER.value}
    - **Required:** Yes
    - **PQA Guidance Note:** Ask "What is the total quantity you are looking for?".
34. **Display Label:** Dimensions
    - **HubSpot Internal Name:** `{HubSpotPropertyName.WIDTH_IN_INCHES.value}`, `{HubSpotPropertyName.HEIGHT_IN_INCHES.value}`
    - **Property Type:** {HubSpotPropertyType.TICKET_PROPERTY.value}
    - **Field Type:** {HubSpotFieldType.NUMBER.value}
    - **Required:** Yes
    - **PQA Guidance Note:** Ask for dimensions in a single question: "What are the dimensions for your product (e.g., '3x3 inches')?". The PQA will parse the user's response for width and height values.

**III. Contact Information (Step 3)**
*(PQA collects the single point of contact)*
35. **Display Label:** Email
    - **HubSpot Internal Name:** `{HubSpotPropertyName.EMAIL.value}`
    - **Property Type:** {HubSpotPropertyType.CONTACT_PROPERTY.value}
    - **Field Type:** {HubSpotFieldType.SINGLE_LINE_TEXT.value}
    - **Required:** No (but one of email or phone is required)
    - **PQA Guidance Note:** Ask a single, clear question: "Perfect. And how can our team contact you with your quote? Please provide an email address or a phone number.".
36. **Display Label:** Phone number
    - **HubSpot Internal Name:** `{HubSpotPropertyName.PHONE.value}`
    - **Property Type:** {HubSpotPropertyType.CONTACT_PROPERTY.value}
    - **Field Type:** {HubSpotFieldType.PHONE_NUMBER.value}
    - **Required:** No (but one of email or phone is required)
    - **Limits:** Must be between 7 and 20 characters.
    - **PQA Guidance Note:** This is collected via the same question as the email.

**IV. Final Confirmation Question (Step 4)**
*(The very last question)*
37. **Display Label:** Are you a promotional product distributor?
    - **HubSpot Internal Name:** `{HubSpotPropertyName.PROMOTIONAL_PRODUCT_DISTRIBUTOR.value}`
    - **Property Type:** {HubSpotPropertyType.TICKET_PROPERTY.value}
    - **Field Type:** {HubSpotFieldType.SINGLE_CHECKBOX.value}
    - **Required:** No
    - **PQA Guidance Note:** Ask this as the final question: "Got it. One last thing: to make sure we get you to the right team, are you a promotional product distributor?".

**V. Optional & Context-Populated Fields**
*(These fields are not asked for directly. The PQA should parse the user's conversation and populate these fields if the user provides the information voluntarily.)*
38. **Display Label:** First name
    - **HubSpot Internal Name:** `{HubSpotPropertyName.FIRSTNAME.value}`
    - **Required:** No
    - **PQA Guidance Note:** Do not ask for this. Populate only if the user offers it.
39. **Display Label:** Last name
    - **HubSpot Internal Name:** `{HubSpotPropertyName.LASTNAME.value}`
    - **Required:** No
    - **PQA Guidance Note:** Do not ask for this. Populate only if the user offers it.
40. **Display Label:** Upload your design
    - **HubSpot Internal Name:** `{HubSpotPropertyName.UPLOAD_YOUR_DESIGN.value}`
    - **Required:** No
    - **PQA Guidance Note:** Do not ask for this. The Planner will prompt the user for a file after the ticket is created. If a file is uploaded during the conversation, this field can be noted as 'File Provided'.
41. **Display Label:** Additional Instructions:
    - **HubSpot Internal Name:** `{HubSpotPropertyName.ADDITIONAL_INSTRUCTIONS.value}`
    - **Required:** No
    - **PQA Guidance Note:** Do not ask for this directly. This field is a catch-all for any extra details the user provides during the conversation.

**VI. System Generated Fields (For AI agents internal use only):**
- **HubSpot Internal Name:** `{HubSpotPropertyName.SUBJECT.value}`
- **HubSpot Internal Name:** `{HubSpotPropertyName.CONTENT.value}`
- **HubSpot Internal Name:** `{HubSpotPropertyName.TYPE_OF_TICKET.value}`
"""
