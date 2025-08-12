"""
Custom Quote Constants Package.

This package contains all constants related to the custom quote form,
organized based on actual HubSpot API data.
"""

# Property Names
from .property_names import CustomQuotePropertyName

# Form Value Options
from .form_properties import (
    # Business Information
    BusinessCategoryEnum,
    HowDidYouFindUsEnum,
    WhatMadeYouComeBackEnum,
    ContentPreferenceEnum,
    
    # Basic Form Fields
    LocationEnum,
    UseTypeEnum,
    YesNoEnum,
    
    # Product Specification
    ProductGroupEnum,
    PreferredFormatEnum,
    NumberOfColoursInDesignEnum,
    
    # Product Types
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
    
    # Packaging Specific
    PouchSizeEnum,
    PouchLabelMaterialEnum,
    
    # Tape Specific
    TapeSizeEnum,
)

__all__ = [
    # Property Names
    "CustomQuotePropertyName",
    
    # Business Information
    "BusinessCategoryEnum",
    "HowDidYouFindUsEnum",
    "WhatMadeYouComeBackEnum",
    "ContentPreferenceEnum",
    
    # Basic Form Fields
    "LocationEnum",
    "UseTypeEnum", 
    "YesNoEnum",
    
    # Product Specification
    "ProductGroupEnum",
    "PreferredFormatEnum",
    "NumberOfColoursInDesignEnum",
    
    # Product Types
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
    
    # Packaging Specific
    "PouchSizeEnum",
    "PouchLabelMaterialEnum",
    
    # Tape Specific
    "TapeSizeEnum",
]
