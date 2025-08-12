"""
Custom Quote Form Properties - Based on HubSpot API JSON data.

This file contains all the constants for the custom quote form properties
as they appear in HubSpot. These are grouped by their logical function
in the custom quote process.
"""

from ..base import BaseEnum


# =============================================================================
# BUSINESS INFORMATION
# =============================================================================

class BusinessCategoryEnum(BaseEnum):
    """Business Category options for custom quote form."""
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
    RESTAURANTS_AND_BARS = "Resturants and Bars"  # Note: misspelling matches HubSpot data
    SCHOOLS = "Schools"
    TECHNOLOGY_COMPANY = "Technology Company"
    OTHER_RETAIL_NON_FOOD_STORE = "Other Retail (Non Food Store)"
    OTHER = "Other Not Shown"  # Note: value differs from label in HubSpot


class HowDidYouFindUsEnum(BaseEnum):
    """How did you find us options for custom quote form."""
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


class WhatMadeYouComeBackEnum(BaseEnum):
    """What made you come back to StickerYou options."""
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


class ContentPreferenceEnum(BaseEnum):
    """Content preference options for marketing."""
    BUSINESS_PRODUCTS_AND_NEWS = "Business Products and News"
    CONSUMER_PRODUCTS_AND_NEWS = "Consumer Products and News"
    PRODUCTS_AND_SWEET_DEALS_FOR_PARENTS = "Products and Sweet Deals for Parents"
    NOT_SURE_YET_SEND_ME_EVERYTHING = "Not sure yet - send me everything!"


# =============================================================================
# BASIC FORM FIELDS
# =============================================================================

class LocationEnum(BaseEnum):
    """Location options for custom quote form."""
    USA = "USA"
    CANADA = "Canada"
    OUTSIDE_NORTH_AMERICA = "Outside North America"


class UseTypeEnum(BaseEnum):
    """Use type options for custom quote form."""
    PERSONAL = "Personal"
    BUSINESS = "Business"


class YesNoEnum(BaseEnum):
    """Yes/No options for boolean-like fields."""
    YES = "yes"
    NO = "no"


# =============================================================================
# PRODUCT SPECIFICATION
# =============================================================================

class ProductGroupEnum(BaseEnum):
    """Product Group options for custom quote form."""
    BADGE = "Badge"
    CLING = "Cling"
    DECAL = "Decal"
    IRON_ON = "Iron-On"
    MAGNET = "Magnet"
    PACKAGING = "Packaging"
    PATCH = "Patch"
    ROLL_LABEL = "Roll Label"
    SERVICES = "Services"  # hidden in HubSpot
    SIGNAGE = "Signage"  # hidden in HubSpot
    STICKER = "Sticker"
    TAPE = "Tape"
    TATTOO = "Tattoo"
    NONE_PRODUCT_REQUEST = "None Product Request"  # hidden in HubSpot


class PreferredFormatEnum(BaseEnum):
    """Preferred Format options for custom quote form."""
    PAGES = "Pages"
    KISS_CUT_SINGLES = "Kiss-Cut Singles"
    DIE_CUT_SINGLES = "Die-Cut Singles"


class NumberOfColoursInDesignEnum(BaseEnum):
    """Number of colours in design options."""
    ONE = "1"
    TWO = "2"
    THREE = "3"


# =============================================================================
# PRODUCT TYPES
# =============================================================================

class TypeOfStickerEnum(BaseEnum):
    """Type of Sticker options for custom quote form."""
    GOLD_FOIL_UV_DTF_IMAGE_TRANSFERS = "Gold Foil UV DTF Image Transfers"
    HOLOGRAPHIC = "Holographic"
    GLITTER = "Glitter"
    CLEAR_VINYL = "Clear Vinyl"
    REMOVABLE_WHITE_VINYL = "Removable White Vinyl"
    PERMANENT_WHITE_VINYL = "Permanent White Vinyl"
    MATTE_WHITE_VINYL = "Matte White Vinyl"
    ECO_SAFE = "Eco-Safe"
    HANG_TAG = "Hang Tag"
    REMOVABLE_SMART_SAVE = "Smart Save Die-Cut Sticker"  # Note: value differs from label
    PERMANENT_GLOW_IN_THE_DARK_DIE_CUT_SINGLES = "Permanent Glow in the Dark Die Cut Singles"
    SCRATCH_AND_SNIFF = "Scratch & Sniff"
    MINI_PAGES = "Mini Pages"
    UV_DTF_IMAGE_TRANSFER_STICKER = "UV DTF Image Transfer Sticker"


