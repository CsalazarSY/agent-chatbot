"""
HubSpot Custom Properties - Ticket Information Custom Group.

This file contains all the constants for the HubSpot custom properties
in the "ticket_information_-_custom" group. These properties are used
for custom ticket management and workflow automation.

Group: "ticket_information_-_custom"
"""

from ..base import BaseEnum


# =============================================================================
# TICKET CUSTOM PROPERTY NAMES
# =============================================================================

class TicketCustomPropertyName(BaseEnum):
    """Property names for custom ticket information fields in HubSpot."""
    
    # Basic Contact Information
    COMPANY = "company"
    EMAIL = "email"
    FIRSTNAME = "firstname"
    LASTNAME = "lastname"
    PHONE = "phone"
    
    # Ticket Management
    CONTACT_OWNER = "contact_owner"
    TYPE_OF_TICKET = "type_of_ticket"
    
    # Workflow and Automation
    CREATE_HOUR = "create_hour"
    CREATED_ON_BUSINESS_HOURS = "created_on_business_hours"
    OWNER_AVAILABILITY = "owner_availability"
    WAS_HANDED_OFF = "was_handed_off"


# =============================================================================
# TICKET TYPE OPTIONS
# =============================================================================

class TicketTypeEnum(BaseEnum):
    """Type of Ticket options for HubSpot tickets."""
    QUOTE = "Quote"
    REQUEST = "Request"
    INQUIRY = "Inquiry"
    ISSUE = "Issue"
    OTHER = "Other"
    ORDER_MGMT = "Order Mgmt"
    ORDER_ON_HOLD = "Order On Hold"


# =============================================================================
# AVAILABILITY OPTIONS
# =============================================================================

class OwnerAvailabilityEnum(BaseEnum):
    """Owner availability status options."""
    AVAILABLE = "available"
    AWAY = "away"
