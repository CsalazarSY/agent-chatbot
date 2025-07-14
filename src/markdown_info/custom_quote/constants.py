from enum import Enum
from typing import List


# HubSpot Specific Enums
class HubSpotFieldType(str, Enum):
    SINGLE_LINE_TEXT = "Single-line text"
    PHONE_NUMBER = "Phone number"
    SINGLE_CHECKBOX = "Single checkbox"
    DROPDOWN = "Dropdown"
    NUMBER = "Number"
    MULTI_LINE_TEXT = "Multi-line text"
    FILE = "File"


class HubSpotPropertyType(str, Enum):
    CONTACT_PROPERTY = "Contact Property"
    TICKET_PROPERTY = "Ticket Property"


# Base Enum with get_all_values
class BaseEnum(str, Enum):
    @classmethod
    def get_all_values(cls) -> List[str]:
        return [e.value for e in cls]

# Product Category
class ProductCategoryEnum(BaseEnum):
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

# Stickers
class StickerFormatEnum(BaseEnum):
    PAGE_SINGLE_DESIGN = "Page (Single Design)"
    DIE_CUT = "Die-Cut"
    KISS_CUT = "Kiss-Cut"
    ROLLS = "Rolls"
    PAGE_MULTIPLE_DESIGNS = "Page (Multiple Designs)"
    TRANSFERS = "Transfers"

class StickerPageSingleDesignFinishEnum(BaseEnum):
    WHITE_VINYL_REMOVABLE_MATTE = "White Vinyl Removable Matte"
    CLEAR_VINYL_REMOVABLE_GLOSSY = "Clear Vinyl Removable Glossy"
    WHITE_VINYL_PERMANENT_GLOSSY = "White Vinyl Permanent Glossy"
    WHITE_VINYL_REMOVABLE_GLOSSY = "White Vinyl Removable Glossy"

class StickerDieCutFinishEnum(BaseEnum):
    WHITE_VINYL_REMOVABLE_SEMI_GLOSS = "White Vinyl Removable Semi-Gloss"
    WHITE_VINYL_PERMANENT_SEMI_GLOSS = "White Vinyl Permanent Semi-Gloss"
    CLEAR_VINYL_REMOVABLE_SEMI_GLOSS = "Clear Vinyl Removable Semi-Gloss"
    PERMANENT_HOLOGRAPHIC_PERMANENT_GLOSSY = "Permanent Holographic Permanent Glossy"
    PERMANENT_GLITTER_PERMANENT_GLOSSY = "Permanent Glitter Permanent Glossy"
    ECO_SAFE_PET_REMOVABLE_MATTE = "Eco-Safe PET Removable Matte"
    HANG_TAG_REMOVABLE_SEMI_GLOSS_STICKERS = "Hang Tag Removable Semi-Gloss Stickers"
    GLOW_IN_THE_DARK_PERMANENT_STICKERS = "Glow In The Dark Permanent Stickers"

class StickerKissCutFinishEnum(BaseEnum):
    WHITE_VINYL_REMOVABLE_GLOSSY = "White Vinyl Removable Glossy"
    WHITE_VINYL_REMOVABLE_MATTE = "White Vinyl Removable Matte"
    CLEAR_VINYL_REMOVABLE_GLOSSY = "Clear Vinyl Removable Glossy"

class StickerRollsFinishEnum(BaseEnum):
    WHITE_PAPER_PERMANENT_GLOSSY_LAMINATED = "White Paper Permanent Glossy (Laminated)"
    WHITE_BOPP_PERMANENT_MATTE_WRITEABLE = "White BOPP Permanent Matte (Writeable)"
    WHITE_BOPP_PERMANENT_GLOSSY_LAMINATED = "White BOPP Permanent Glossy (Laminated)"
    CLEAR_BOPP_PERMANENT_GLOSSY = "Clear BOPP Permanent Glossy"
    WHITE_PAPER_PERMANENT_SEMI_GLOSS_ECO_SAFE = "White Paper Permanent Semi-Gloss (Eco-Safe)"
    WHITE_PAPER_REMOVABLE_GLOSSY_LAMINATED = "White Paper Removable Glossy (Laminated)"
    SILVER_FOIL_PERMANENT_METALLIC_SILVER = "Silver Foil Permanent Metallic Silver"
    GOLD_FOIL_PERMANENT_SHINY_GOLD = "Gold Foil Permanent Shiny-Gold"
    COLORED_FOIL_LABELS_PERMANENT_SHINY_COLOR = "Colored Foil Labels Permanent Shiny Color"

