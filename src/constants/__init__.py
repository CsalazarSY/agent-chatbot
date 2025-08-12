"""Constants package - organized constants by domain."""

# Base constants
from .base import (
    BaseEnum,
)

# HubSpot constants
from .hubspot import (
    HubSpotFieldType,
    HubSpotPropertyType,
    HubSpotTicketCategoryEnum,
    HubSpotTicketPriorityEnum,
    HubSpotSourceTypeEnum,
    HubSpotTicketLanguageEnum,
    HubSpotPropertyName,
    # Custom Ticket Properties
    TicketCustomPropertyName,
    TicketTypeEnum,
    OwnerAvailabilityEnum,
)

# All product-related constants are now imported from quick_quote as authoritative source
# (Legacy wrapper files stickers.py, labels.py, products.py, other_products.py are deprecated)

# Business and marketing constants - MOVED TO CUSTOM_QUOTE
# Note: BusinessCategoryEnum, HowDidYouFindUsEnum, ContentPreferenceEnum, 
# and WhatMadeYouComeBackEnum have been moved to custom_quote module
# as they are specifically used for HubSpot custom quote forms

# Custom Quote Form constants
from .custom_quote import (
    CustomQuotePropertyName,
    BusinessCategoryEnum,
    HowDidYouFindUsEnum,
    WhatMadeYouComeBackEnum,
    ContentPreferenceEnum,
    LocationEnum,
    UseTypeEnum,
    YesNoEnum,
    ProductGroupEnum,
    PreferredFormatEnum,
    NumberOfColoursInDesignEnum,
    TypeOfStickerEnum,
    TypeOfLabelEnum,
    TypeOfDecalEnum,
    TypeOfImageTransferEnum,
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

# Quick Quote Form constants (authoritative source)
from .quick_quote import (
    QuickQuotePropertyName,
    # Product categories
    ProductCategoryEnum,
    # Format options  
    StickerFormatEnum,
    LabelsFormatEnum,
    DecalsFormatEnum,
    IronOnsFormatEnum,
    TempTattoosFormatEnum,
    # Sticker finish options
    StickerDieCutFinishEnum,
    StickerKissCutFinishEnum,
    StickerPageSingleDesignFinishEnum,
    StickerPageMultipleDesignsFinishEnum,
    StickerRollsFinishEnum,
    StickerTransfersFinishEnum,
    # Labels finish options
    LabelsKissCutFinishEnum,
    LabelsPageSingleDesignFinishEnum,
    LabelsPageMultipleDesignsFinishEnum,
    LabelsRollsFinishEnum,
    LabelsImageTransfersFinishEnum,
    # Decals finish options
    DecalsWallWindowFinishEnum,
    DecalsFloorOutdoorFinishEnum,
    DecalsImageTransfersFinishEnum,
    # Iron-Ons finish options
    IronOnsPageSingleDesignFinishEnum,
    IronOnsPageMultipleDesignsFinishEnum,
    IronOnsTransfersFinishEnum,
    # Temp Tattoos finish options
    TempTattoosKissCutFinishEnum,
    TempTattoosPageSingleDesignFinishEnum,
    TempTattoosPageMultipleDesignsFinishEnum,
    # Specialized products
    ClingsFinishEnum,
    MagnetsFinishEnum,
    ImageTransfersFinishEnum,
    # Pouches options
    PouchesColor,
    PouchesSizeEnum,
    PouchesLabelMaterialEnum,
)

__all__ = [
    # Base
    "BaseEnum",
    "YesNoEnum",
    "LocationEnum", 
    "UseTypeEnum",
    "NumberOfColoursInDesignEnum",
    "PreferredFormatEnum",
    
    # HubSpot
    "HubSpotFieldType",
    "HubSpotPropertyType",
    "HubSpotTicketCategoryEnum",
    "HubSpotTicketPriorityEnum",
    "HubSpotSourceTypeEnum",
    "HubSpotTicketLanguageEnum",
    "HubSpotPropertyName",
    
    # HubSpot Custom Ticket Properties
    "TicketCustomPropertyName",
    "TicketTypeEnum",
    "OwnerAvailabilityEnum",
    
    # Custom Quote Form
    "CustomQuotePropertyName",
    "BusinessCategoryEnum",
    "HowDidYouFindUsEnum",
    "WhatMadeYouComeBackEnum",
    "ContentPreferenceEnum",
    "ProductGroupEnum",
    "TypeOfStickerEnum",
    "TypeOfLabelEnum",
    "TypeOfDecalEnum",
    "TypeOfImageTransferEnum",
    "TypeOfClingEnum",
    "TypeOfMagnetEnum",
    "TypeOfPackagingEnum",
    "TypeOfPatchEnum",
    "TypeOfTapeEnum",
    "TypeOfTattooEnum",
    "TapeSizeEnum",
    
    # Quick Quote Form (authoritative source for product formats and finishes)
    "QuickQuotePropertyName",
    "ProductCategoryEnum",
    # Format options
    "StickerFormatEnum",
    "LabelsFormatEnum", 
    "DecalsFormatEnum",
    "IronOnsFormatEnum",
    "TempTattoosFormatEnum",
    # Sticker finish options
    "StickerDieCutFinishEnum",
    "StickerKissCutFinishEnum",
    "StickerPageSingleDesignFinishEnum",
    "StickerPageMultipleDesignsFinishEnum",
    "StickerRollsFinishEnum",
    "StickerTransfersFinishEnum",
    # Labels finish options
    "LabelsKissCutFinishEnum",
    "LabelsPageSingleDesignFinishEnum",
    "LabelsPageMultipleDesignsFinishEnum",
    "LabelsRollsFinishEnum",
    "LabelsImageTransfersFinishEnum",
    # Decals finish options
    "DecalsWallWindowFinishEnum",
    "DecalsFloorOutdoorFinishEnum", 
    "DecalsImageTransfersFinishEnum",
    # Iron-Ons finish options
    "IronOnsPageSingleDesignFinishEnum",
    "IronOnsPageMultipleDesignsFinishEnum",
    "IronOnsTransfersFinishEnum",
    # Temp Tattoos finish options
    "TempTattoosKissCutFinishEnum",
    "TempTattoosPageSingleDesignFinishEnum",
    "TempTattoosPageMultipleDesignsFinishEnum",
    # Specialized products
    "ClingsFinishEnum",
    "MagnetsFinishEnum",
    "ImageTransfersFinishEnum",
    # Pouches options
    "PouchesColor",  # Note: PouchesPouchColorFinishEnum is now PouchesColor in quick_quote
    "PouchesSizeEnum",
    "PouchesLabelMaterialEnum",
]
