"""
Quick Quote Form Properties - Based on HubSpot API JSON data.

This file contains all the constants for the quick quote form properties
as they appear in HubSpot. This is the authoritative source for all
quick quote related enums.

Group: "quote_information_-_quick_quote_-_changed_values"

Note: This module contains the canonical definitions for product format
and finish options that were previously scattered across multiple files.
"""

from ..base import BaseEnum


# =============================================================================
# PRODUCT CATEGORIES
# =============================================================================

class ProductCategoryEnum(BaseEnum):
    """Product category options for quick quote form."""
    STICKERS = "Stickers"
    LABELS = "Labels"
    IMAGE_TRANSFERS = "Image Transfers"
    DECALS = "Decals"
    TEMP_TATTOOS = "Temp Tattoos"
    IRON_ONS = "Iron-Ons"
    MAGNETS = "Magnets"
    PATCHES = "Patches"
    CLINGS = "Clings"
    BADGES = "Badges"
    POUCHES = "Pouches"


# =============================================================================
# STICKER FORMAT AND FINISHES
# =============================================================================

class StickerFormatEnum(BaseEnum):
    """Sticker format options for quick quote."""
    PAGE_SINGLE_DESIGN = "Page (Single Design)"
    DIE_CUT = "Die-Cut"
    KISS_CUT = "Kiss-Cut"
    ROLLS = "Rolls"
    PAGE_MULTIPLE_DESIGNS = "Page (Multiple Designs)"
    TRANSFERS = "Transfers"


class StickerDieCutFinishEnum(BaseEnum):
    """Sticker die-cut finish options for quick quote."""
    WHITE_VINYL_REMOVABLE_SEMI_GLOSS = "White Vinyl Removable Semi-Gloss"
    WHITE_VINYL_PERMANENT_SEMI_GLOSS = "White Vinyl Permanent Semi-Gloss"
    CLEAR_VINYL_REMOVABLE_SEMI_GLOSS = "Clear Vinyl Removable Semi-Gloss"
    PERMANENT_HOLOGRAPHIC_PERMANENT_GLOSSY = "Permanent Holographic Permanent Glossy"
    PERMANENT_GLITTER_PERMANENT_GLOSSY = "Permanent Glitter Permanent Glossy"
    ECO_SAFE_PET_REMOVABLE_MATTE = "Eco-Safe PET Removable Matte"
    HANG_TAG_REMOVABLE_SEMI_GLOSS_STICKERS = "Hang Tag Removable Semi-Gloss Stickers"
    GLOW_IN_THE_DARK_PERMANENT_STICKERS = "Glow In The Dark Permanent Stickers"


class StickerKissCutFinishEnum(BaseEnum):
    """Sticker kiss-cut finish options for quick quote."""
    WHITE_VINYL_REMOVABLE_GLOSSY = "White Vinyl Removable Glossy"
    WHITE_VINYL_REMOVABLE_MATTE = "White Vinyl Removable Matte"
    CLEAR_VINYL_REMOVABLE_GLOSSY = "Clear Vinyl Removable Glossy"


class StickerPageSingleDesignFinishEnum(BaseEnum):
    """Sticker page single design finish options for quick quote."""
    WHITE_VINYL_REMOVABLE_MATTE = "White Vinyl Removable Matte"
    CLEAR_VINYL_REMOVABLE_GLOSSY = "Clear Vinyl Removable Glossy"
    WHITE_VINYL_PERMANENT_GLOSSY = "White Vinyl Permanent Glossy"
    WHITE_VINYL_REMOVABLE_GLOSSY = "White Vinyl Removable Glossy"


class StickerPageMultipleDesignsFinishEnum(BaseEnum):
    """Sticker page multiple designs finish options for quick quote."""
    WHITE_VINYL_REMOVABLE_MATTE = "White Vinyl Removable Matte"
    WHITE_VINYL_REMOVABLE_GLOSSY = "White Vinyl Removable Glossy"
    WHITE_VINYL_PERMANENT_GLOSSY = "White Vinyl Permanent Glossy"


class StickerRollsFinishEnum(BaseEnum):
    """Sticker rolls finish options for quick quote."""
    WHITE_PAPER_PERMANENT_GLOSSY_LAMINATED = "White Paper Permanent Glossy (Laminated)"
    WHITE_BOPP_PERMANENT_MATTE_WRITEABLE = "White BOPP Permanent Matte (Writeable)"
    WHITE_BOPP_PERMANENT_GLOSSY_LAMINATED = "White BOPP Permanent Glossy (Laminated)"
    CLEAR_BOPP_PERMANENT_GLOSSY = "Clear BOPP Permanent Glossy"
    WHITE_PAPER_PERMANENT_SEMI_GLOSS_ECO_SAFE = "White Paper Permanent Semi-Gloss (Eco-Safe)"
    WHITE_PAPER_REMOVABLE_GLOSSY_LAMINATED = "White Paper Removable Glossy (Laminated)"
    SILVER_FOIL_PERMANENT_METALLIC_SILVER = "Silver Foil Permanent Metallic Silver"
    GOLD_FOIL_PERMANENT_SHINY_GOLD = "Gold Foil Permanent Shiny-Gold"
    COLORED_FOIL_LABELS_PERMANENT_SHINY_COLOR = "Colored Foil Labels Permanent Shiny Color"