class StickerPageMultipleDesignsFinishEnum(BaseEnum):
    WHITE_VINYL_REMOVABLE_MATTE = "White Vinyl Removable Matte"
    WHITE_VINYL_REMOVABLE_GLOSSY = "White Vinyl Removable Glossy"
    WHITE_VINYL_PERMANENT_GLOSSY = "White Vinyl Permanent Glossy"

class StickerTransfersFinishEnum(BaseEnum):
    VINYL_LETTERING_REMOVABLE_GLOSSY = "Vinyl Lettering Removable Glossy"
    VINYL_GRAPHICS = "Vinyl Graphics"
    TRANSFER_STICKER_PERMANENT_GLOSSY = "Transfer Sticker Permanent Glossy"

# Labels
class LabelsFormatEnum(BaseEnum):
    PAGE_SINGLE_DESIGN = "Page (Single Design)"
    KISS_CUT = "Kiss-Cut"
    ROLLS = "Rolls"
    PAGE_MULTIPLE_DESIGNS = "Page (Multiple Designs)"
    IMAGE_TRANSFERS = "Image Transfers"

class LabelsPageSingleDesignFinishEnum(BaseEnum):
    WHITE_VINYL_PERMANENT_GLOSSY = "White Vinyl Permanent Glossy"
    WHITE_VINYL_REMOVABLE_GLOSSY = "White Vinyl Removable Glossy"
    WHITE_VINYL_REMOVABLE_MATTE = "White Vinyl Removable Matte"
    CLEAR_VINYL_REMOVABLE_GLOSSY = "Clear Vinyl Removable Glossy"
    KIDS_LABEL_REMOVABLE_GLOSSY_UV_COATED = "Kids Label Removable Glossy - UV Coated"

class LabelsKissCutFinishEnum(BaseEnum):
    WHITE_VINYL_REMOVABLE_GLOSSY = "White Vinyl Removable Glossy"
    WHITE_VINYL_REMOVABLE_MATTE = "White Vinyl Removable Matte"
    CLEAR_VINYL_REMOVABLE_GLOSSY = "Clear Vinyl Removable Glossy"

class LabelsRollsFinishEnum(BaseEnum):
    WHITE_PAPER_PERMANENT_GLOSSY_LAMINATED = "White Paper Permanent Glossy (Laminated)"
    WHITE_BOPP_PERMANENT_MATTE_WRITEABLE = "White BOPP Permanent Matte (Writeable)"
    WHITE_BOPP_PERMANENT_GLOSSY_LAMINATED = "White BOPP Permanent Glossy (Laminated)"
    CLEAR_BOPP_PERMANENT_GLOSSY = "Clear BOPP Permanent Glossy"
    WHITE_PAPER_PERMANENT_SEMI_GLOSS_ECO_SAFE = "White Paper Permanent Semi-Gloss (Eco-Safe)"
    WHITE_PAPER_REMOVABLE_GLOSSY_LAMINATED = "White Paper Removable Glossy (Laminated)"
    SILVER_FOIL_PERMANENT_METALLIC_SILVER = "Silver Foil Permanent Metallic Silver"
    GOLD_FOIL_PERMANENT_SHINY_GOLD = "Gold Foil Permanent Shiny-Gold"
    COLORED_FOIL_LABELS_PERMANENT_SHINY_COLOR = "Colored Foil Labels Permanent Shiny Color"

class LabelsPageMultipleDesignsFinishEnum(BaseEnum):
    WHITE_VINYL_PERMANENT_GLOSSY = "White Vinyl Permanent Glossy"
    WHITE_VINYL_REMOVABLE_GLOSSY = "White Vinyl Removable Glossy"
    WHITE_VINYL_REMOVABLE_MATTE = "White Vinyl Removable Matte"
    KIDS_LABEL_REMOVABLE_GLOSSY_UV_COATED = "Kids Label Removable Glossy - UV Coated"

