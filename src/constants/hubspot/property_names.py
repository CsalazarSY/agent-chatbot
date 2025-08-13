"""
Unified HubSpot Property Names.

This module creates a comprehensive enum that includes all property names
from all HubSpot form groups: quick quote, custom quote, and ticket custom properties.
This provides a single source of truth for all HubSpot property names while
maintaining the organized structure.
"""

from enum import Enum
from ..quick_quote.property_names import QuickQuotePropertyName
from ..custom_quote.property_names import CustomQuotePropertyName
from .custom_properties_values import TicketCustomPropertyName


class HubSpotPropertyName(str, Enum):
    """
    Unified HubSpot property names from all form groups.
    
    This enum combines property names from:
    - Quick Quote form (quote_information_-_quick_quote_-_changed_values)
    - Custom Quote form (custom_quote_properties) 
    - Ticket Custom properties (ticket_information_-_custom)
    - Additional HubSpot-defined properties
    """
    
    # =============================================================================
    # HUBSPOT CORE PROPERTIES (Ticket Management)
    # =============================================================================
    
    # Required Base Fields
    SUBJECT = "subject"
    CONTENT = "content"
    HS_PIPELINE = "hs_pipeline"
    HS_PIPELINE_STAGE = "hs_pipeline_stage"
    HS_TICKET_PRIORITY = "hs_ticket_priority"
    
    # Contact Properties
    FIRSTNAME = "firstname"
    LASTNAME = "lastname"
    EMAIL = "email"
    PHONE = "phone"
    COMPANY = "company"
    
    # HubSpot-Defined Ticket Properties
    CREATED_BY = "created_by"
    HS_CUSTOM_INBOX = "hs_custom_inbox"
    HS_FILE_UPLOAD = "hs_file_upload"
    HS_IN_HELPDESK = "hs_in_helpdesk"
    HS_INBOX_ID = "hs_inbox_id"
    HS_OBJECT_ID = "hs_object_id"
    HS_OBJECT_SOURCE = "hs_object_source"
    HS_TICKET_CATEGORY = "hs_ticket_category"
    HS_TICKET_ID = "hs_ticket_id"
    HS_TICKET_LANGUAGE_AI_TAG = "hs_ticket_language_ai_tag"
    HS_UNIQUE_CREATION_KEY = "hs_unique_creation_key"
    HUBSPOT_OWNER_ID = "hubspot_owner_id"
    SOURCE_TYPE = "source_type"
    
    # =============================================================================
    # QUICK QUOTE PROPERTIES (Dynamically imported)
    # =============================================================================
    
    # Product selection
    PRODUCT_CATEGORY = QuickQuotePropertyName.PRODUCT_CATEGORY.value
    
    # Stickers
    STICKER_FORMAT = QuickQuotePropertyName.STICKER_FORMAT.value
    STICKER_DIE_CUT_FINISH = QuickQuotePropertyName.STICKER_DIE_CUT_FINISH.value
    STICKER_KISS_CUT_FINISH = QuickQuotePropertyName.STICKER_KISS_CUT_FINISH.value
    STICKER_PAGE_SINGLE_DESIGN_FINISH = QuickQuotePropertyName.STICKER_PAGE_SINGLE_DESIGN_FINISH.value
    STICKER_PAGE_MULTIPLE_DESIGNS_FINISH = QuickQuotePropertyName.STICKER_PAGE_MULTIPLE_DESIGNS_FINISH.value
    STICKER_ROLLS_FINISH = QuickQuotePropertyName.STICKER_ROLLS_FINISH.value
    STICKER_TRANSFERS_FINISH = QuickQuotePropertyName.STICKER_TRANSFERS_FINISH.value
    
    # Labels
    LABELS_FORMAT = QuickQuotePropertyName.LABELS_FORMAT.value
    LABELS_KISS_CUT_FINISH = QuickQuotePropertyName.LABELS_KISS_CUT_FINISH.value
    LABELS_PAGE_SINGLE_DESIGN_FINISH = QuickQuotePropertyName.LABELS_PAGE_SINGLE_DESIGN_FINISH.value
    LABELS_PAGE_MULTIPLE_DESIGNS_FINISH = QuickQuotePropertyName.LABELS_PAGE_MULTIPLE_DESIGNS_FINISH.value
    LABELS_ROLLS_FINISH = QuickQuotePropertyName.LABELS_ROLLS_FINISH.value
    LABELS_IMAGE_TRANSFERS_FINISH = QuickQuotePropertyName.LABELS_IMAGE_TRANSFERS_FINISH.value
    
    # Decals
    DECALS_FORMAT = QuickQuotePropertyName.DECALS_FORMAT.value
    DECALS_WALL_WINDOW_FINISH = QuickQuotePropertyName.DECALS_WALL_WINDOW_FINISH.value
    DECALS_FLOOR_OUTDOOR_FINISH = QuickQuotePropertyName.DECALS_FLOOR_OUTDOOR_FINISH.value
    DECALS_IMAGE_TRANSFERS_FINISH = QuickQuotePropertyName.DECALS_IMAGE_TRANSFERS_FINISH.value
    
    # Iron-Ons
    IRON_ONS_FORMAT = QuickQuotePropertyName.IRON_ONS_FORMAT.value
    IRON_ONS_PAGE_SINGLE_DESIGN_FINISH = QuickQuotePropertyName.IRON_ONS_PAGE_SINGLE_DESIGN_FINISH.value
    IRON_ONS_PAGE_MULTIPLE_DESIGNS_FINISH = QuickQuotePropertyName.IRON_ONS_PAGE_MULTIPLE_DESIGNS_FINISH.value
    IRON_ONS_TRANSFERS_FINISH = QuickQuotePropertyName.IRON_ONS_TRANSFERS_FINISH.value
    
    # Temp Tattoos
    TEMP_TATTOOS_FORMAT = QuickQuotePropertyName.TEMP_TATTOOS_FORMAT.value
    TEMP_TATTOOS_KISS_CUT_FINISH = QuickQuotePropertyName.TEMP_TATTOOS_KISS_CUT_FINISH.value
    TEMP_TATTOOS_PAGE_SINGLE_DESIGN_FINISH = QuickQuotePropertyName.TEMP_TATTOOS_PAGE_SINGLE_DESIGN_FINISH.value
    TEMP_TATTOOS_PAGE_MULTIPLE_DESIGNS_FINISH = QuickQuotePropertyName.TEMP_TATTOOS_PAGE_MULTIPLE_DESIGNS_FINISH.value
    
    # Specialized Products
    CLINGS_FINISH = QuickQuotePropertyName.CLINGS_FINISH.value
    MAGNETS_FINISH = QuickQuotePropertyName.MAGNETS_FINISH.value
    IMAGE_TRANSFERS_FINISH = QuickQuotePropertyName.IMAGE_TRANSFERS_FINISH.value
    
    # Pouches
    POUCHES_POUCH_SIZE = QuickQuotePropertyName.POUCHES_POUCH_SIZE.value
    POUCHES_POUCH_COLOR = QuickQuotePropertyName.POUCHES_POUCH_COLOR.value
    POUCHES_LABEL_MATERIAL = QuickQuotePropertyName.POUCHES_LABEL_MATERIAL.value
    
    # =============================================================================
    # CUSTOM QUOTE PROPERTIES (Dynamically imported)
    # =============================================================================
    
    # Basic Information
    ADDITIONAL_INSTRUCTIONS = CustomQuotePropertyName.ADDITIONAL_INSTRUCTIONS.value
    APPLICATION_USE = CustomQuotePropertyName.APPLICATION_USE.value
    
    # Business Information  
    BUSINESS_CATEGORY = CustomQuotePropertyName.BUSINESS_CATEGORY.value
    OTHER_BUSINESS_CATEGORY = CustomQuotePropertyName.OTHER_BUSINESS_CATEGORY.value
    PROMOTIONAL_PRODUCT_DISTRIBUTOR = CustomQuotePropertyName.PROMOTIONAL_PRODUCT_DISTRIBUTOR.value
    
    # Customer Information
    CALL_REQUESTED = CustomQuotePropertyName.CALL_REQUESTED.value
    HAVE_YOU_ORDERED_WITH_US_BEFORE = CustomQuotePropertyName.HAVE_YOU_ORDERED_WITH_US_BEFORE.value
    HOW_DID_YOU_FIND_US = CustomQuotePropertyName.HOW_DID_YOU_FIND_US.value
    WHAT_KIND_OF_CONTENT_WOULD_YOU_LIKE_TO_HEAR_ABOUT = CustomQuotePropertyName.WHAT_KIND_OF_CONTENT_WOULD_YOU_LIKE_TO_HEAR_ABOUT.value
    WHAT_MADE_YOU_COME_BACK_TO_STICKER_YOU = CustomQuotePropertyName.WHAT_MADE_YOU_COME_BACK_TO_STICKER_YOU.value
    
    # Location and Use
    LOCATION = CustomQuotePropertyName.LOCATION.value
    USE_TYPE = CustomQuotePropertyName.USE_TYPE.value
    
    # Product Dimensions and Quantity
    HEIGHT_IN_INCHES = CustomQuotePropertyName.HEIGHT_IN_INCHES.value
    WIDTH_IN_INCHES = CustomQuotePropertyName.WIDTH_IN_INCHES.value
    TOTAL_QUANTITY = CustomQuotePropertyName.TOTAL_QUANTITY.value
    
    # Design Specifications
    NUMBER_OF_COLOURS_IN_DESIGN = CustomQuotePropertyName.NUMBER_OF_COLOURS_IN_DESIGN.value
    
    # Product Selection
    PRODUCT_GROUP = CustomQuotePropertyName.PRODUCT_GROUP.value
    PRODUCT_GROUP_2 = CustomQuotePropertyName.PRODUCT_GROUP_2.value
    PREFERRED_FORMAT = CustomQuotePropertyName.PREFERRED_FORMAT.value
    PREFERRED_FORMAT_STICKERS = CustomQuotePropertyName.PREFERRED_FORMAT_STICKERS.value
    
    # Product Type Specifications
    TYPE_OF_CLING = CustomQuotePropertyName.TYPE_OF_CLING.value
    TYPE_OF_DECAL = CustomQuotePropertyName.TYPE_OF_DECAL.value
    TYPE_OF_IMAGE_TRANSFER = CustomQuotePropertyName.TYPE_OF_IMAGE_TRANSFER.value
    TYPE_OF_LABEL = CustomQuotePropertyName.TYPE_OF_LABEL.value
    TYPE_OF_MAGNET = CustomQuotePropertyName.TYPE_OF_MAGNET.value
    TYPE_OF_PACKAGING = CustomQuotePropertyName.TYPE_OF_PACKAGING.value
    TYPE_OF_PATCH = CustomQuotePropertyName.TYPE_OF_PATCH.value
    TYPE_OF_STICKER = CustomQuotePropertyName.TYPE_OF_STICKER.value
    TYPE_OF_TAPE = CustomQuotePropertyName.TYPE_OF_TAPE.value
    TYPE_OF_TATTOO = CustomQuotePropertyName.TYPE_OF_TATTOO.value
    
    # Packaging Specific
    POUCH_LABEL_MATERIAL = CustomQuotePropertyName.POUCH_LABEL_MATERIAL.value
    POUCH_SIZE = CustomQuotePropertyName.POUCH_SIZE.value
    
    # Tape Specific
    WHAT_SIZE_OF_TAPE = CustomQuotePropertyName.WHAT_SIZE_OF_TAPE.value
    
    # File Uploads
    UPLOAD_YOUR_DESIGN = CustomQuotePropertyName.UPLOAD_YOUR_DESIGN.value
    UPLOAD_YOUR_VECTOR_ARTWORK = CustomQuotePropertyName.UPLOAD_YOUR_VECTOR_ARTWORK.value
    
    # =============================================================================
    # TICKET CUSTOM PROPERTIES (Dynamically imported)
    # =============================================================================
    
    # Ticket Management
    CONTACT_OWNER = TicketCustomPropertyName.CONTACT_OWNER.value
    TYPE_OF_TICKET = TicketCustomPropertyName.TYPE_OF_TICKET.value
    
    # Workflow and Automation
    CREATE_HOUR = TicketCustomPropertyName.CREATE_HOUR.value
    CREATED_ON_BUSINESS_HOURS = TicketCustomPropertyName.CREATED_ON_BUSINESS_HOURS.value
    OWNER_AVAILABILITY = TicketCustomPropertyName.OWNER_AVAILABILITY.value
    WAS_HANDED_OFF = TicketCustomPropertyName.WAS_HANDED_OFF.value
    
    # Additional Custom Quote Properties (not in organized modules)
    ORDER_NUMBER = "order_number"