class StickerTransfersFinishEnum(BaseEnum):
    """Sticker transfers finish options for quick quote."""
    VINYL_LETTERING_REMOVABLE_GLOSSY = "Vinyl Lettering Removable Glossy"
    VINYL_GRAPHICS = "Vinyl Graphics"
    TRANSFER_STICKER_PERMANENT_GLOSSY = "Transfer Sticker Permanent Glossy"


# =============================================================================
# LABELS FORMAT AND FINISHES
# =============================================================================

class LabelsFormatEnum(BaseEnum):
    """Labels format options for quick quote."""
    PAGE_SINGLE_DESIGN = "Page (Single Design)"
    KISS_CUT = "Kiss-Cut"
    ROLLS = "Rolls"
    PAGE_MULTIPLE_DESIGNS = "Page (Multiple Designs)"
    IMAGE_TRANSFERS = "Image Transfers"


class LabelsKissCutFinishEnum(BaseEnum):
    """Labels kiss-cut finish options for quick quote."""
    WHITE_VINYL_REMOVABLE_GLOSSY = "White Vinyl Removable Glossy"
    WHITE_VINYL_REMOVABLE_MATTE = "White Vinyl Removable Matte"
    CLEAR_VINYL_REMOVABLE_GLOSSY = "Clear Vinyl Removable Glossy"


class LabelsPageSingleDesignFinishEnum(BaseEnum):
    """Labels page single design finish options for quick quote."""
    WHITE_VINYL_PERMANENT_GLOSSY = "White Vinyl Permanent Glossy"
    WHITE_VINYL_REMOVABLE_GLOSSY = "White Vinyl Removable Glossy"
    WHITE_VINYL_REMOVABLE_MATTE = "White Vinyl Removable Matte"
    CLEAR_VINYL_REMOVABLE_GLOSSY = "Clear Vinyl Removable Glossy"
    KIDS_LABEL_REMOVABLE_GLOSSY_UV_COATED = "Kids Label Removable Glossy - UV Coated"


class LabelsPageMultipleDesignsFinishEnum(BaseEnum):
    """Labels page multiple designs finish options for quick quote."""
    WHITE_VINYL_PERMANENT_GLOSSY = "White Vinyl Permanent Glossy"
    WHITE_VINYL_REMOVABLE_GLOSSY = "White Vinyl Removable Glossy"
    WHITE_VINYL_REMOVABLE_MATTE = "White Vinyl Removable Matte"
    KIDS_LABEL_REMOVABLE_GLOSSY_UV_COATED = "Kids Label Removable Glossy - UV Coated"


class LabelsRollsFinishEnum(BaseEnum):
    """Labels rolls finish options for quick quote."""
    WHITE_PAPER_PERMANENT_GLOSSY_LAMINATED = "White Paper Permanent Glossy (Laminated)"
    WHITE_BOPP_PERMANENT_MATTE_WRITEABLE = "White BOPP Permanent Matte (Writeable)"
    WHITE_BOPP_PERMANENT_GLOSSY_LAMINATED = "White BOPP Permanent Glossy (Laminated)"
    CLEAR_BOPP_PERMANENT_GLOSSY = "Clear BOPP Permanent Glossy"
    WHITE_PAPER_PERMANENT_SEMI_GLOSS_ECO_SAFE = "White Paper Permanent Semi-Gloss (Eco-Safe)"
    WHITE_PAPER_REMOVABLE_GLOSSY_LAMINATED = "White Paper Removable Glossy (Laminated)"
    SILVER_FOIL_PERMANENT_METALLIC_SILVER = "Silver Foil Permanent Metallic Silver"
    GOLD_FOIL_PERMANENT_SHINY_GOLD = "Gold Foil Permanent Shiny-Gold"
    COLORED_FOIL_LABELS_PERMANENT_SHINY_COLOR = "Colored Foil Labels Permanent Shiny Color"


class LabelsImageTransfersFinishEnum(BaseEnum):
    """Labels image transfers finish options for quick quote."""
    TRANSFER_LABEL_PERMANENT_GLOSSY = "Transfer Label Permanent Glossy"


# =============================================================================
# DECALS FORMAT AND FINISHES
# =============================================================================

class DecalsFormatEnum(BaseEnum):
    """Decals format options for quick quote."""
    WALL_WINDOW = "Wall & Window"
    FLOOR_OUTDOOR = "Floor & Outdoor"
    IMAGE_TRANSFERS = "Image Transfers"


class DecalsWallWindowFinishEnum(BaseEnum):
    """Decals wall & window finish options for quick quote."""
    WHITE_VINYL_REMOVABLE_MATTE = "White Vinyl Removable Matte"
    CLEAR_VINYL_REMOVABLE_GLOSSY = "Clear Vinyl Removable Glossy"
    VINYL_LETTERING_REMOVABLE_GLOSSY = "Vinyl Lettering Removable Glossy"
    VINYL_GRAPHICS = "Vinyl Graphics"
    DRY_ERASE = "Dry Erase"


