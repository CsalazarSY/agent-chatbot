"""
Constants for HubSpot Ticket Associations.
"""

# /src/tools/hubspot/tickets/constants.py
from enum import Enum
from typing import List


class AssociationCategory(str, Enum):
    """Defines the category of the association."""

    HUBSPOT_DEFINED = "HUBSPOT_DEFINED"
    USER_DEFINED = "USER_DEFINED"
    INTEGRATOR_DEFINED = "INTEGRATOR_DEFINED"


class PipelineStage(str, Enum):
    """Defines common HubSpot ticket pipeline stage IDs."""

    NEW = "1"  # Default for many "Support Pipeline" setups
    WAITING_ON_CONTACT = "2"
    WAITING_ON_US = "3"
    CLOSED = "4"


class AssociationTypeIdTicket(Enum):
    """
    Defines HubSpot-defined association type IDs for linking FROM a TICKET TO other objects.
    """

    # Ticket to X
    TICKET_TO_TICKET = 452
    TICKET_TO_CONTACT = 16
    TICKET_TO_COMPANY = 26  # Primary is 26, general is not listed for Ticket To Company, but often same.
    TICKET_TO_COMPANY_PRIMARY = 26
    TICKET_TO_DEAL = 28
    TICKET_TO_CALL = 219
    TICKET_TO_EMAIL = 223
    TICKET_TO_MEETING = 225
    TICKET_TO_NOTE = 227
    TICKET_TO_TASK = 229
    TICKET_TO_COMMUNICATION = 84  # (SMS, WhatsApp, or LinkedIn message)
    TICKET_TO_POSTAL_MAIL = 456
    TICKET_TO_THREAD = 32  # Potentially relevant for chat
    TICKET_TO_CONVERSATION = 278  # Potentially relevant for chat
    TICKET_TO_ORDER = 526
    TICKET_TO_APPOINTMENT = 947
    TICKET_TO_COURSE = 941
    TICKET_TO_LISTING = 943
    TICKET_TO_SERVICE = 797


class AssociationTypeIdContact(Enum):
    """
    Defines HubSpot-defined association type IDs for linking FROM a CONTACT TO other objects.
    """

    # Contact to X
    CONTACT_TO_CONTACT = 449
    CONTACT_TO_COMPANY = 1  # Primary is 1
    CONTACT_TO_COMPANY_PRIMARY = 1
    CONTACT_TO_DEAL = 4
    CONTACT_TO_TICKET = 15
    CONTACT_TO_CALL = 193
    CONTACT_TO_EMAIL = 197
    CONTACT_TO_MEETING = 199
    CONTACT_TO_NOTE = 201
    CONTACT_TO_TASK = 203
    CONTACT_TO_COMMUNICATION = 82
    CONTACT_TO_POSTAL_MAIL = 454
    CONTACT_TO_CART = 587
    CONTACT_TO_ORDER = 508
    CONTACT_TO_INVOICE = 178
    CONTACT_TO_PAYMENT = 388
    CONTACT_TO_SUBSCRIPTION = 296
    CONTACT_TO_APPOINTMENT = 907
    CONTACT_TO_COURSE = 861
    CONTACT_TO_LISTING = 883
    CONTACT_TO_SERVICE = 799


class AssociationTypeIdNote(Enum):
    """
    Defines HubSpot-defined association type IDs for linking FROM a NOTE TO other objects.
    """

    # Note to X
    NOTE_TO_CONTACT = 202
    NOTE_TO_COMPANY = 190
    NOTE_TO_DEAL = 214
    NOTE_TO_TICKET = 228
    NOTE_TO_APPOINTMENT = 921
    NOTE_TO_COURSE = 875
    NOTE_TO_LISTING = 899
    NOTE_TO_SERVICE = 837


class AssociationTypeIdCommunication(Enum):
    """
    Defines HubSpot-defined association type IDs for linking FROM a COMMUNICATION TO other objects.
    """

    # Communication to X
    COMMUNICATION_TO_CONTACT = 81
    COMMUNICATION_TO_COMPANY = 87
    COMMUNICATION_TO_DEAL = 85
    COMMUNICATION_TO_TICKET = 83
    COMMUNICATION_TO_APPOINTMENT = 925
    COMMUNICATION_TO_COURSE = 879
    COMMUNICATION_TO_LISTING = 903
    COMMUNICATION_TO_SERVICE = 847


# Default association type for creating a ticket and linking it to the current conversation
DEFAULT_TICKET_TO_CONVERSATION_TYPE_ID = AssociationTypeIdTicket.TICKET_TO_THREAD.value


class TypeOfTicketEnum(str, Enum):
    """Enum for HubSpot's ticket type_of_ticket field."""

    QUOTE = "Quote"
    REQUEST = "Request"
    INQUIRY = "Inquiry"
    ISSUE = "Issue"
    OTHER = "Other"

    @classmethod
    def get_all_values(cls) -> List[str]:
        return [e.value for e in cls]
