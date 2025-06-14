"""
Request DTOs for HubSpot Ticket tools.
"""

# /src/tools/hubspot/tickets/dto_requests.py
from typing import Optional, List
from pydantic import BaseModel, Field

# Import Enums from custom_quote constants
from src.markdown_info.custom_quote.constants import (
    UseTypeEnum,
    BusinessCategoryEnum,
    LocationEnum,
    ProductGroupEnum,
    TypeOfClingEnum,
    TypeOfDecalEnum,
    TypeOfMagnetEnum,
    TypeOfPatchEnum,
    TypeOfLabelEnum,
    TypeOfStickerEnum,
    TypeOfTattooEnum,
    TypeOfTapeEnum,
    PreferredFormatEnum,
    TypeOfPackagingEnum,
    PouchSizeEnum,
    PouchLabelMaterialEnum,
    WhatSizeOfTapeEnum,
)

# Import TypeOfTicketEnum from its new location
from .constants import TypeOfTicketEnum


# --- Association Types --- #
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


# --- Ticker properties --- #
class TicketCreationProperties(BaseModel):
    """Properties for creating a HubSpot ticket. This will be used by both general ticket creation and conversation-specific ticket creation."""

    # --- Required Base Fields ---
    subject: str = Field(..., description="The subject or title of the ticket.")
    content: str = Field(
        ...,
        description="The main description or content of the ticket (e.g., summary of the issue for handoff).",
    )
    hs_pipeline: Optional[str] = Field(
        None,
        description="Optional: The ID of the pipeline the ticket belongs to. Overrides default if provided by logic.",
    )
    hs_pipeline_stage: Optional[str] = Field(
        None,
        description="Optional: The ID of the pipeline stage (status) of the ticket. Overrides default if provided by logic.",
    )
    hs_ticket_priority: str = Field(
        ...,
        description="The priority of the ticket (e.g., 'HIGH', 'MEDIUM', 'LOW').",
    )

    # --- Base Ticket Information Properties ---
    type_of_ticket: TypeOfTicketEnum = Field(
        TypeOfTicketEnum.INQUIRY,
        description="The type of ticket (e.g., 'Quote', 'Request', 'Inquiry', 'Issue', 'Other').",
    )

    # --- Custom Quote Ticket Properties (from form_fields_markdown.py) ---
    use_type: Optional[UseTypeEnum] = Field(
        None, description="Personal or business use? (e.g., 'Personal', 'Business')"
    )
    company: Optional[str] = Field(None, description="Company name")
    business_category: Optional[BusinessCategoryEnum] = Field(
        None, description="Business Category (e.g., 'Amateur Sport', 'Other')"
    )
    other_business_category: Optional[str] = Field(
        None, description="Business Category (Other)"
    )
    promotional_product_distributor_: Optional[bool] = Field(
        None, description="Are you a promotional product distributor? (True/False)"
    )
    location: Optional[LocationEnum] = Field(
        None, description="Location (e.g., 'USA', 'Canada')"
    )
    product_group: Optional[ProductGroupEnum] = Field(
        None, description="Product group (e.g., 'Stickers', 'Decals')"
    )
    type_of_cling_: Optional[TypeOfClingEnum] = Field(None, description="Type of Cling")
    type_of_decal_: Optional[TypeOfDecalEnum] = Field(None, description="Type of Decal")
    type_of_magnet_: Optional[TypeOfMagnetEnum] = Field(
        None, description="Type of Magnet"
    )
    type_of_patch_: Optional[TypeOfPatchEnum] = Field(None, description="Type of Patch")
    type_of_label_: Optional[TypeOfLabelEnum] = Field(None, description="Type of Label")
    type_of_sticker_: Optional[TypeOfStickerEnum] = Field(
        None, description="Type of Sticker"
    )
    type_of_tattoo_: Optional[TypeOfTattooEnum] = Field(
        None, description="Type of Tattoo"
    )
    type_of_tape_: Optional[TypeOfTapeEnum] = Field(None, description="Type of Tape")
    preferred_format: Optional[PreferredFormatEnum] = Field(
        None, description="Preferred Format (e.g., 'Pages', 'Die-Cut Singles')"
    )
    type_of_packaging_: Optional[TypeOfPackagingEnum] = Field(
        None, description="Type of Packaging"
    )
    pouch_size_: Optional[PouchSizeEnum] = Field(None, description="Pouch Size")
    pouch_label_material_: Optional[PouchLabelMaterialEnum] = Field(
        None, description="Pouch Label Material"
    )
    what_size_of_tape_: Optional[WhatSizeOfTapeEnum] = Field(
        None, description="What size of tape?"
    )
    total_quantity_: Optional[float] = Field(None, description="Total Quantity")
    width_in_inches_: Optional[float] = Field(None, description="Width in Inches")
    height_in_inches_: Optional[float] = Field(None, description="Height in Inches")
    application_use_: Optional[str] = Field(None, description="Application Use")
    additional_instructions_: Optional[str] = Field(
        None, description="Additional Instructions"
    )
    call_requested: Optional[bool] = Field(
        None, description="Request a support call (True/False)"
    )
    upload_your_design: Optional[str] = Field(
        None,
        description="Upload your design (e.g., 'Yes, file provided', 'No, assistance requested') - conceptual, actual file path not stored here",
    )
    have_you_ordered_with_us_before_: Optional[bool] = Field(
        None, description="Have you ordered with us before? (True/False)"
    )
    how_did_you_find_us_: Optional[str] = Field(
        None, description="How did you find us?"
    )
    number_of_colours_in_design_: Optional[str] = Field(
        None, description="Number of colours in design (e.g., '1', '2', '3')"
    )
    preferred_format_stickers: Optional[PreferredFormatEnum] = Field(
        None,
        description="Preferred Format Stickers (Potentially duplicate/specific, using PreferredFormatEnum for now)",
    )
    upload_your_vector_artwork: Optional[str] = Field(
        None, description="Upload your vector artwork (Conceptual file status)"
    )
    what_kind_of_content_would_you_like_to_hear_about_: Optional[str] = Field(
        None, description="What kind of content would you like to hear about?"
    )

    model_config = {"extra": "allow"}


class CreateTicketRequest(BaseModel):
    """Request model for the create_ticket tool."""

    properties: TicketCreationProperties = Field(
        ..., description="The properties of the ticket to create."
    )
    associations: Optional[List[AssociationToCreate]] = Field(
        None,
        description="List of associations to create with the ticket. For example, to link to a conversation.",
    )