class TypeOfLabelEnum(BaseEnum):
    """Type of Label options for custom quote form."""
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
    UV_DTF_IMAGE_TRANSFER_LABEL = "Permanent Image Transfer Label"  # Note: value differs from label


class TypeOfDecalEnum(BaseEnum):
    """Type of Decal options for custom quote form."""
    INDOOR_FLOOR_VINYL = "Indoor Floor Vinyl"
    INDOOR_WALL_VINYL = "Indoor Wall Vinyl"
    CLEAR_WINDOW = "Clear Window"
    OUTDOOR_STREET_VINYL = "Outdoor/Street Vinyl"
    STATIC_CLING = "Static Cling"
    DRY_ERASE_VINYL = "Dry Erase Vinyl"
    FROSTED_VINYL_WINDOW_GRAPHIC = "Frosted Vinyl Window Graphic"
    VINYL_GRAPHIC = "Vinyl Graphic"
    UV_DTF_IMAGE_TRANSFER_STICKER = "Permanent Image Transfer Decal"  # Note: value differs from label


class TypeOfImageTransferEnum(BaseEnum):
    """Type of Image Transfer options for custom quote form."""
    GOLD_FOIL_UV_DTF_IMAGE_TRANSFERS = "Gold Foil UV DTF Image Transfers"
    UV_DTF_IMAGE_TRANSFERS = "UV DTF Image Transfers"  # Note: value differs from label


class TypeOfClingEnum(BaseEnum):
    """Type of Cling options for custom quote form."""
    CLEAR_STATIC_CLING = "Clear Static Cling"
    WHITE_STATIC_CLING = "White Static Cling"


class TypeOfMagnetEnum(BaseEnum):
    """Type of Magnet options for custom quote form."""
    FRIDGE_MAGNET = "Fridge Magnet"
    CAR_MAGNET = "Car Magnet"


class TypeOfPackagingEnum(BaseEnum):
    """Type of Packaging options for custom quote form."""
    MATTE_BLACK_POUCH = "Matte Black Pouch"
    KRAFT_PAPER_POUCH = "Kraft Paper Pouch"
    CLEAR_POUCH_WITH_SILVER_BACK = "Clear Pouch with Silver Back"
    GLOSSY_WHITE_POUCH = "Glossy White Pouch"


class TypeOfPatchEnum(BaseEnum):
    """Type of Patch options for custom quote form."""
    PRINTED_PATCH = "Printed Patch"
    EMBROIDERED_PATCH = "Embroidered Patch"


class TypeOfTapeEnum(BaseEnum):
    """Type of Tape options for custom quote form."""
    CUSTOM_WHITE_TAPE = "Custom White Tape"
    CUSTOM_CLEAR_TAPE = "Custom Clear Tape"
    BLANK_WHITE_TAPE = "Blank White Tape"
    BLANK_CLEAR_TAPE = "Blank Clear Tape"


class TypeOfTattooEnum(BaseEnum):
    """Type of Tattoo options for custom quote form."""
    GLITTER_TATTOO = "Glitter Tattoo"
    GLOW_IN_THE_DARK_TATTOO = "Glow in the Dark Tattoo"
    METALLIC_FOIL_TATTOO = "Metallic Foil Tattoo"
    STANDARD_TATTOO = "Standard Tattoo"
    WHITE_INK_TATTOO = "White Ink Tattoo"


# =============================================================================
# PACKAGING SPECIFIC OPTIONS
# =============================================================================

class PouchSizeEnum(BaseEnum):
    """Pouch Size options for packaging products."""
    THREE_BY_FIVE_FLAT_WITH_HANGHOLE = "3\" x 5\" (Flat with Hanghole)"
    FIVE_BY_SEVEN_BY_THREE_STAND_UP = "5\"x 7\" x 3\" (Stand-Up)"
    SIX_BY_NINE_BY_THREE_FIVE_STAND_UP = "6\" x 9\" x 3.5\" (Stand-Up)"


class PouchLabelMaterialEnum(BaseEnum):
    """Pouch Label Material options for packaging products."""
    WHITE_PAPER = "White Paper"
    WHITE_BOPP = "White BOPP"
    SILVER_FOIL = "Silver Foil"
    GOLD_FOIL = "Gold Foil"


# =============================================================================
# TAPE SPECIFIC OPTIONS
# =============================================================================

class TapeSizeEnum(BaseEnum):
    """Tape Size options for tape products."""
    TWO_INCH_55_YARDS = "2\" x 55 yards"
    TWO_INCH_110_YARDS = "2\" x 110 yards"
    THREE_INCH_55_YARDS = "3\" x 55 yards"
