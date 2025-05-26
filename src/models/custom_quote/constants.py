from enum import Enum
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
    RESTAURANTS_BARS = "Resturants and Bars"  # Typo from MD
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
    BADGE = "Badges"
    CLING = "Clings"
    DECAL = "Decals"
    IRON_ON = "Iron-Ons"
    MAGNET = "Magnets"
    PACKAGING = "Packaging"
    PACKING_TAPE = "Packing Tape"
    PATCH = "Patches"
    ROLL_LABEL = "Roll Labels"
    STICKER = "Stickers"
    TATTOO = "Tattoos"

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


class PouchSizeEnum(str, Enum):
    S_3x5_FLAT_HANGHOLE = '3" x 5" (Flat with Hanghole)'
    M_5x7x3_5_STANDUP = '5"x 7" x 3.5" (Stand-Up)'
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


# Define the form structure for AI-based interaction
custom_quote_form_fields = [
    {
        "display_label": "First name",
        "hubspot_internal_name": "firstname",
        "property_type": HubSpotPropertyType.CONTACT_PROPERTY,
        "required": False,
        "type": "string",
    },
    {
        "display_label": "Last name",
        "hubspot_internal_name": "lastname",
        "property_type": HubSpotPropertyType.CONTACT_PROPERTY,
        "required": False,
        "type": "string",
    },
    {
        "display_label": "Email",
        "hubspot_internal_name": "email",
        "property_type": HubSpotPropertyType.CONTACT_PROPERTY,
        "required": True,
        "type": "string",
    },
    {
        "display_label": "Phone number",
        "hubspot_internal_name": "phone",
        "property_type": HubSpotPropertyType.CONTACT_PROPERTY,
        "required": True,
        "type": "string",
    },
    {
        "display_label": "Request a support call",
        "hubspot_internal_name": "call_requested",
        "property_type": HubSpotPropertyType.TICKET_PROPERTY,
        "required": False,
        "type": "boolean",
    },
    {
        "display_label": "Personal or business use?",
        "hubspot_internal_name": "use_type",
        "property_type": HubSpotPropertyType.TICKET_PROPERTY,
        "required": True,
        "type": "string",
        "values": UseTypeEnum.get_all_values(),
        "triggers_conditional_fields": True,
    },
    {
        "display_label": "Company name",
        "hubspot_internal_name": "company",
        "property_type": HubSpotPropertyType.CONTACT_PROPERTY,
        "required": False,
        "type": "string",
        "condition": {"field": "use_type", "value": UseTypeEnum.BUSINESS.value},
    },
    {
        "display_label": "Business Category",
        "hubspot_internal_name": "business_category",
        "property_type": HubSpotPropertyType.TICKET_PROPERTY,
        "required": False,
        "type": "string",
        "values": BusinessCategoryEnum.get_all_values(),
        "condition": {"field": "use_type", "value": UseTypeEnum.BUSINESS.value},
    },
    {
        "display_label": "Business Category (Other)",
        "hubspot_internal_name": "other_business_category",
        "property_type": HubSpotPropertyType.TICKET_PROPERTY,
        "required": False,
        "type": "string",
        "condition": {
            "field": "business_category",
            "value": BusinessCategoryEnum.OTHER.value,
        },
    },
    {
        "display_label": "Are you a promotional product distributor?",
        "hubspot_internal_name": "promotional_product_distributor_",
        "property_type": HubSpotPropertyType.TICKET_PROPERTY,
        "required": False,
        "type": "boolean",
        "condition": {"field": "use_type", "value": UseTypeEnum.BUSINESS.value},
    },
    {
        "display_label": "Location",
        "hubspot_internal_name": "location",
        "property_type": HubSpotPropertyType.TICKET_PROPERTY,
        "required": False,
        "type": "string",
        "values": LocationEnum.get_all_values(),
    },
    {
        "display_label": "Product:",
        "hubspot_internal_name": "product_group",
        "property_type": HubSpotPropertyType.TICKET_PROPERTY,
        "required": True,
        "type": "string",
        "values": ProductGroupEnum.get_all_values(),
        "triggers_conditional_fields": True,
    },
    {
        "display_label": "Type of Cling:",
        "hubspot_internal_name": "type_of_cling_",
        "property_type": HubSpotPropertyType.TICKET_PROPERTY,
        "required": True,
        "type": "string",
        "values": TypeOfClingEnum.get_all_values(),
        "condition": {"field": "product_group", "value": ProductGroupEnum.CLING.value},
    },
    {
        "display_label": "Type of Decal:",
        "hubspot_internal_name": "type_of_decal_",
        "property_type": HubSpotPropertyType.TICKET_PROPERTY,
        "required": True,
        "type": "string",
        "values": TypeOfDecalEnum.get_all_values(),
        "condition": {"field": "product_group", "value": ProductGroupEnum.DECAL.value},
    },
    {
        "display_label": "Type of Magnet:",
        "hubspot_internal_name": "type_of_magnet_",
        "property_type": HubSpotPropertyType.TICKET_PROPERTY,
        "required": True,
        "type": "string",
        "values": TypeOfMagnetEnum.get_all_values(),
        "condition": {"field": "product_group", "value": ProductGroupEnum.MAGNET.value},
    },
    {
        "display_label": "Type of Patch:",
        "hubspot_internal_name": "type_of_patch_",
        "property_type": HubSpotPropertyType.TICKET_PROPERTY,
        "required": True,
        "type": "string",
        "values": TypeOfPatchEnum.get_all_values(),
        "condition": {"field": "product_group", "value": ProductGroupEnum.PATCH.value},
    },
    {
        "display_label": "Type of Label:",
        "hubspot_internal_name": "type_of_label_",
        "property_type": HubSpotPropertyType.TICKET_PROPERTY,
        "required": True,
        "type": "string",
        "values": TypeOfLabelEnum.get_all_values(),
        "condition": {
            "field": "product_group",
            "value": ProductGroupEnum.ROLL_LABEL.value,
        },
    },
    {
        "display_label": "Type of Sticker:",
        "hubspot_internal_name": "type_of_sticker_",
        "property_type": HubSpotPropertyType.TICKET_PROPERTY,
        "required": True,
        "type": "string",
        "values": TypeOfStickerEnum.get_all_values(),
        "condition": {
            "field": "product_group",
            "value": ProductGroupEnum.STICKER.value,
        },
    },
    {
        "display_label": "Type of Tattoo:",
        "hubspot_internal_name": "type_of_tattoo_",
        "property_type": HubSpotPropertyType.TICKET_PROPERTY,
        "required": True,
        "type": "string",
        "values": TypeOfTattooEnum.get_all_values(),
        "condition": {"field": "product_group", "value": ProductGroupEnum.TATTOO.value},
    },
    {
        "display_label": "Type of Tape:",
        "hubspot_internal_name": "type_of_tape_",
        "property_type": HubSpotPropertyType.TICKET_PROPERTY,
        "required": True,
        "type": "string",
        "values": TypeOfTapeEnum.get_all_values(),
        "condition": {
            "field": "product_group",
            "value": ProductGroupEnum.PACKING_TAPE.value,
        },
    },
    {
        "display_label": "Preferred Format",
        "hubspot_internal_name": "preferred_format",
        "property_type": HubSpotPropertyType.TICKET_PROPERTY,
        "required": True,
        "type": "string",
        "values": PreferredFormatEnum.get_all_values(),
        "condition": {
            "field": "product_group",
            "any_of_values": [
                ProductGroupEnum.STICKER.value,
                ProductGroupEnum.ROLL_LABEL.value,
            ],
        },
    },
    {
        "display_label": "Type of Packaging:",
        "hubspot_internal_name": "type_of_packaging_",
        "property_type": HubSpotPropertyType.TICKET_PROPERTY,
        "required": True,
        "type": "string",
        "values": TypeOfPackagingEnum.get_all_values(),
        "condition": {
            "field": "product_group",
            "value": ProductGroupEnum.PACKAGING.value,
        },
    },
    {
        "display_label": "Pouch Size:",
        "hubspot_internal_name": "pouch_size_",
        "property_type": HubSpotPropertyType.TICKET_PROPERTY,
        "required": True,
        "type": "string",
        "values": PouchSizeEnum.get_all_values(),
        "condition": {
            "field": "product_group",
            "value": ProductGroupEnum.PACKAGING.value,
        },
    },
    {
        "display_label": "Pouch Label Material:",
        "hubspot_internal_name": "pouch_label_material_",
        "property_type": HubSpotPropertyType.TICKET_PROPERTY,
        "required": True,
        "type": "string",
        "values": PouchLabelMaterialEnum.get_all_values(),
        "condition": {
            "field": "product_group",
            "value": ProductGroupEnum.PACKAGING.value,
        },
    },
    {
        "display_label": "What size of tape?",
        "hubspot_internal_name": "what_size_of_tape_",
        "property_type": HubSpotPropertyType.TICKET_PROPERTY,
        "required": False,
        "type": "string",
        "values": WhatSizeOfTapeEnum.get_all_values(),
        "condition": {
            "field": "product_group",
            "value": ProductGroupEnum.PACKING_TAPE.value,
        },
    },
    {
        "display_label": "Total Quantity:",
        "hubspot_internal_name": "total_quantity_",
        "property_type": HubSpotPropertyType.TICKET_PROPERTY,
        "required": True,
        "type": "number",
    },
    {
        "display_label": "Width in Inches:",
        "hubspot_internal_name": "width_in_inches_",
        "property_type": HubSpotPropertyType.TICKET_PROPERTY,
        "required": True,
        "type": "number",
    },
    {
        "display_label": "Height in Inches:",
        "hubspot_internal_name": "height_in_inches_",
        "property_type": HubSpotPropertyType.TICKET_PROPERTY,
        "required": True,
        "type": "number",
    },
    {
        "display_label": "Application Use:",
        "hubspot_internal_name": "application_use_",
        "property_type": HubSpotPropertyType.TICKET_PROPERTY,
        "required": False,
        "type": "string",
    },
    {
        "display_label": "Additional Instructions:",
        "hubspot_internal_name": "additional_instructions_",
        "property_type": HubSpotPropertyType.TICKET_PROPERTY,
        "required": False,
        "type": "string",
    },
    {
        "display_label": "Upload your design (multiple files can be selected to be uploaded)",
        "hubspot_internal_name": "upload_your_design",
        "property_type": HubSpotPropertyType.TICKET_PROPERTY,
        "required": False,
        "type": "file",
    },
    {
        "display_label": "Consent to communicate",
        "hubspot_internal_name": "hs_legal_communication_consent_checkbox",
        "property_type": HubSpotPropertyType.CONTACT_PROPERTY,
        "required": True,
        "type": "boolean",
        "note": "StickerYou is committed to protecting and respecting your privacy...",
    },
]
