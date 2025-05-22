"""
Request DTOs for HubSpot Ticket tools.
"""
# /src/tools/hubspot/tickets/dto_requests.py
from typing import Optional, List
from pydantic import BaseModel, Field


class CreateTicketProperties(BaseModel):
    """Properties for creating a HubSpot ticket."""

    subject: str = Field(..., description="The subject or title of the ticket.")
    content: str = Field(
        ..., description="The main description or content of the ticket."
    )
    hs_pipeline: Optional[str] = Field(
        "0", description="The ID of the pipeline the ticket belongs to."
    )
    hs_pipeline_stage: Optional[str] = Field(
        "2",
        description="The ID of the pipeline stage (status) of the ticket. e.g. New, Waiting, Closed, etc.",
    )
    hs_ticket_priority: Optional[str] = Field(
        None, description="The priority of the ticket (e.g., 'HIGH', 'MEDIUM', 'LOW')."
    )
    # Allow any other string properties to be passed through
    model_config = {"extra": "allow"}


class AssociationTypeSpec(BaseModel):
    """Defines the category and type ID of an association."""

    associationCategory: str = Field(
        default="HUBSPOT_DEFINED",
        description="Category of the association, e.g., HUBSPOT_DEFINED",
    )
    associationTypeId: int = Field(
        ..., description="The HubSpot-defined ID for the association type."
    )


class AssociationToObject(BaseModel):
    """Specifies the object to which the association is being made."""

    id: str = Field(..., description="The ID of the target object for association.")


class AssociationToCreate(BaseModel):
    """Represents an association to be created with the ticket, matching API structure."""

    to: AssociationToObject = Field(
        ..., description="The target object of the association."
    )
    types: List[AssociationTypeSpec] = Field(
        ..., description="A list defining the types of association."
    )


class CreateTicketRequest(BaseModel):
    """Request model for the create_ticket tool."""

    properties: CreateTicketProperties = Field(
        ..., description="The properties of the ticket to create."
    )
    associations: Optional[List[AssociationToCreate]] = Field(
        None,
        description="List of associations to create with the ticket. For example, to link to a conversation.",
    )


class CreateSupportTicketForConversationRequest(BaseModel):
    """Request model for creating a support ticket linked to a specific conversation."""

    conversation_id: str = Field(
        ...,
        description="The ID of the HubSpot conversation/thread to associate this ticket with.",
    )
    subject: str = Field(..., description="The subject or title of the ticket.")
    content: str = Field(
        ...,
        description="The main description or content of the ticket (e.g., summary of the issue for handoff).",
    )
    hs_ticket_priority: str = Field(
        ...,
        description="The priority of the ticket (e.g., 'HIGH', 'MEDIUM', 'LOW').",
    )
    hs_pipeline: Optional[str] = Field(
        None, description="Optional: The ID of the pipeline the ticket belongs to. Overrides default if provided."
    )
    hs_pipeline_stage: Optional[str] = Field(
        None, description="Optional: The ID of the pipeline stage (status) of the ticket. Overrides default if provided."
    )