class LabelsImageTransfersFinishEnum(BaseEnum):
    TRANSFER_LABEL_PERMANENT_GLOSSY = "Transfer Label Permanent Glossy"

# Image Transfers
class ImageTransfersFinishEnum(BaseEnum):
    PERMANENT_GLOSSY_IMAGE_TRANSFER_STICKER = "Permanent Glossy Image Transfer Sticker"
    IMAGE_TRANSFER_IRON_ONS_DTF = "Image Transfer Iron-Ons (DTF)"

# Decals
class DecalsFormatEnum(BaseEnum):
    WALL_WINDOW = "Wall & Window"
    FLOOR_OUTDOOR = "Floor & Outdoor"
    IMAGE_TRANSFERS = "Image Transfers"

class DecalsWallWindowFinishEnum(BaseEnum):
    WHITE_VINYL_REMOVABLE_MATTE = "White Vinyl Removable Matte"
    CLEAR_VINYL_REMOVABLE_GLOSSY = "Clear Vinyl Removable Glossy"
    VINYL_LETTERING_REMOVABLE_GLOSSY = "Vinyl Lettering Removable Glossy"
    VINYL_GRAPHICS = "Vinyl Graphics"
    DRY_ERASE = "Dry Erase"

class DecalsFloorOutdoorFinishEnum(BaseEnum):
    WHITE_VINYL_SMOOTH_SURFACE_REMOVABLE_GLOSSY = "White Vinyl - Smooth Surface Removable Glossy"
    WHITE_VINYL_ROUGH_ROUGH_SURFACE = "White Vinyl Rough - Rough Surface"

class DecalsImageTransfersFinishEnum(BaseEnum):
    TRANSFER_DECAL_PERMANENT_GLOSSY = "Transfer Decal Permanent Glossy"

# Temp Tattoos
class TempTattoosFormatEnum(BaseEnum):
    PAGE_SINGLE_DESIGN = "Page (Single Design)"
    KISS_CUT = "Kiss-Cut"
    PAGE_MULTIPLE_DESIGNS = "Page (Multiple Designs)"

class TempTattoosPageSingleDesignFinishEnum(BaseEnum):
    REMOVABLE_CLEAR_MATTE = "Removable Clear Matte"

class TempTattoosKissCutFinishEnum(BaseEnum):
    REMOVABLE_CLEAR_MATTE = "Removable Clear Matte"

class TempTattoosPageMultipleDesignsFinishEnum(BaseEnum):
    REMOVABLE_CLEAR_MATTE = "Removable Clear Matte"

# Iron-Ons
class IronOnsFormatEnum(BaseEnum):
    PAGE_SINGLE_DESIGN = "Page (Single Design)"
    PAGE_MULTIPLE_DESIGNS = "Page (Multiple Designs)"
    TRANSFERS = "Transfers"

class IronOnsPageSingleDesignFinishEnum(BaseEnum):
    IRON_ONS_SINGLES = "Iron-Ons Singles"

class IronOnsPageMultipleDesignsFinishEnum(BaseEnum):
    IRON_ONS_MULTIPLE = "Iron-Ons Multiple"

class IronOnsTransfersFinishEnum(BaseEnum):
    IMAGE_TRANSFER_IRON_ONS_DTF = "Image Transfer Iron-Ons (DTF)"
    IRON_ON_LETTERING_TRANSFERS = "Iron-On Lettering Transfers"

# Magnets
class MagnetsFinishEnum(BaseEnum):
    DIE_CUT_FRIDGE_MAGNETS = "Die-Cut Fridge Magnets"
    DIE_CUT_CAR_MAGNETS = "Die-Cut Car Magnets"

# Clings
class ClingsFinishEnum(BaseEnum):
    CLEAR_STATIC_REMOVABLE_GLOSSY = "Clear Static Removable Glossy"
    WHITE_STATIC_REMOVABLE_GLOSSY = "White Static Removable Glossy"

# Pouches
class PouchesPouchColorFinishEnum(BaseEnum):
    CLEAR_WITH_SILVER_BACK = "Clear with Silver Back"
    GLOSSY_WHITE = "Glossy White"
    KRAFT_PAPER = "Kraft Paper"
    MATTE_BLACK = "Matte Black"