class DecalsFloorOutdoorFinishEnum(BaseEnum):
    """Decals floor & outdoor finish options for quick quote."""
    WHITE_VINYL_SMOOTH_SURFACE_REMOVABLE_GLOSSY = "White Vinyl - Smooth Surface Removable Glossy"
    WHITE_VINYL_ROUGH_ROUGH_SURFACE = "White Vinyl Rough - Rough Surface"


class DecalsImageTransfersFinishEnum(BaseEnum):
    """Decals image transfers finish options for quick quote."""
    TRANSFER_DECAL_PERMANENT_GLOSSY = "Transfer Decal Permanent Glossy"


# =============================================================================
# IRON-ONS FORMAT AND FINISHES
# =============================================================================

class IronOnsFormatEnum(BaseEnum):
    """Iron-Ons format options for quick quote."""
    PAGE_SINGLE_DESIGN = "Page (Single Design)"
    PAGE_MULTIPLE_DESIGNS = "Page (Multiple Designs)"
    TRANSFERS = "Transfers"


class IronOnsPageSingleDesignFinishEnum(BaseEnum):
    """Iron-Ons page single design finish options for quick quote."""
    IRON_ONS_SINGLES = "Iron-Ons Singles"


class IronOnsPageMultipleDesignsFinishEnum(BaseEnum):
    """Iron-Ons page multiple designs finish options for quick quote."""
    IRON_ONS_MULTIPLE = "Iron-Ons Multiple"


class IronOnsTransfersFinishEnum(BaseEnum):
    """Iron-Ons transfers finish options for quick quote."""
    IMAGE_TRANSFER_IRON_ONS_DTF = "Image Transfer Iron-Ons (DTF)"
    IRON_ON_LETTERING_TRANSFERS = "Iron-On Lettering Transfers"


# =============================================================================
# TEMP TATTOOS FORMAT AND FINISHES
# =============================================================================

class TempTattoosFormatEnum(BaseEnum):
    """Temp Tattoos format options for quick quote."""
    PAGE_SINGLE_DESIGN = "Page (Single Design)"
    KISS_CUT = "Kiss-Cut"
    PAGE_MULTIPLE_DESIGNS = "Page (Multiple Designs)"


class TempTattoosKissCutFinishEnum(BaseEnum):
    """Temp Tattoos kiss-cut finish options for quick quote."""
    REMOVABLE_CLEAR_MATTE = "Removable Clear Matte"


class TempTattoosPageSingleDesignFinishEnum(BaseEnum):
    """Temp Tattoos page single design finish options for quick quote."""
    REMOVABLE_CLEAR_MATTE = "Removable Clear Matte"


class TempTattoosPageMultipleDesignsFinishEnum(BaseEnum):
    """Temp Tattoos page multiple designs finish options for quick quote."""
    REMOVABLE_CLEAR_MATTE = "Removable Clear Matte"


# =============================================================================
# SPECIALIZED PRODUCT FINISHES
# =============================================================================

class ClingsFinishEnum(BaseEnum):
    """Clings finish options for quick quote."""
    CLEAR_STATIC_REMOVABLE_GLOSSY = "Clear Static Removable Glossy"
    WHITE_STATIC_REMOVABLE_GLOSSY = "White Static Removable Glossy"


class MagnetsFinishEnum(BaseEnum):
    """Magnets finish options for quick quote."""
    DIE_CUT_FRIDGE_MAGNETS = "Die-Cut Fridge Magnets"
    DIE_CUT_CAR_MAGNETS = "Die-Cut Car Magnets"


class ImageTransfersFinishEnum(BaseEnum):
    """Image Transfers finish options for quick quote."""
    PERMANENT_GLOSSY_IMAGE_TRANSFER_STICKER = "Permanent Glossy Image Transfer Sticker"
    IMAGE_TRANSFER_IRON_ONS_DTF = "Image Transfer Iron-Ons (DTF)"


# =============================================================================
# POUCHES OPTIONS
# =============================================================================

class PouchesColor(BaseEnum):
    """Pouches color options for quick quote."""
    CLEAR_WITH_SILVER_BACK = "Clear with Silver Back"
    GLOSSY_WHITE = "Glossy White"
    KRAFT_PAPER = "Kraft Paper"
    MATTE_BLACK = "Matte Black"


class PouchesSizeEnum(BaseEnum):
    """Pouches size options for quick quote."""
    THREE_X_FIVE_FLAT_WITH_HANGHOLE = "3\" x 5\" (Flat with Hanghole)"
    FIVE_X_SEVEN_X_THREE_STAND_UP = "5\" x 7\" x 3\" (Stand-Up)"
    SIX_X_NINE_X_THREE_FIVE_STAND_UP = "6\" x 9\" x 3.5\" (Stand-Up)"


class PouchesLabelMaterialEnum(BaseEnum):
    """Pouches label material options for quick quote."""
    WHITE_PAPER = "White Paper"
    WHITE_BOPP = "White BOPP"
    SILVER_FOIL = "Silver Foil"
    GOLD_FOIL = "Gold Foil"
