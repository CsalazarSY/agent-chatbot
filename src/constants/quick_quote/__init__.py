"""
Quick Quote constants module.

This module contains constants for the HubSpot quick quote form properties.
These constants are derived from the JSON API data for the group:
"quote_information_-_quick_quote_-_changed_values"

This is the authoritative source for all product format and finish options
that were previously scattered across multiple files.
"""

from .property_names import QuickQuotePropertyName
from .form_properties import (
    # Product Categories
    ProductCategoryEnum,
    
    # Sticker Format and Finishes
    StickerFormatEnum,
    StickerDieCutFinishEnum,
    StickerKissCutFinishEnum,
    StickerPageSingleDesignFinishEnum,
    StickerPageMultipleDesignsFinishEnum,
    StickerRollsFinishEnum,
    StickerTransfersFinishEnum,
    
    # Labels Format and Finishes
    LabelsFormatEnum,
    LabelsKissCutFinishEnum,
    LabelsPageSingleDesignFinishEnum,
    LabelsPageMultipleDesignsFinishEnum,
    LabelsRollsFinishEnum,
    LabelsImageTransfersFinishEnum,
    
    # Decals Format and Finishes
    DecalsFormatEnum,
    DecalsWallWindowFinishEnum,
    DecalsFloorOutdoorFinishEnum,
    DecalsImageTransfersFinishEnum,
    
    # Iron-Ons Format and Finishes
    IronOnsFormatEnum,
    IronOnsPageSingleDesignFinishEnum,
    IronOnsPageMultipleDesignsFinishEnum,
    IronOnsTransfersFinishEnum,
    
    # Temp Tattoos Format and Finishes
    TempTattoosFormatEnum,
    TempTattoosKissCutFinishEnum,
    TempTattoosPageSingleDesignFinishEnum,
    TempTattoosPageMultipleDesignsFinishEnum,
    
    # Specialized Product Finishes
    ClingsFinishEnum,
    MagnetsFinishEnum,
    ImageTransfersFinishEnum,
    
    # Pouches Options
    PouchesColor,
    PouchesSizeEnum,
    PouchesLabelMaterialEnum,
)

# Import pouch size and material from custom_quote (identical values) - DEPRECATED
# Note: We now define these locally in form_properties to keep quick_quote self-contained
# from ..custom_quote import PouchSizeEnum, PouchLabelMaterialEnum

__all__ = [
    "QuickQuotePropertyName",
    
    # Product Categories
    "ProductCategoryEnum",
    
    # Sticker Format and Finishes
    "StickerFormatEnum",
    "StickerDieCutFinishEnum",
    "StickerKissCutFinishEnum",
    "StickerPageSingleDesignFinishEnum",
    "StickerPageMultipleDesignsFinishEnum",
    "StickerRollsFinishEnum",
    "StickerTransfersFinishEnum",
    
    # Labels Format and Finishes
    "LabelsFormatEnum",
    "LabelsKissCutFinishEnum",
    "LabelsPageSingleDesignFinishEnum",
    "LabelsPageMultipleDesignsFinishEnum",
    "LabelsRollsFinishEnum",
    "LabelsImageTransfersFinishEnum",
    
    # Decals Format and Finishes
    "DecalsFormatEnum",
    "DecalsWallWindowFinishEnum",
    "DecalsFloorOutdoorFinishEnum",
    "DecalsImageTransfersFinishEnum",
    
    # Iron-Ons Format and Finishes
    "IronOnsFormatEnum",
    "IronOnsPageSingleDesignFinishEnum",
    "IronOnsPageMultipleDesignsFinishEnum",
    "IronOnsTransfersFinishEnum",
    
    # Temp Tattoos Format and Finishes
    "TempTattoosFormatEnum",
    "TempTattoosKissCutFinishEnum",
    "TempTattoosPageSingleDesignFinishEnum",
    "TempTattoosPageMultipleDesignsFinishEnum",
    
    # Specialized Product Finishes
    "ClingsFinishEnum",
    "MagnetsFinishEnum",
    "ImageTransfersFinishEnum",
    
    # Pouches Options
    "PouchesColor",
    "PouchesSizeEnum",
    "PouchesLabelMaterialEnum",
]
