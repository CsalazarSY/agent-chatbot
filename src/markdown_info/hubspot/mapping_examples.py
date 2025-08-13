"""
HubSpot Agent Translation Examples

This module contains comprehensive examples demonstrating how the HubSpot agent
should perform property translation from AI-friendly format to HubSpot API format.
"""

HUBSPOT_TRANSLATION_EXAMPLES_MARKDOWN = """
# Translation Examples: Step-by-Step Reasoning Process

## Overview
These concrete examples demonstrate how you MUST perform the translation from AI-friendly 
properties to HubSpot API properties. Follow this exact thought process for every translation.

## Translation Process Summary
1. **Recognize**: Identify AI-friendly product properties in the payload
2. **Read Values**: Extract the user's product requirements 
3. **Find HubSpot Match**: Map to correct HubSpot property names and values
4. **Enhance Payload**: Add HubSpot properties while preserving original data

---
## Example 1: Standard Sticker (Holographic)

### Input Payload from Planner:
```json
{
  "product_category": "Stickers",
  "sticker_format": "Die-Cut", 
  "sticker_die_cut_finish": "Permanent Holographic Permanent Glossy",
  "total_quantity_": 500
}
```

### Translation Steps:
1. **Recognize**: Found AI-friendly properties → `product_category`, `sticker_format`, `sticker_die_cut_finish`
2. **Read Values**: User wants Stickers, Die-Cut format, Holographic material
3. **Find HubSpot Match**:
   - `product_category: "Stickers"` → `product_group: "Sticker"`
   - `sticker_format: "Die-Cut"` → `preferred_format: "Die-Cut Singles"`
   - Material contains "Holographic" → `type_of_sticker_: "Holographic"`
4. **Enhance Payload**: Add 3 HubSpot properties to original payload

### Enhanced Output for API:
```json
{
  "product_category": "Stickers",
  "sticker_format": "Die-Cut",
  "sticker_die_cut_finish": "Permanent Holographic Permanent Glossy", 
  "total_quantity_": 500,
  "product_group": "Sticker",
  "preferred_format": "Die-Cut Singles",
  "type_of_sticker_": "Holographic"
}
```

---
## Example 2: Label on a Roll

### Input Payload from Planner:
```json
{
  "product_category": "Labels",
  "labels_format": "Rolls",
  "labels_rolls_finish": "White BOPP Permanent Glossy (Laminated)"
}
```

### Translation Steps:
1. **Recognize**: Found AI-friendly properties → `product_category`, `labels_format`, `labels_rolls_finish`
2. **Read Values**: User wants Labels, Rolls format, White BOPP material
3. **Find HubSpot Match**:
   - `product_category: "Labels"` → `product_group: "Roll Label"`
   - Material contains "White BOPP" → `type_of_label_: "White BOPP"`
   - Note: For Rolls, `product_group` defines format (no separate `preferred_format`)
4. **Enhance Payload**: Add 2 HubSpot properties to original payload

### Enhanced Output for API:
```json
{
  "product_category": "Labels",
  "labels_format": "Rolls", 
  "labels_rolls_finish": "White BOPP Permanent Glossy (Laminated)",
  "product_group": "Roll Label",
  "type_of_label_": "White BOPP"
}
```

---
## Example 3: Decal for Window Application

### Input Payload from Planner:
```json
{
  "product_category": "Decals",
  "decals_format": "Wall & Window", 
  "decals_wall_window_finish": "Clear Vinyl Removable Glossy"
}
```

### Translation Steps:
1. **Recognize**: Found AI-friendly properties → `product_category`, `decals_format`, `decals_wall_window_finish`
2. **Read Values**: User wants Decals, Wall & Window application, Clear Vinyl material
3. **Find HubSpot Match**:
   - `product_category: "Decals"` → `product_group: "Decal"`
   - Format "Wall & Window" + Material "Clear Vinyl" → `type_of_decal_: "Clear Window"`
4. **Enhance Payload**: Add 2 HubSpot properties to original payload

### Enhanced Output for API:
```json
{
  "product_category": "Decals",
  "decals_format": "Wall & Window",
  "decals_wall_window_finish": "Clear Vinyl Removable Glossy",
  "product_group": "Decal",
  "type_of_decal_": "Clear Window"
}
```

---
## Example 4: Special Case - Iron-On (Maps to Tattoo Group)

### Input Payload from Planner:
```json
{
  "product_category": "Iron-Ons",
  "iron_ons_format": "Page (Single Design)",
  "iron_ons_page_single_design_finish": "Iron-Ons Singles"
}
```

### Translation Steps:
1. **Recognize**: Found AI-friendly properties → `product_category`, `iron_ons_format`, `iron_ons_page_single_design_finish`
2. **Read Values**: User wants Iron-Ons, Page format with single design
3. **Find HubSpot Match** (Special Mapping):
   - `product_category: "Iron-Ons"` → `product_group: "Tattoo"`  **Special Case**
   - `iron_ons_format: "Page (Single Design)"` → `preferred_format: "Pages"`
   - Iron-on transfers → `type_of_tattoo_: "Standard Tattoo"`
4. **Enhance Payload**: Add 3 HubSpot properties (note the special mapping)

### Enhanced Output for API:
```json
{
  "product_category": "Iron-Ons",
  "iron_ons_format": "Page (Single Design)",
  "iron_ons_page_single_design_finish": "Iron-Ons Singles",
  "product_group": "Tattoo",
  "preferred_format": "Pages", 
  "type_of_tattoo_": "Standard Tattoo"
}
```

---
## Example 5: Simple Product - Car Magnet

### Input Payload from Planner:
```json
{
  "product_category": "Magnets",
  "magnets_finish": "Die-Cut Car Magnets"
}
```

### Translation Steps:
1. **Recognize**: Found AI-friendly properties → `product_category`, `magnets_finish`
2. **Read Values**: User wants Magnets, specifically Car Magnets (die-cut)
3. **Find HubSpot Match**:
   - `product_category: "Magnets"` → `product_group: "Magnet"`
   - Finish contains "Car Magnets" → `type_of_magnet_: "Car Magnet"`
4. **Enhance Payload**: Add 2 HubSpot properties to original payload

### Enhanced Output for API:
```json
{
  "product_category": "Magnets",
  "magnets_finish": "Die-Cut Car Magnets",
  "product_group": "Magnet",
  "type_of_magnet_": "Car Magnet"
}
```

---
## Example 6: Complex Product - Custom Pouch (Multiple Properties)

### Input Payload from Planner:
```json
{
  "product_category": "Pouches",
  "pouches_pouch_size": "5\"x 7\" x 3\" (Stand-Up)",
  "pouches_pouch_color": "Kraft Paper",
  "pouches_label_material": "White Paper"
}
```

### Translation Steps:
1. **Recognize**: Found AI-friendly properties → `product_category`, `pouches_pouch_size`, `pouches_pouch_color`, `pouches_label_material`
2. **Read Values**: User wants Pouches, 5x7x3 size, Kraft Paper color, White Paper label
3. **Find HubSpot Match**:
   - `product_category: "Pouches"` → `product_group: "Packaging"`
   - `pouches_pouch_color: "Kraft Paper"` → `type_of_packaging_: "Kraft Paper Pouch"`
   - `pouches_pouch_size` → `pouch_size_` (direct mapping)
   - `pouches_label_material` → `pouch_label_material_` (direct mapping)
4. **Enhance Payload**: Add 4 HubSpot properties to original payload

### Enhanced Output for API:
```json
{
  "product_category": "Pouches",
  "pouches_pouch_size": "5\"x 7\" x 3\" (Stand-Up)",
  "pouches_pouch_color": "Kraft Paper",
  "pouches_label_material": "White Paper",
  "product_group": "Packaging",
  "type_of_packaging_": "Kraft Paper Pouch",
  "pouch_size_": "5\"x 7\" x 3\" (Stand-Up)",
  "pouch_label_material_": "White Paper"
}
```

---
## Example 7: Standard Tattoo
**Planner Payload Received:**
```json
{
  "product_category": "Temp Tattoos",
  "temp_tattoos_format": "Kiss-Cut",
  "temp_tattoos_kiss_cut_finish": "Removable Clear Matte"
}
```
**Your Internal Reasoning Steps:**
- Recognize: The payload is for "Temp Tattoos".
- Read Values: The user wants "Temp Tattoos" in "Kiss-Cut" format.
- Find HubSpot Match:
    - `product_category`: "Temp Tattoos" → `product_group`: "Tattoo"
    - Format "Kiss-Cut" → `preferred_format`: "Kiss-Cut Singles"
    - Material "Removable Clear Matte" → `type_of_tattoo_`: "Standard Tattoo"
- Enhance Payload: Add the three translated HubSpot properties.
**Final Enhanced Payload for API Call:**
```json
{
  "product_category": "Temp Tattoos",
  "temp_tattoos_format": "Kiss-Cut",
  "temp_tattoos_kiss_cut_finish": "Removable Clear Matte",
  "product_group": "Tattoo",
  "preferred_format": "Kiss-Cut Singles",
  "type_of_tattoo_": "Standard Tattoo"
}
```

---
## Example 8: Sticker with "Page" Format
**Planner Payload Received:**
```json
{
  "product_category": "Stickers",
  "sticker_format": "Page (Single Design)",
  "sticker_page_single_design_finish": "White Vinyl Removable Matte"
}
```
**Your Internal Reasoning Steps:**
- Recognize: AI-friendly properties for a page of stickers.
- Read Values: "Stickers", "Page (Single Design)", "White Vinyl Removable Matte".
- Find HubSpot Match:
    - `product_category`: "Stickers" → `product_group`: "Sticker"
    - `sticker_format`: "Page (Single Design)" → `preferred_format`: "Pages"
    - Material "White Vinyl Removable Matte" → `type_of_sticker_`: "Matte White Vinyl"
- Enhance Payload: Add the three new HubSpot properties.
**Final Enhanced Payload for API Call:**
```json
{
  "product_category": "Stickers",
  "sticker_format": "Page (Single Design)",
  "sticker_page_single_design_finish": "White Vinyl Removable Matte",
  "product_group": "Sticker",
  "preferred_format": "Pages",
  "type_of_sticker_": "Matte White Vinyl"
}
```

---
## Example 9: Special Case - Image Transfer
**Planner Payload Received:**
```json
{
  "product_category": "Image Transfers",
  "image_transfers_finish": "Permanent Glossy Image Transfer Sticker"
}
```
**Your Internal Reasoning Steps:**
- Recognize: The payload is for "Image Transfers".
- Read Values: The user wants "Image Transfers" with a specific finish.
- Find HubSpot Match (Special Case):
    - `product_category`: "Image Transfers" → `product_group`: "Sticker"
    - Finish "Permanent Glossy Image Transfer Sticker" → `type_of_sticker_`: "UV DTF Image Transfer Sticker"
- Enhance Payload: Add the two translated HubSpot properties.
**Final Enhanced Payload for API Call:**
```json
{
  "product_category": "Image Transfers",
  "image_transfers_finish": "Permanent Glossy Image Transfer Sticker",
  "product_group": "Sticker",
  "type_of_sticker_": "UV DTF Image Transfer Sticker"
}
```

---
## Example 10: Non-Product Update (No Translation Required)

### Input Payload from Planner:
```json
{
  "content": "User has confirmed their shipping address is correct.",
  "hs_ticket_priority": "MEDIUM"
}
```

### Translation Steps:
1. **Recognize**: No AI-friendly product properties found
2. **Read Values**: General ticket update, no product information
3. **Find HubSpot Match**: N/A - No product properties to translate
4. **Enhance Payload**: No enhancement needed - use payload as-is

### Enhanced Output for API:
```json
{
  "content": "User has confirmed their shipping address is correct.",
  "hs_ticket_priority": "MEDIUM"
}
```

---
## Key Translation Patterns Summary

### Common Mappings:
- `product_category: "Stickers"` → `product_group: "Sticker"`
- `product_category: "Labels"` → `product_group: "Roll Label"` (for Rolls)
- `product_category: "Decals"` → `product_group: "Decal"`
- `product_category: "Magnets"` → `product_group: "Magnet"`
- `product_category: "Pouches"` → `product_group: "Packaging"`

### Special Cases:
- `product_category: "Iron-Ons"` → `product_group: "Tattoo"` 
- `product_category: "Temp Tattoos"` → `product_group: "Tattoo"`
- `product_category: "Image Transfers"` → `product_group: "Sticker"` 

### Format Mappings:
- `"Die-Cut"` → `preferred_format: "Die-Cut Singles"`
- `"Page (Single Design)"` → `preferred_format: "Pages"`
- `"Kiss-Cut"` → `preferred_format: "Kiss-Cut Singles"`

**Remember**: Always preserve original AI-friendly properties while adding HubSpot equivalents!
"""
