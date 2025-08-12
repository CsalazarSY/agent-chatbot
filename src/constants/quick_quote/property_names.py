"""
Quick Quote Property Names - HubSpot API field names.

This file contains the exact property names as they appear in HubSpot
for the quick quote form group: "quote_information_-_quick_quote_-_changed_values"
"""

from ..base import BaseEnum


class QuickQuotePropertyName(BaseEnum):
    """Property names for quick quote form fields in HubSpot."""
    
    # Product selection
    PRODUCT_CATEGORY = "product_category"
    
    # Stickers
    STICKER_FORMAT = "sticker_format"
    STICKER_DIE_CUT_FINISH = "sticker_die_cut_finish"
    STICKER_KISS_CUT_FINISH = "sticker_kiss_cut_finish"
    STICKER_PAGE_SINGLE_DESIGN_FINISH = "sticker_page_single_design_finish"
    STICKER_PAGE_MULTIPLE_DESIGNS_FINISH = "sticker_page_multiple_designs_finish"
    STICKER_ROLLS_FINISH = "sticker_rolls_finish"
    STICKER_TRANSFERS_FINISH = "sticker_transfers_finish"
    
    # Labels
    LABELS_FORMAT = "labels_format"
    LABELS_KISS_CUT_FINISH = "labels_kiss_cut_finish"
    LABELS_PAGE_SINGLE_DESIGN_FINISH = "labels_page_single_design_finish"
    LABELS_PAGE_MULTIPLE_DESIGNS_FINISH = "labels_page_multiple_designs_finish"
    LABELS_ROLLS_FINISH = "labels_rolls_finish"
    LABELS_IMAGE_TRANSFERS_FINISH = "labels_image_transfers_finish"
    
    # Decals
    DECALS_FORMAT = "decals_format"
    DECALS_WALL_WINDOW_FINISH = "decals_wall_window_finish"
    DECALS_FLOOR_OUTDOOR_FINISH = "decals_floor_outdoor_finish"
    DECALS_IMAGE_TRANSFERS_FINISH = "decals_image_transfers_finish"
    
    # Iron-Ons
    IRON_ONS_FORMAT = "iron_ons_format"
    IRON_ONS_PAGE_SINGLE_DESIGN_FINISH = "iron_ons_page_single_design_finish"
    IRON_ONS_PAGE_MULTIPLE_DESIGNS_FINISH = "iron_ons_page_multiple_designs_finish"
    IRON_ONS_TRANSFERS_FINISH = "iron_ons_transfers_finish"
    
    # Temp Tattoos
    TEMP_TATTOOS_FORMAT = "temp_tattoos_format"
    TEMP_TATTOOS_KISS_CUT_FINISH = "temp_tattoos_kiss_cut_finish"
    TEMP_TATTOOS_PAGE_SINGLE_DESIGN_FINISH = "temp_tattoos_page_single_design_finish"
    TEMP_TATTOOS_PAGE_MULTIPLE_DESIGNS_FINISH = "temp_tattoos_page_multiple_designs_finish"
    
    # Specialized Products
    CLINGS_FINISH = "clings_finish"
    MAGNETS_FINISH = "magnets_finish"
    IMAGE_TRANSFERS_FINISH = "image_transfers_finish"
    
    # Pouches
    POUCHES_POUCH_SIZE = "pouches_pouch_size"
    POUCHES_POUCH_COLOR = "pouches_pouch_color"
    POUCHES_LABEL_MATERIAL = "pouches_label_material"
