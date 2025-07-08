from enum import Enum, StrEnum
from typing import List, Dict, Any, Union, Optional


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


# Option Enums for Dropdowns
class UseTypeEnum(str, Enum):
    PERSONAL = "Personal"
    BUSINESS = "Business"

    @classmethod
    def get_all_values(cls) -> List[str]:
        return [e.value for e in cls]


class BusinessCategoryEnum(str, Enum):
    AMATEUR_SPORT = "Amateur Sport"
    ASSOCIATIONS = "Associations"
    AUTO_SERVICES = "Auto Services"
    BEVERAGE_PRODUCER = "Beverage Producer"
    CHARITY_NON_PROFIT = "Charity or Non-Profit Association"
    CHILDCARE = "Childcare"
    CLOTHING_COMPANY = "Clothing Company"
    CONTRACTOR_INDUSTRIAL = "Contractor or Industrial"
    ENTERTAINMENT = "Entertainment"
    FOOD_MANUFACTURING_STORE = "Food Manufacturing or Food Store"
    GOVERNMENT = "Government"
    GRAPHIC_DESIGNER = "Graphic Designer"
    HEALTH_FITNESS = "Health & Fitness"
    HEALTH_BEAUTY_AIDS = "Health and Beauty Aids"
    HOTEL_TRAVEL_PLANNER = "Hotel and Travel Planner"
    MARIJUANA_INDUSTRY = "Marijuana Industry"
    MARKETING_AGENCY = "Marketing Agency"
    MEDICAL = "Medical"
    PPAI_ASI_PROMOTIONAL = "PPAI/ASI Promotional"
    PRINTING_COMPANY = "Printing Company"
    PROFESSIONAL_EVENT_PLANNER = "Professional Event Planner"
    PROFESSIONAL_SERVICES = "Professional Services"
    RESTAURANTS_BARS = "Resturants and Bars"
    SCHOOLS = "Schools"
    TECHNOLOGY_COMPANY = "Technology Company"
    OTHER_RETAIL_NON_FOOD = "Other Retail (Non Food Store)"
    OTHER = "Other"

    @classmethod
    def get_all_values(cls) -> List[str]:
        return [e.value for e in cls]


class LocationEnum(str, Enum):
    USA = "USA"
    CANADA = "Canada"
    OUTSIDE_NORTH_AMERICA = "Outside North America"

    @classmethod
    def get_all_values(cls) -> List[str]:
        return [e.value for e in cls]


class ProductGroupEnum(str, Enum):
    BADGE = "Badge"
    CLING = "Cling"
    DECAL = "Decal"
    IRON_ON = "Iron-On"
    MAGNET = "Magnet"
    PACKAGING = "Packaging"
    PACKING_TAPE = "Packing Tape"
    PATCH = "Patch"
    ROLL_LABEL = "Roll Label"
    STICKER = "Sticker"
    TATTOO = "Tattoo"

    @classmethod
    def get_all_values(cls) -> List[str]:
        return [e.value for e in cls]


class TypeOfClingEnum(str, Enum):
    CLEAR_STATIC = "Clear Static Cling"
    WHITE_STATIC = "White Static Cling"

    @classmethod
    def get_all_values(cls) -> List[str]:
        return [e.value for e in cls]


class TypeOfDecalEnum(str, Enum):
    INDOOR_FLOOR_VINYL = "Indoor Floor Vinyl"
    INDOOR_WALL_VINYL = "Indoor Wall Vinyl"
    CLEAR_WINDOW = "Clear Window"
    OUTDOOR_STREET_VINYL = "Outdoor/Street Vinyl"
    STATIC_CLING = "Static Cling"
    DRY_ERASE_VINYL = "Dry Erase Vinyl"
    FROSTED_VINYL_WINDOW_GRAPHIC = "Frosted Vinyl Window Graphic"
    VINYL_GRAPHIC = "Vinyl Graphic"
    UV_DTF_TRANSFER_STICKER = "UV DTF Image Transfer Sticker"

    @classmethod
    def get_all_values(cls) -> List[str]:
        return [e.value for e in cls]


class TypeOfMagnetEnum(str, Enum):
    FRIDGE = "Fridge Magnet"
    CAR = "Car Magnet"

    @classmethod
    def get_all_values(cls) -> List[str]:
        return [e.value for e in cls]


class TypeOfPatchEnum(str, Enum):
    PRINTED = "Printed Patch"
    EMBROIDERED = "Embroidered Patch"

    @classmethod
    def get_all_values(cls) -> List[str]:
        return [e.value for e in cls]


