"""HubSpot Ticket Tools"""

# From ticket_tools.py
from .ticket_tools import create_ticket, create_support_ticket_for_conversation

# From constants.py
from .constants import (
    AssociationCategory,
    PipelineStage,
    AssociationTypeIdTicket,
    AssociationTypeIdContact,
    AssociationTypeIdNote,
    AssociationTypeIdCommunication,
    TypeOfTicketEnum,
    DEFAULT_TICKET_TO_CONVERSATION_TYPE_ID,
)

# From dto_requests.py
from .dto_requests import (
    AssociationTypeSpec,
    AssociationToObject,
    AssociationToCreate,
    TicketProperties,
    CreateTicketRequest,
)

# From dto_responses.py
from .dto_responses import (
    TicketAssociationDetail,
    TicketPropertiesResponse,
    TicketDetailResponse,
    BatchTicketDetail,
    BatchReadTicketsResponse,
)


__all__ = [
    # ticket_tools
    "create_ticket",
    "create_support_ticket_for_conversation",
    # constants
    "AssociationCategory",
    "PipelineStage",
    "AssociationTypeIdTicket",
    "AssociationTypeIdContact",
    "AssociationTypeIdNote",
    "AssociationTypeIdCommunication",
    "TypeOfTicketEnum",
    "DEFAULT_TICKET_TO_CONVERSATION_TYPE_ID",
    # dto_requests
    "AssociationTypeSpec",
    "AssociationToObject",
    "AssociationToCreate",
    "TicketProperties",
    "CreateTicketRequest",
    # dto_responses
    "TicketAssociationDetail",
    "TicketPropertiesResponse",
    "TicketDetailResponse",
    "BatchTicketDetail",
    "BatchReadTicketsResponse",
]