class PouchesPouchSizeFinishEnum(BaseEnum):
    S_3x5_FLAT_HANGHOLE = '3" x 5" (Flat with Hanghole)'
    M_5x7x3_STANDUP = '5"x 7" x 3" (Stand-Up)'
    L_6x9x3_5_STANDUP = '6" x 9" x 3.5" (Stand-Up)'

class PouchesLabelMaterialFinishEnum(BaseEnum):
    WHITE_PAPER = "White Paper"
    WHITE_BOPP = "White BOPP"
    SILVER_FOIL = "Silver Foil"
    GOLD_FOIL = "Gold Foil"


class HubSpotPropertyName(str, Enum):
    PRODUCT_CATEGORY = "product_category"
    STICKER_FORMAT = "sticker_format"
    STICKER_PAGE_SINGLE_DESIGN_FINISH = "sticker_page_single_design_finish"
    STICKER_DIE_CUT_FINISH = "sticker_die_cut_finish"
    STICKER_KISS_CUT_FINISH = "sticker_kiss_cut_finish"
    STICKER_ROLLS_FINISH = "sticker_rolls_finish"
    STICKER_PAGE_MULTIPLE_DESIGNS_FINISH = "sticker_page_multiple_designs_finish"
    STICKER_TRANSFERS_FINISH = "sticker_transfers_finish"
    LABELS_FORMAT = "labels_format"
    LABELS_PAGE_SINGLE_DESIGN_FINISH = "labels_page_single_design_finish"
    LABELS_KISS_CUT_FINISH = "labels_kiss_cut_finish"
    LABELS_ROLLS_FINISH = "labels_rolls_finish"
    LABELS_PAGE_MULTIPLE_DESIGNS_FINISH = "labels_page_multiple_designs_finish"
    LABELS_IMAGE_TRANSFERS_FINISH = "labels_image_transfers_finish"
    IMAGE_TRANSFERS_FINISH = "image_transfers_finish"
    DECALS_FORMAT = "decals_format"
    DECALS_WALL_WINDOW_FINISH = "decals_wall_window_finish"
    DECALS_FLOOR_OUTDOOR_FINISH = "decals_floor_outdoor_finish"
    DECALS_IMAGE_TRANSFERS_FINISH = "decals_image_transfers_finish"
    TEMP_TATTOOS_FORMAT = "temp_tattoos_format"
    TEMP_TATTOOS_PAGE_SINGLE_DESIGN_FINISH = "temp_tattoos_page_single_design_finish"
    TEMP_TATTOOS_KISS_CUT_FINISH = "temp_tattoos_kiss_cut_finish"
    TEMP_TATTOOS_PAGE_MULTIPLE_DESIGNS_FINISH = "temp_tattoos_page_multiple_designs_finish"
    IRON_ONS_FORMAT = "iron_ons_format"
    IRON_ONS_PAGE_SINGLE_DESIGN_FINISH = "iron_ons_page_single_design_finish"
    IRON_ONS_PAGE_MULTIPLE_DESIGNS_FINISH = "iron_ons_page_multiple_designs_finish"
    IRON_ONS_TRANSFERS_FINISH = "iron_ons_transfers_finish"
    MAGNETS_FINISH = "magnets_finish"
    CLINGS_FINISH = "clings_finish"
    POUCHES_POUCH_COLOR_FINISH = "pouches_pouch_color_finish"
    POUCHES_POUCH_SIZE_FINISH = "pouches_pouch_size_finish"
    POUCHES_LABEL_MATERIAL_FINISH = "pouches_label_material_finish"
    TOTAL_QUANTITY = "total_quantity_"
    WIDTH_IN_INCHES = "width_in_inches_"
    HEIGHT_IN_INCHES = "height_in_inches_"
    EMAIL = "email"
    PHONE = "phone"
    PROMOTIONAL_PRODUCT_DISTRIBUTOR = "promotional_product_distributor_"
    FIRSTNAME = "firstname"
    LASTNAME = "lastname"
    UPLOAD_YOUR_DESIGN = "upload_your_design"
    ADDITIONAL_INSTRUCTIONS = "additional_instructions_"
    SUBJECT = "subject"
    CONTENT = "content"
    TYPE_OF_TICKET = "type_of_ticket"
