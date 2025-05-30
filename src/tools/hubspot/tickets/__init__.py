"""HubSpot Ticket Tools"""

from .ticket_tools import create_support_ticket_for_conversation
from .constants import (
    AssociationCategory,
    AssociationTypeIdTicket,
    AssociationTypeIdContact,
    AssociationTypeIdNote,
    AssociationTypeIdCommunication,
    DEFAULT_TICKET_TO_CONVERSATION_TYPE_ID,
)
from .dto_requests import (
    TicketCreationProperties,
    CreateTicketRequest,
)
from .dto_responses import (
    TicketDetailResponse,
    TicketPropertiesResponse,
    BatchReadTicketsResponse,
    BatchTicketDetail,
    TicketAssociationDetail,
)

__all__ = [
    "create_support_ticket_for_conversation",
    "AssociationCategory",
    "AssociationTypeIdTicket",
    "AssociationTypeIdContact",
    "AssociationTypeIdNote",
    "AssociationTypeIdCommunication",
    "DEFAULT_TICKET_TO_CONVERSATION_TYPE_ID",
    "TicketCreationProperties",
    "CreateTicketRequest",
    "TicketDetailResponse",
    "TicketPropertiesResponse",
    "BatchReadTicketsResponse",
    "BatchTicketDetail",
    "TicketAssociationDetail",
]
