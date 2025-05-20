"""
Response DTOs for HubSpot Ticket tools.
"""
# /src/tools/hubspot/tickets/dto_responses.py

from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field


class TicketAssociationDetail(BaseModel):
    """Simplified association detail for responses."""

    id: str
    type: str  # e.g., "contact", "conversation"


class TicketPropertiesResponse(BaseModel):
    """Modeled after SimplePublicObject.properties, but flexible for relevant ticket details."""

    subject: Optional[str] = None
    content: Optional[str] = None
    hs_pipeline: Optional[str] = None
    hs_pipeline_stage: Optional[str] = None
    hs_ticket_priority: Optional[str] = None
    createdate: Optional[str] = None
    lastmodifieddate: Optional[str] = None
    hs_object_id: Optional[str] = None  # Ticket ID
    # Allow any other properties returned by HubSpot
    model_config = {"extra": "allow"}


class TicketDetailResponse(BaseModel):
    """Response model for successful ticket operations like create or get."""

    id: str = Field(..., description="The ID of the ticket.")
    properties: TicketPropertiesResponse = Field(
        ..., description="Key properties of the ticket."
    )
    associations: Optional[Dict[str, List[TicketAssociationDetail]]] = Field(
        None, description="Associated objects, keyed by object type."
    )
    created_at: Optional[str] = Field(None, alias="createdAt")
    updated_at: Optional[str] = Field(None, alias="updatedAt")
    archived: Optional[bool] = False

    model_config = {"populate_by_name": True}


class BatchTicketDetail(BaseModel):
    """Simplified ticket detail for batch responses."""

    id: str
    properties: Dict[str, Any]
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
    archived: Optional[bool] = False


class BatchReadTicketsResponse(BaseModel):
    """Response for batch reading tickets."""

    status: str
    results: List[BatchTicketDetail]
    startedAt: Optional[str] = None
    completedAt: Optional[str] = None
    links: Optional[Dict[str, str]] = None
