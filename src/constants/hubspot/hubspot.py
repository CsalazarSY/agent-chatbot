"""HubSpot-related constants and enums."""

from enum import Enum
from ..base import BaseEnum


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
