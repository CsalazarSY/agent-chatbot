"""
HubSpot constants module.

This module contains all HubSpot-related constants including field types,
property types, and custom properties for tickets.
"""

from .hubspot import (
    HubSpotFieldType,
    HubSpotPropertyType,
    HubSpotTicketCategoryEnum,
    HubSpotTicketPriorityEnum,
    HubSpotSourceTypeEnum,
    HubSpotTicketLanguageEnum,
)

from .property_names import (
    HubSpotPropertyName,
)

from .custom_properties_values import (
    TicketCustomPropertyName,
    TicketTypeEnum,
    OwnerAvailabilityEnum,
)

__all__ = [
    # Base HubSpot Constants
    "HubSpotFieldType",
    "HubSpotPropertyType",
    "HubSpotTicketCategoryEnum",
    "HubSpotTicketPriorityEnum",
    "HubSpotSourceTypeEnum",
    "HubSpotTicketLanguageEnum",
    
    # Unified Property Names
    "HubSpotPropertyName",
    
    # Custom Ticket Properties
    "TicketCustomPropertyName",
    "TicketTypeEnum",
    "OwnerAvailabilityEnum",
]