class TypeOfLabelEnum(str, Enum):
    CLEAR_BOPP = "Clear BOPP"
    WHITE_BOPP = "White BOPP"
    EMBOSSED = "Embossed"
    KRAFT_PAPER = "Kraft Paper"
    WHITE_PERMANENT_PAPER = "White Permanent Paper"
    GOLD_FOIL = "Gold Foil"
    SILVER_FOIL = "Silver Foil"
    COLOURED_FOIL = "Coloured Foil"
    WRITABLE_MATTE_BOPP = "Writable Matte BOPP"
    VAR_BARCODE = "Variable Data - Custom Barcode Labels"
    VAR_QR_CODE = "Variable Data - Custom QR Code Labels"
    VAR_SERIAL_NUMBER = "Variable Data - Custom Serial Number Labels"
    VAR_ASSET_TAG = "Variable Data - Custom Asset Tag Labels"
    VAR_SEQUENTIAL_NUMBER = "Variable Data - Custom Sequential Number Labels"
    UV_DTF_TRANSFER_LABEL = "UV DTF Image Transfer Label"

    @classmethod
    def get_all_values(cls) -> List[str]:
        return [e.value for e in cls]


class TypeOfStickerEnum(str, Enum):
    HOLOGRAPHIC = "Holographic"
    GLITTER = "Glitter"
    CLEAR_VINYL = "Clear Vinyl"
    REMOVABLE_WHITE_VINYL = "Removable White Vinyl"
    PERMANENT_WHITE_VINYL = "Permanent White Vinyl"
    MATTE_WHITE_VINYL = "Matte White Vinyl"
    ECO_SAFE = "Eco-Safe"
    HANG_TAG = "Hang Tag"
    REMOVABLE_SMART_SAVE = "Removable Smart Save"
    PERMANENT_GLOW_DIE_CUT = "Permanent Glow in the Dark Die Cut Singles"
    SCRATCH_SNIFF = "Scratch & Sniff"
    MINI_PAGES = "Mini Pages"
    UV_DTF_TRANSFER_STICKER = "UV DTF Image Transfer Sticker"

    @classmethod
    def get_all_values(cls) -> List[str]:
        return [e.value for e in cls]


class TypeOfTattooEnum(str, Enum):
    GLITTER = "Glitter Tattoo"
    GLOW_IN_DARK = "Glow in the Dark Tattoo"
    METALLIC_FOIL = "Metallic Foil Tattoo"
    STANDARD = "Standard Tattoo"
    WHITE_INK = "White Ink Tattoo"

    @classmethod
    def get_all_values(cls) -> List[str]:
        return [e.value for e in cls]


class TypeOfTapeEnum(str, Enum):
    CUSTOM_WHITE = "Custom White Tape"
    CUSTOM_CLEAR = "Custom Clear Tape"
    BLANK_WHITE = "Blank White Tape"
    BLANK_CLEAR = "Blank Clear Tape"

    @classmethod
    def get_all_values(cls) -> List[str]:
        return [e.value for e in cls]


class PreferredFormatEnum(str, Enum):
    PAGES = "Pages"
    KISS_CUT_SINGLES = "Kiss-Cut Singles"
    DIE_CUT_SINGLES = "Die-Cut Singles"

    @classmethod
    def get_all_values(cls) -> List[str]:
        return [e.value for e in cls]


class TypeOfPackagingEnum(str, Enum):
    MATTE_BLACK_POUCH = "Matte Black Pouch"
    KRAFT_PAPER_POUCH = "Kraft Paper Pouch"
    CLEAR_POUCH_SILVER_BACK = "Clear Pouch with Silver Back"
    GLOSSY_WHITE_POUCH = "Glossy White Pouch"

    @classmethod
    def get_all_values(cls) -> List[str]:
        return [e.value for e in cls]


class PouchSizeEnum(StrEnum):
    """Enum for pouch sizes."""

    S_3x5_FLAT_HANGHOLE = '3" x 5" (Flat with Hanghole)'
    M_5x7x3_STANDUP = '5"x 7" x 3" (Stand-Up)'
    L_6x9x3_5_STANDUP = '6" x 9" x 3.5" (Stand-Up)'

    @classmethod
    def get_all_values(cls) -> List[str]:
        return [e.value for e in cls]


class PouchLabelMaterialEnum(str, Enum):
    WHITE_PAPER = "White Paper"
    WHITE_BOPP = "White BOPP"
    SILVER_FOIL = "Silver Foil"
    GOLD_FOIL = "Gold Foil"

    @classmethod
    def get_all_values(cls) -> List[str]:
        return [e.value for e in cls]


class WhatSizeOfTapeEnum(str, Enum):
    IN_2_X_55_YD = '2" x 55 yards'
    IN_2_X_110_YD = '2" x 110 yards'
    IN_3_X_55_YD = '3" x 55 yards'

    @classmethod
    def get_all_values(cls) -> List[str]:
        return [e.value for e in cls]
