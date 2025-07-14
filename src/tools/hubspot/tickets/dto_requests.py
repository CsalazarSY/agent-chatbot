"""
Request DTOs for HubSpot Ticket tools.
"""

# /src/tools/hubspot/tickets/dto_requests.py
from typing import Optional, List
from pydantic import BaseModel, Field

# Import Enums from custom_quote constants
from src.markdown_info.custom_quote.constants import (
    StickerFormatEnum,
    StickerPageSingleDesignFinishEnum,
    StickerDieCutFinishEnum,
    StickerKissCutFinishEnum,
    StickerRollsFinishEnum,
    StickerPageMultipleDesignsFinishEnum,
    StickerTransfersFinishEnum,
    LabelsFormatEnum,
    LabelsPageSingleDesignFinishEnum,
    LabelsKissCutFinishEnum,
    LabelsRollsFinishEnum,
    LabelsPageMultipleDesignsFinishEnum,
    LabelsImageTransfersFinishEnum,
    ImageTransfersFinishEnum,
    DecalsFormatEnum,
    DecalsWallWindowFinishEnum,
    DecalsFloorOutdoorFinishEnum,
    DecalsImageTransfersFinishEnum,
    TempTattoosFormatEnum,
    TempTattoosPageSingleDesignFinishEnum,
    TempTattoosKissCutFinishEnum,
    TempTattoosPageMultipleDesignsFinishEnum,
    IronOnsFormatEnum,
    IronOnsPageSingleDesignFinishEnum,
    IronOnsPageMultipleDesignsFinishEnum,
    IronOnsTransfersFinishEnum,
    MagnetsFinishEnum,
    ClingsFinishEnum,
    PouchesPouchColorFinishEnum,
    PouchesPouchSizeFinishEnum,
    PouchesLabelMaterialFinishEnum,
    ProductCategoryEnum,
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

    # --- Contact Properties ---
    firstname: Optional[str] = Field(None, description="First name of the contact.")
    lastname: Optional[str] = Field(None, description="Last name of the contact.")
    email: Optional[str] = Field(None, description="Email address of the contact.")
    phone: Optional[str] = Field(None, description="Phone number of the contact.")

    # --- Base Ticket Information Properties ---
    type_of_ticket: TypeOfTicketEnum = Field(
        TypeOfTicketEnum.INQUIRY,
        description="The type of ticket (e.g., 'Quote', 'Request', 'Inquiry', 'Issue', 'Other').",
    )

    # --- Custom Quote Ticket Properties ---
    promotional_product_distributor_: Optional[bool] = Field(
        None, description="Are you a promotional product distributor? (True/False)"
    )
    total_quantity_: Optional[float] = Field(None, description="Total Quantity")
    width_in_inches_: Optional[float] = Field(None, description="Width in Inches")
    height_in_inches_: Optional[float] = Field(None, description="Height in Inches")
    additional_instructions_: Optional[str] = Field(
        None, description="Additional Instructions"
    )
    upload_your_design: Optional[str] = Field(
        None,
        description="Upload your design (e.g., 'Yes, file provided', 'No, assistance requested') - conceptual, actual file path not stored here",
    )

    # --- Custom Quote Ticket Properties for products (from form_fields_markdown.py) ---
    product_category: Optional[ProductCategoryEnum] = Field(None, description="Product Category")
    sticker_format: Optional[StickerFormatEnum] = Field(None, description="Sticker Format")
    sticker_page_single_design_finish: Optional[StickerPageSingleDesignFinishEnum] = Field(None, description="Finish for Sticker Page (Single Design)")
    sticker_die_cut_finish: Optional[StickerDieCutFinishEnum] = Field(None, description="Finish for Sticker Die-Cut")
    sticker_kiss_cut_finish: Optional[StickerKissCutFinishEnum] = Field(None, description="Finish for Sticker Kiss-Cut")
    sticker_rolls_finish: Optional[StickerRollsFinishEnum] = Field(None, description="Finish for Sticker Rolls")
    sticker_page_multiple_designs_finish: Optional[StickerPageMultipleDesignsFinishEnum] = Field(None, description="Finish for Sticker Page (Multiple Designs)")
    sticker_transfers_finish: Optional[StickerTransfersFinishEnum] = Field(None, description="Finish for Sticker Transfers")
    labels_format: Optional[LabelsFormatEnum] = Field(None, description="Labels Format")
    labels_page_single_design_finish: Optional[LabelsPageSingleDesignFinishEnum] = Field(None, description="Finish for Labels Page (Single Design)")
    labels_kiss_cut_finish: Optional[LabelsKissCutFinishEnum] = Field(None, description="Finish for Labels Kiss-Cut")
    labels_rolls_finish: Optional[LabelsRollsFinishEnum] = Field(None, description="Finish for Labels Rolls")
    labels_page_multiple_designs_finish: Optional[LabelsPageMultipleDesignsFinishEnum] = Field(None, description="Finish for Labels Page (Multiple Designs)")
    labels_image_transfers_finish: Optional[LabelsImageTransfersFinishEnum] = Field(None, description="Finish for Labels Image Transfers")
    image_transfers_finish: Optional[ImageTransfersFinishEnum] = Field(None, description="Finish for Image Transfers")
    decals_format: Optional[DecalsFormatEnum] = Field(None, description="Decals Format")
    decals_wall_window_finish: Optional[DecalsWallWindowFinishEnum] = Field(None, description="Finish for Decals Wall & Window")
    decals_floor_outdoor_finish: Optional[DecalsFloorOutdoorFinishEnum] = Field(None, description="Finish for Decals Floor & Outdoor")
    decals_image_transfers_finish: Optional[DecalsImageTransfersFinishEnum] = Field(None, description="Finish for Decals Image Transfers")
    temp_tattoos_format: Optional[TempTattoosFormatEnum] = Field(None, description="Temp Tattoos Format")
    temp_tattoos_page_single_design_finish: Optional[TempTattoosPageSingleDesignFinishEnum] = Field(None, description="Finish for Temp Tattoos Page (Single Design)")
    temp_tattoos_kiss_cut_finish: Optional[TempTattoosKissCutFinishEnum] = Field(None, description="Finish for Temp Tattoos Kiss-Cut")
    temp_tattoos_page_multiple_designs_finish: Optional[TempTattoosPageMultipleDesignsFinishEnum] = Field(None, description="Finish for Temp Tattoos Page (Multiple Designs)")
    iron_ons_format: Optional[IronOnsFormatEnum] = Field(None, description="Iron-Ons Format")
    iron_ons_page_single_design_finish: Optional[IronOnsPageSingleDesignFinishEnum] = Field(None, description="Finish for Iron-Ons Page (Single Design)")
    iron_ons_page_multiple_designs_finish: Optional[IronOnsPageMultipleDesignsFinishEnum] = Field(None, description="Finish for Iron-Ons Page (Multiple Designs)")
    iron_ons_transfers_finish: Optional[IronOnsTransfersFinishEnum] = Field(None, description="Finish for Iron-Ons Transfers")
    magnets_finish: Optional[MagnetsFinishEnum] = Field(None, description="Finish for Magnets")
    clings_finish: Optional[ClingsFinishEnum] = Field(None, description="Finish for Clings")
    pouches_pouch_color_finish: Optional[PouchesPouchColorFinishEnum] = Field(None, description="Pouch Color")
    pouches_pouch_size_finish: Optional[PouchesPouchSizeFinishEnum] = Field(None, description="Pouch Size")
    pouches_label_material_finish: Optional[PouchesLabelMaterialFinishEnum] = Field(None, description="Label Material")

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
