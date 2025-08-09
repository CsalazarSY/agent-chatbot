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

# Business Category
class BusinessCategoryEnum(BaseEnum):
    AMATEUR_SPORT = "Amateur Sport"
    ASSOCIATIONS = "Associations"
    AUTO_SERVICES = "Auto Services"
    BEVERAGE_PRODUCER = "Beverage Producer"
    CHARITY_OR_NON_PROFIT_ASSOCIATION = "Charity or Non-Profit Association"
    CHILDCARE = "Childcare"
    CLOTHING_COMPANY = "Clothing Company"
    CONTRACTOR_OR_INDUSTRIAL = "Contractor or Industrial"
    ENTERTAINMENT = "Entertainment"
    FOOD_MANUFACTURING_OR_FOOD_STORE = "Food Manufacturing or Food Store"
    GOVERNMENT = "Government"
    GRAPHIC_DESIGNER = "Graphic Designer"
    HEALTH_AND_FITNESS = "Health & Fitness"
    HEALTH_AND_BEAUTY_AIDS = "Health and Beauty Aids"
    HOTEL_AND_TRAVEL_PLANNER = "Hotel and Travel Planner"
    MARIJUANA_INDUSTRY = "Marijuana Industry"
    MARKETING_AGENCY = "Marketing Agency"
    MEDICAL = "Medical"
    PPAI_ASI_PROMOTIONAL = "PPAI/ASI Promotional"
    PRINTING_COMPANY = "Printing Company"
    PROFESSIONAL_EVENT_PLANNER = "Professional Event Planner"
    PROFESSIONAL_SERVICES = "Professional Services"
    RESTAURANTS_AND_BARS = "Resturants and Bars"
    SCHOOLS = "Schools"
    TECHNOLOGY_COMPANY = "Technology Company"
    OTHER_RETAIL_NON_FOOD_STORE = "Other Retail (Non Food Store)"
    OTHER = "Other"

# How did you find us
class HowDidYouFindUsEnum(BaseEnum):
    GOOGLE_SEARCH = "Google Search"
    SOCIAL_MEDIA = "Social Media"
    EMAIL = "Email"
    PPAI_ASI = "PPAI/ASI"
    TRADESHOW = "Tradeshow"
    STICKERYOU_STORE = "StickerYou Store"
    EXISTING_CUSTOMER = "Existing customer"
    BANNER_ADS = "Banner Ads"
    REFERRAL_FROM_ANOTHER_CUSTOMER = "Referral from Another Customer"
    CATALOG = "Catalog"
    LIVE_CHAT = "Live Chat"
    GENERAL_INQUIRY_FORM = "General Inquiry Form"

# Number of colours in design
class NumberOfColoursInDesignEnum(BaseEnum):
    ONE = "1"
    TWO = "2"
    THREE = "3"

# Preferred Format
class PreferredFormatEnum(BaseEnum):
    PAGES = "Pages"
    KISS_CUT_SINGLES = "Kiss-Cut Singles"
    DIE_CUT_SINGLES = "Die-Cut Singles"

# Product Group
class ProductGroupEnum(BaseEnum):
    BADGE = "Badge"
    CLING = "Cling"
    DECAL = "Decal"
    IRON_ON = "Iron-On"
    MAGNET = "Magnet"
    PACKAGING = "Packaging"
    PATCH = "Patch"
    ROLL_LABEL = "Roll Label"
    SERVICES = "Services"
    SIGNAGE = "Signage"
    STICKERS = "Stickers"
    STICKER = "Sticker"  # Note: JSON has both "Stickers" and "Sticker"
    TAPE = "Tape"
    TATTOO = "Tattoo"
    NONE_PRODUCT_REQUEST = "None Product Request"

# HubSpot Ticket Category
class HubSpotTicketCategoryEnum(BaseEnum):
    PRODUCT_ISSUE = "PRODUCT_ISSUE"
    BILLING_ISSUE = "BILLING_ISSUE"
    FEATURE_REQUEST = "FEATURE_REQUEST"
    GENERAL_INQUIRY = "GENERAL_INQUIRY"

