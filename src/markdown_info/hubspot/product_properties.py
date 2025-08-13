"""
This file contains the markdown definition of HubSpot product properties for the custom quote form.
Used by the HubSpot agent to understand property names and valid values when updating tickets.
"""

from src.constants.custom_quote import (
    CustomQuotePropertyName,
    ProductGroupEnum,
    PreferredFormatEnum,
    TypeOfStickerEnum,
    TypeOfLabelEnum,
    TypeOfDecalEnum,
    TypeOfClingEnum,
    TypeOfMagnetEnum,
    TypeOfPackagingEnum,
    TypeOfPatchEnum,
    TypeOfTapeEnum,
    TypeOfTattooEnum,
    PouchSizeEnum,
    PouchLabelMaterialEnum,
    TapeSizeEnum,
)

HUBSPOT_PRODUCT_PROPERTIES_MARKDOWN = f"""
**HubSpot Product Properties Reference:**

## **PRODUCT SELECTION FIELDS**

### Product Group
- **Property Name:** `{CustomQuotePropertyName.PRODUCT_GROUP.value}`
- **Field Type:** Enumeration (Select)
- **Valid Values:** {', '.join(f"'{e}'" for e in ProductGroupEnum.get_all_values())}
- **Required:** No

### Preferred Format
- **Property Name:** `{CustomQuotePropertyName.PREFERRED_FORMAT.value}`
- **Field Type:** Enumeration (Select)
- **Valid Values:** {', '.join(f"'{e}'" for e in PreferredFormatEnum.get_all_values())}
- **Required:** No

---

## **PRODUCT TYPE SPECIFICATIONS**

### Type of Cling
- **Property Name:** `{CustomQuotePropertyName.TYPE_OF_CLING.value}`
- **Field Type:** Enumeration (Select)
- **Valid Values:** {', '.join(f"'{e}'" for e in TypeOfClingEnum.get_all_values())}
- **Required:** No

### Type of Decal
- **Property Name:** `{CustomQuotePropertyName.TYPE_OF_DECAL.value}`
- **Field Type:** Enumeration (Select)
- **Valid Values:** {', '.join(f"'{e}'" for e in TypeOfDecalEnum.get_all_values())}
- **Required:** No

### Type of Label
- **Property Name:** `{CustomQuotePropertyName.TYPE_OF_LABEL.value}`
- **Field Type:** Enumeration (Select)
- **Valid Values:** {', '.join(f"'{e}'" for e in TypeOfLabelEnum.get_all_values())}
- **Required:** No

### Type of Magnet
- **Property Name:** `{CustomQuotePropertyName.TYPE_OF_MAGNET.value}`
- **Field Type:** Enumeration (Select)
- **Valid Values:** {', '.join(f"'{e}'" for e in TypeOfMagnetEnum.get_all_values())}
- **Required:** No

### Type of Packaging
- **Property Name:** `{CustomQuotePropertyName.TYPE_OF_PACKAGING.value}`
- **Field Type:** Enumeration (Select)
- **Valid Values:** {', '.join(f"'{e}'" for e in TypeOfPackagingEnum.get_all_values())}
- **Required:** No

### Type of Patch
- **Property Name:** `{CustomQuotePropertyName.TYPE_OF_PATCH.value}`
- **Field Type:** Enumeration (Select)
- **Valid Values:** {', '.join(f"'{e}'" for e in TypeOfPatchEnum.get_all_values())}
- **Required:** No

### Type of Sticker
- **Property Name:** `{CustomQuotePropertyName.TYPE_OF_STICKER.value}`
- **Field Type:** Enumeration (Select)
- **Valid Values:** {', '.join(f"'{e}'" for e in TypeOfStickerEnum.get_all_values())}
- **Required:** No

### Type of Tape
- **Property Name:** `{CustomQuotePropertyName.TYPE_OF_TAPE.value}`
- **Field Type:** Enumeration (Select)
- **Valid Values:** {', '.join(f"'{e}'" for e in TypeOfTapeEnum.get_all_values())}
- **Required:** No

### Type of Tattoo
- **Property Name:** `{CustomQuotePropertyName.TYPE_OF_TATTOO.value}`
- **Field Type:** Enumeration (Select)
- **Valid Values:** {', '.join(f"'{e}'" for e in TypeOfTattooEnum.get_all_values())}
- **Required:** No

---

## **PACKAGING SPECIFIC FIELDS**

### Pouch Size
- **Property Name:** `{CustomQuotePropertyName.POUCH_SIZE.value}`
- **Field Type:** Enumeration (Select)
- **Valid Values:** {', '.join(f"'{e}'" for e in PouchSizeEnum.get_all_values())}
- **Required:** No

### Pouch Label Material
- **Property Name:** `{CustomQuotePropertyName.POUCH_LABEL_MATERIAL.value}`
- **Field Type:** Enumeration (Select)
- **Valid Values:** {', '.join(f"'{e}'" for e in PouchLabelMaterialEnum.get_all_values())}
- **Required:** No

---

## **TAPE SPECIFIC FIELDS**

### What Size of Tape
- **Property Name:** `{CustomQuotePropertyName.WHAT_SIZE_OF_TAPE.value}`
- **Field Type:** Enumeration (Select)
- **Valid Values:** {', '.join(f"'{e}'" for e in TapeSizeEnum.get_all_values())}
- **Required:** No

---

**IMPORTANT NOTES FOR HUBSPOT AGENT:**

1. **Exact Property Names**: Always use the exact property names as specified above when updating HubSpot tickets.

2. **Value Validation**: For enumeration fields, ensure the value being set exactly matches one of the valid values listed.

3. **Product Type Conditional Logic**: Different product types require different sets of properties:
   - Stickers: Use type_of_sticker_ property
   - Labels: Use type_of_label_ property
   - Decals: Use type_of_decal_ property
   - Clings: Use type_of_cling_ property
   - Magnets: Use type_of_magnet_ property
   - Packaging: Use type_of_packaging_, pouch_size_, and pouch_label_material_ properties
   - Patches: Use type_of_patch_ property
   - Tape: Use type_of_tape_ and what_size_of_tape_ properties
   - Tattoos: Use type_of_tattoo_ property

4. **Format Property**: The preferred_format property applies to multiple product types and should be used when available.

5. **Hidden Values**: Some product group values like "Services", "Signage", and "None Product Request" are marked as hidden in HubSpot but are still valid values.
"""
