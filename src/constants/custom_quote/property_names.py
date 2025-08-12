"""
HubSpot Property Names for Custom Quote Form.

This file contains the exact property names as they appear in HubSpot
for the custom quote form fields. These match the "name" field in the
HubSpot API JSON data.
"""

from ..base import BaseEnum


class CustomQuotePropertyName(BaseEnum):
    """HubSpot property names for custom quote form fields."""
    
    # Basic Information
    ADDITIONAL_INSTRUCTIONS = "additional_instructions_"
    APPLICATION_USE = "application_use_"
    
    # Business Information
    BUSINESS_CATEGORY = "business_category"
    OTHER_BUSINESS_CATEGORY = "other_business_category"
    PROMOTIONAL_PRODUCT_DISTRIBUTOR = "promotional_product_distributor_"
    
    # Customer Information
    CALL_REQUESTED = "call_requested"
    HAVE_YOU_ORDERED_WITH_US_BEFORE = "have_you_ordered_with_us_before_"
    HOW_DID_YOU_FIND_US = "how_did_you_find_us_"
    WHAT_KIND_OF_CONTENT_WOULD_YOU_LIKE_TO_HEAR_ABOUT = "what_kind_of_content_would_you_like_to_hear_about_"
    WHAT_MADE_YOU_COME_BACK_TO_STICKER_YOU = "what_made_you_come_back_to_sticker_you_"
    
    # Location and Use
    LOCATION = "location"
    USE_TYPE = "use_type"
    
    # Product Dimensions and Quantity
    HEIGHT_IN_INCHES = "height_in_inches_"
    WIDTH_IN_INCHES = "width_in_inches_"
    TOTAL_QUANTITY = "total_quantity_"
    
    # Design Specifications
    NUMBER_OF_COLOURS_IN_DESIGN = "number_of_colours_in_design_"
    
    # Product Selection
    PRODUCT_GROUP = "product_group"
    PRODUCT_GROUP_2 = "product_group_2"
    PREFERRED_FORMAT = "preferred_format"
    PREFERRED_FORMAT_STICKERS = "preferred_format_stickers"
    
    # Product Type Specifications
    TYPE_OF_CLING = "type_of_cling_"
    TYPE_OF_DECAL = "type_of_decal_"
    TYPE_OF_IMAGE_TRANSFER = "type_of_image_transfer_"
    TYPE_OF_LABEL = "type_of_label_"
    TYPE_OF_MAGNET = "type_of_magnet_"
    TYPE_OF_PACKAGING = "type_of_packaging_"
    TYPE_OF_PATCH = "type_of_patch_"
    TYPE_OF_STICKER = "type_of_sticker_"
    TYPE_OF_TAPE = "type_of_tape_"
    TYPE_OF_TATTOO = "type_of_tattoo_"
    
    # Packaging Specific
    POUCH_LABEL_MATERIAL = "pouch_label_material_"
    POUCH_SIZE = "pouch_size_"
    
    # Tape Specific
    WHAT_SIZE_OF_TAPE = "what_size_of_tape_"
    
    # File Uploads
    UPLOAD_YOUR_DESIGN = "upload_your_design"
    UPLOAD_YOUR_VECTOR_ARTWORK = "upload_your_vector_artwork"