# HubSpot Ticket Priority
class HubSpotTicketPriorityEnum(BaseEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"

# HubSpot Source Type
class HubSpotSourceTypeEnum(BaseEnum):
    CHAT = "CHAT"
    EMAIL = "EMAIL"
    FORM = "FORM"
    PHONE = "PHONE"

# HubSpot Ticket Language (AI Tag) - simplified version with most common languages
class HubSpotTicketLanguageEnum(BaseEnum):
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    DUTCH = "nl"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"
    RUSSIAN = "ru"
    ARABIC = "ar"
    HINDI = "hi"
    # Add more as needed

# Location
class LocationEnum(BaseEnum):
    USA = "USA"
    CANADA = "Canada"
    OUTSIDE_NORTH_AMERICA = "Outside North America"

# Type of Cling
class TypeOfClingEnum(BaseEnum):
    CLEAR_STATIC_CLING = "Clear Static Cling"
    WHITE_STATIC_CLING = "White Static Cling"

# Type of Decal
class TypeOfDecalEnum(BaseEnum):
    INDOOR_FLOOR_VINYL = "Indoor Floor Vinyl"
    INDOOR_WALL_VINYL = "Indoor Wall Vinyl"
    CLEAR_WINDOW = "Clear Window"
    OUTDOOR_STREET_VINYL = "Outdoor/Street Vinyl"
    STATIC_CLING = "Static Cling"
    DRY_ERASE_VINYL = "Dry Erase Vinyl"
    FROSTED_VINYL_WINDOW_GRAPHIC = "Frosted Vinyl Window Graphic"
    VINYL_GRAPHIC = "Vinyl Graphic"
    UV_DTF_IMAGE_TRANSFER_STICKER = "UV DTF Image Transfer Sticker"

# Type of Image Transfer
class TypeOfImageTransferEnum(BaseEnum):
    GOLD_FOIL_UV_DTF_IMAGE_TRANSFERS = "Gold Foil UV DTF Image Transfers"
    UV_DTF_IMAGE_TRANSFERS = "UV DTF Image Transfers"

# Type of Label
class TypeOfLabelEnum(BaseEnum):
    CLEAR_BOPP = "Clear BOPP"
    WHITE_BOPP = "White BOPP"
    EMBOSSED = "Embossed"
    KRAFT_PAPER = "Kraft Paper"
    WHITE_PERMANENT_PAPER = "White Permanent Paper"
    GOLD_FOIL = "Gold Foil"
    SILVER_FOIL = "Silver Foil"
    COLOURED_FOIL = "Coloured Foil"
    WRITABLE_MATTE_BOPP = "Writable Matte BOPP"
    VARIABLE_DATA_CUSTOM_BARCODE_LABELS = "Variable Data - Custom Barcode Labels"
    VARIABLE_DATA_CUSTOM_QR_CODE_LABELS = "Variable Data - Custom QR Code Labels"
    VARIABLE_DATA_CUSTOM_SERIAL_NUMBER_LABELS = "Variable Data - Custom Serial Number Labels"
    VARIABLE_DATA_CUSTOM_ASSET_TAG_LABELS = "Variable Data - Custom Asset Tag Labels"
    VARIABLE_DATA_CUSTOM_SEQUENTIAL_NUMBER_LABELS = "Variable Data - Custom Sequential Number Labels"
    UV_DTF_IMAGE_TRANSFER_LABEL = "UV DTF Image Transfer Label"

# Type of Magnet
class TypeOfMagnetEnum(BaseEnum):
    FRIDGE_MAGNET = "Fridge Magnet"
    CAR_MAGNET = "Car Magnet"

# Type of Packaging
class TypeOfPackagingEnum(BaseEnum):
    MATTE_BLACK_POUCH = "Matte Black Pouch"
    KRAFT_PAPER_POUCH = "Kraft Paper Pouch"
    CLEAR_POUCH_WITH_SILVER_BACK = "Clear Pouch with Silver Back"
    GLOSSY_WHITE_POUCH = "Glossy White Pouch"

# Type of Patch
class TypeOfPatchEnum(BaseEnum):
    PRINTED_PATCH = "Printed Patch"
    EMBROIDERED_PATCH = "Embroidered Patch"

# Type of Sticker
class TypeOfStickerEnum(BaseEnum):
    HOLOGRAPHIC = "Holographic"
    GLITTER = "Glitter"
    CLEAR_VINYL = "Clear Vinyl"
    REMOVABLE_WHITE_VINYL = "Removable White Vinyl"
    PERMANENT_WHITE_VINYL = "Permanent White Vinyl"
    MATTE_WHITE_VINYL = "Matte White Vinyl"
    ECO_SAFE = "Eco-Safe"
    HANG_TAG = "Hang Tag"
    REMOVABLE_SMART_SAVE = "Removable Smart Save"
    PERMANENT_GLOW_IN_THE_DARK_DIE_CUT_SINGLES = "Permanent Glow in the Dark Die Cut Singles"
    SCRATCH_AND_SNIFF = "Scratch & Sniff"
    MINI_PAGES = "Mini Pages"
    UV_DTF_IMAGE_TRANSFER_STICKER = "UV DTF Image Transfer Sticker"

# Type of Tape
class TypeOfTapeEnum(BaseEnum):
    CUSTOM_WHITE_TAPE = "Custom White Tape"
    CUSTOM_CLEAR_TAPE = "Custom Clear Tape"
    BLANK_WHITE_TAPE = "Blank White Tape"
    BLANK_CLEAR_TAPE = "Blank Clear Tape"

# Type of Tattoo
class TypeOfTattooEnum(BaseEnum):
    GLITTER_TATTOO = "Glitter Tattoo"
    GLOW_IN_THE_DARK_TATTOO = "Glow in the Dark Tattoo"
    METALLIC_FOIL_TATTOO = "Metallic Foil Tattoo"
    STANDARD_TATTOO = "Standard Tattoo"
    WHITE_INK_TATTOO = "White Ink Tattoo"

# Use Type
class UseTypeEnum(BaseEnum):
    PERSONAL = "Personal"
    BUSINESS = "Business"

# What kind of content would you like to hear about
class ContentPreferenceEnum(BaseEnum):
    BUSINESS_PRODUCTS_AND_NEWS = "Business Products and News"
    CONSUMER_PRODUCTS_AND_NEWS = "Consumer Products and News"
    PRODUCTS_AND_SWEET_DEALS_FOR_PARENTS = "Products and Sweet Deals for Parents"
    NOT_SURE_YET_SEND_ME_EVERYTHING = "Not sure yet - send me everything!"

# What made you come back to Sticker You
class WhatMadeYouComeBackEnum(BaseEnum):
    STICKERYOU_IS_MY_GO_TO = "StickerYou is my go to"
    GOOGLE_SEARCH = "Google Search"
    SOCIAL_MEDIA = "Social Media"
    EMAIL = "Email"
    PPAI_ASI = "PPAI/ASI"
    TRADESHOW = "Tradeshow"
    STICKERYOU_STORE = "StickerYou Store"
    EXISTING_CUSTOMER = "Existing customer"
    BANNER_ADS = "Banner Ads"
    REFERRAL_FROM_ANOTHER_CUSTOMER = "Referral from Another Customer"
    CATALOG = "Catalog"
    LIVE_CHAT = "Live Chat"
    GENERAL_INQUIRY_FORM = "General Inquiry Form"

# What size of tape
class TapeSizeEnum(BaseEnum):
    TWO_INCH_55_YARDS = "2\" x 55 yards"
    TWO_INCH_110_YARDS = "2\" x 110 yards"
    THREE_INCH_55_YARDS = "3\" x 55 yards"

# Yes/No Enum for various boolean-like fields
class YesNoEnum(BaseEnum):
    YES = "yes"
    NO = "no"


class HubSpotPropertyName(str, Enum):
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
    
    # Base Ticket Information
    TYPE_OF_TICKET = "type_of_ticket"
    
    # Product Category and Formats
    PRODUCT_CATEGORY = "product_category"
    
    # Stickers
    STICKER_FORMAT = "sticker_format"
    STICKER_PAGE_SINGLE_DESIGN_FINISH = "sticker_page_single_design_finish"
    STICKER_DIE_CUT_FINISH = "sticker_die_cut_finish"
    STICKER_KISS_CUT_FINISH = "sticker_kiss_cut_finish"
    STICKER_ROLLS_FINISH = "sticker_rolls_finish"
    STICKER_PAGE_MULTIPLE_DESIGNS_FINISH = "sticker_page_multiple_designs_finish"
    STICKER_TRANSFERS_FINISH = "sticker_transfers_finish"
    
    # Labels
    LABELS_FORMAT = "labels_format"
    LABELS_PAGE_SINGLE_DESIGN_FINISH = "labels_page_single_design_finish"
    LABELS_KISS_CUT_FINISH = "labels_kiss_cut_finish"
    LABELS_ROLLS_FINISH = "labels_rolls_finish"
    LABELS_PAGE_MULTIPLE_DESIGNS_FINISH = "labels_page_multiple_designs_finish"
    LABELS_IMAGE_TRANSFERS_FINISH = "labels_image_transfers_finish"
    
    # Image Transfers
    IMAGE_TRANSFERS_FINISH = "image_transfers_finish"
    
    # Decals
    DECALS_FORMAT = "decals_format"
    DECALS_WALL_WINDOW_FINISH = "decals_wall_window_finish"
    DECALS_FLOOR_OUTDOOR_FINISH = "decals_floor_outdoor_finish"
    DECALS_IMAGE_TRANSFERS_FINISH = "decals_image_transfers_finish"
    
    # Temp Tattoos
    TEMP_TATTOOS_FORMAT = "temp_tattoos_format"
    TEMP_TATTOOS_PAGE_SINGLE_DESIGN_FINISH = "temp_tattoos_page_single_design_finish"
    TEMP_TATTOOS_KISS_CUT_FINISH = "temp_tattoos_kiss_cut_finish"
    TEMP_TATTOOS_PAGE_MULTIPLE_DESIGNS_FINISH = "temp_tattoos_page_multiple_designs_finish"
    
    # Iron-Ons
    IRON_ONS_FORMAT = "iron_ons_format"
    IRON_ONS_PAGE_SINGLE_DESIGN_FINISH = "iron_ons_page_single_design_finish"
    IRON_ONS_PAGE_MULTIPLE_DESIGNS_FINISH = "iron_ons_page_multiple_designs_finish"
    IRON_ONS_TRANSFERS_FINISH = "iron_ons_transfers_finish"
    
    # Magnets
    MAGNETS_FINISH = "magnets_finish"
    
    # Clings
    CLINGS_FINISH = "clings_finish"
    
    # Pouches (original naming)
    POUCHES_POUCH_COLOR_FINISH = "pouches_pouch_color_finish"
    POUCHES_POUCH_SIZE_FINISH = "pouches_pouch_size_finish"
    POUCHES_LABEL_MATERIAL_FINISH = "pouches_label_material_finish"
    
    # Alternative Pouch naming
    POUCHES_LABEL_MATERIAL = "pouches_label_material"
    POUCHES_POUCH_COLOR = "pouches_pouch_color"
    POUCHES_POUCH_SIZE = "pouches_pouch_size"
    
    # Basic Dimensions and Quantities
    TOTAL_QUANTITY = "total_quantity_"
    WIDTH_IN_INCHES = "width_in_inches_"
    HEIGHT_IN_INCHES = "height_in_inches_"
    PROMOTIONAL_PRODUCT_DISTRIBUTOR = "promotional_product_distributor_"
    UPLOAD_YOUR_DESIGN = "upload_your_design"
    ADDITIONAL_INSTRUCTIONS = "additional_instructions_"
    
    # Quote Information - Custom Form Properties
    APPLICATION_USE = "application_use_"
    BUSINESS_CATEGORY = "business_category"
    CALL_REQUESTED = "call_requested"
    HAVE_YOU_ORDERED_WITH_US_BEFORE = "have_you_ordered_with_us_before_"
    HOW_DID_YOU_FIND_US = "how_did_you_find_us_"
    LOCATION = "location"
    NUMBER_OF_COLOURS_IN_DESIGN = "number_of_colours_in_design_"
    OTHER_BUSINESS_CATEGORY = "other_business_category"
    PREFERRED_FORMAT = "preferred_format"
    PREFERRED_FORMAT_STICKERS = "preferred_format_stickers"
    PRODUCT_GROUP = "product_group"
    PRODUCT_GROUP_2 = "product_group_2"
    UPLOAD_YOUR_VECTOR_ARTWORK = "upload_your_vector_artwork"
    USE_TYPE = "use_type"
    WHAT_KIND_OF_CONTENT_WOULD_YOU_LIKE_TO_HEAR_ABOUT = "what_kind_of_content_would_you_like_to_hear_about_"
    WHAT_MADE_YOU_COME_BACK_TO_STICKER_YOU = "what_made_you_come_back_to_sticker_you_"
    WHAT_SIZE_OF_TAPE = "what_size_of_tape_"
    
    # Product Type Properties
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
    
    # Alternative Pouch Properties
    POUCH_LABEL_MATERIAL = "pouch_label_material_"
    POUCH_SIZE = "pouch_size_"
    
    # Additional Custom Quote Properties
    ORDER_NUMBER = "order_number"
    
    # Ticket Information - Custom Properties
    WAS_HANDED_OFF = "was_handed_off"
    CREATED_ON_BUSINESS_HOURS = "created_on_business_hours"
    
    # HubSpot-Defined Ticket Properties
    CREATED_BY = "created_by"
    HS_FILE_UPLOAD = "hs_file_upload"
    HS_IN_HELPDESK = "hs_in_helpdesk"
    HS_INBOX_ID = "hs_inbox_id"
    HS_OBJECT_ID = "hs_object_id"
    HS_TICKET_CATEGORY = "hs_ticket_category"
    HS_TICKET_ID = "hs_ticket_id"
    HS_TICKET_LANGUAGE_AI_TAG = "hs_ticket_language_ai_tag"
    HS_UNIQUE_CREATION_KEY = "hs_unique_creation_key"
    HUBSPOT_OWNER_ID = "hubspot_owner_id"
    SOURCE_TYPE = "source_type"
