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
    BusinessCategoryEnum,
    HowDidYouFindUsEnum,
    NumberOfColoursInDesignEnum,
    PreferredFormatEnum,
    ProductGroupEnum,
    HubSpotTicketCategoryEnum,
    HubSpotTicketPriorityEnum,
    HubSpotSourceTypeEnum,
    HubSpotTicketLanguageEnum,
    LocationEnum,
    TypeOfClingEnum,
    TypeOfDecalEnum,
    TypeOfImageTransferEnum,
    TypeOfLabelEnum,
    TypeOfMagnetEnum,
    TypeOfPackagingEnum,
    TypeOfPatchEnum,
    TypeOfStickerEnum,
    TypeOfTapeEnum,
    TypeOfTattooEnum,
    UseTypeEnum,
    ContentPreferenceEnum,
    WhatMadeYouComeBackEnum,
    TapeSizeEnum,
    YesNoEnum,
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


# --- Ticket properties --- #
class TicketProperties(BaseModel):
    """Properties for updating a HubSpot ticket. This will be used by both general ticket updates and conversation-specific ticket updates."""

    # --- Required Base Fields ---
    subject: Optional[str] = Field(None, description="The subject or title of the ticket.")
    content: Optional[str] = Field(
        None,
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
    hs_ticket_priority: Optional[HubSpotTicketPriorityEnum] = Field(
        None,
        description="The level of attention needed on the ticket (e.g., 'LOW', 'MEDIUM', 'HIGH', 'URGENT').",
    )

    # --- Contact Properties ---
    firstname: Optional[str] = Field(None, description="First name of the contact.")
    lastname: Optional[str] = Field(None, description="Last name of the contact.")
    email: Optional[str] = Field(None, description="Email address of the contact.")
    phone: Optional[str] = Field(None, description="Phone number of the contact.")

    # --- Base Ticket Information Properties ---
    type_of_ticket: Optional[TypeOfTicketEnum] = Field(
        TypeOfTicketEnum.INQUIRY,
        description="The type of ticket (e.g., 'Quote', 'Request', 'Inquiry', 'Issue', 'Other').",
    )

    # --- Custom Quote Ticket Properties ---
    # Basic dimension and quantity information

    # --- Quick Quote - Proposed Values Properties / Custom Quote Ticket Properties for products (from form_fields_markdown.py) ---
    # Product Category (Main Selection)
    product_category: Optional[ProductCategoryEnum] = Field(None, description="Product Category")
    
    # Clings
    clings_finish: Optional[ClingsFinishEnum] = Field(None, description="Finish for Clings")
    
    # Decals  
    decals_floor_outdoor_finish: Optional[DecalsFloorOutdoorFinishEnum] = Field(None, description="Finish for Decals Floor & Outdoor")
    decals_format: Optional[DecalsFormatEnum] = Field(None, description="Decals Format")
    decals_image_transfers_finish: Optional[DecalsImageTransfersFinishEnum] = Field(None, description="Finish for Decals Image Transfers")
    decals_wall_window_finish: Optional[DecalsWallWindowFinishEnum] = Field(None, description="Finish for Decals Wall & Window")
    
    # Image Transfers
    image_transfers_finish: Optional[ImageTransfersFinishEnum] = Field(None, description="Finish for Image Transfers")
    
    # Iron-Ons
    iron_ons_format: Optional[IronOnsFormatEnum] = Field(None, description="Iron-Ons Format")
    iron_ons_page_multiple_designs_finish: Optional[IronOnsPageMultipleDesignsFinishEnum] = Field(None, description="Finish for Iron-Ons Page (Multiple Designs)")
    iron_ons_page_single_design_finish: Optional[IronOnsPageSingleDesignFinishEnum] = Field(None, description="Finish for Iron-Ons Page (Single Design)")
    iron_ons_transfers_finish: Optional[IronOnsTransfersFinishEnum] = Field(None, description="Finish for Iron-Ons Transfers")
    
    # Labels
    labels_format: Optional[LabelsFormatEnum] = Field(None, description="Labels Format")
    labels_image_transfers_finish: Optional[LabelsImageTransfersFinishEnum] = Field(None, description="Finish for Labels Image Transfers")
    labels_kiss_cut_finish: Optional[LabelsKissCutFinishEnum] = Field(None, description="Finish for Labels Kiss-Cut")
    labels_page_multiple_designs_finish: Optional[LabelsPageMultipleDesignsFinishEnum] = Field(None, description="Finish for Labels Page (Multiple Designs)")
    labels_page_single_design_finish: Optional[LabelsPageSingleDesignFinishEnum] = Field(None, description="Finish for Labels Page (Single Design)")
    labels_rolls_finish: Optional[LabelsRollsFinishEnum] = Field(None, description="Finish for Labels Rolls")
    
    # Magnets
    magnets_finish: Optional[MagnetsFinishEnum] = Field(None, description="Finish for Magnets")
    
    # Pouches
    pouches_label_material_finish: Optional[PouchesLabelMaterialFinishEnum] = Field(None, description="Label Material")
    pouches_pouch_color_finish: Optional[PouchesPouchColorFinishEnum] = Field(None, description="Pouch Color")
    pouches_pouch_size_finish: Optional[PouchesPouchSizeFinishEnum] = Field(None, description="Pouch Size")
    
    # Stickers
    sticker_die_cut_finish: Optional[StickerDieCutFinishEnum] = Field(None, description="Finish for Sticker Die-Cut")
    sticker_format: Optional[StickerFormatEnum] = Field(None, description="Sticker Format")
    sticker_kiss_cut_finish: Optional[StickerKissCutFinishEnum] = Field(None, description="Finish for Sticker Kiss-Cut")
    sticker_page_multiple_designs_finish: Optional[StickerPageMultipleDesignsFinishEnum] = Field(None, description="Finish for Sticker Page (Multiple Designs)")
    sticker_page_single_design_finish: Optional[StickerPageSingleDesignFinishEnum] = Field(None, description="Finish for Sticker Page (Single Design)")
    sticker_rolls_finish: Optional[StickerRollsFinishEnum] = Field(None, description="Finish for Sticker Rolls")
    sticker_transfers_finish: Optional[StickerTransfersFinishEnum] = Field(None, description="Finish for Sticker Transfers")
    
    # Temp Tattoos
    temp_tattoos_format: Optional[TempTattoosFormatEnum] = Field(None, description="Temp Tattoos Format")
    temp_tattoos_kiss_cut_finish: Optional[TempTattoosKissCutFinishEnum] = Field(None, description="Finish for Temp Tattoos Kiss-Cut")
    temp_tattoos_page_multiple_designs_finish: Optional[TempTattoosPageMultipleDesignsFinishEnum] = Field(None, description="Finish for Temp Tattoos Page (Multiple Designs)")
    temp_tattoos_page_single_design_finish: Optional[TempTattoosPageSingleDesignFinishEnum] = Field(None, description="Finish for Temp Tattoos Page (Single Design)")

    # These are alternative property names for the quick quote form
    pouches_label_material: Optional[PouchesLabelMaterialFinishEnum] = Field(None, description="Pouch Label Material (alternative field)")
    pouches_pouch_color: Optional[PouchesPouchColorFinishEnum] = Field(None, description="Pouch Color (alternative field)")
    pouches_pouch_size: Optional[PouchesPouchSizeFinishEnum] = Field(None, description="Pouch Size (alternative field)")

    # --- Additional Custom Quote Properties ---
    order_number: Optional[str] = Field(None, description="Order Number")

    # --- Quote Information - Custom Form Properties ---
    # These properties are from the custom_quote_properties group in HubSpot
    # They represent alternative field names that may be used in different forms
    
    # Basic Info Properties (moved and new)
    additional_instructions_: Optional[str] = Field(None, description="Additional Instructions")
    application_use_: Optional[str] = Field(None, description="Application Use")
    business_category: Optional[BusinessCategoryEnum] = Field(None, description="Business Category")
    call_requested: Optional[bool] = Field(None, description="Call Requested")
    have_you_ordered_with_us_before_: Optional[bool] = Field(None, description="Have you ordered with us before?")
    height_in_inches_: Optional[float] = Field(None, description="Height in Inches")
    how_did_you_find_us_: Optional[HowDidYouFindUsEnum] = Field(None, description="How did you find us?")
    location: Optional[LocationEnum] = Field(None, description="Location")
    number_of_colours_in_design_: Optional[NumberOfColoursInDesignEnum] = Field(None, description="Number of colours in design")
    other_business_category: Optional[str] = Field(None, description="Other Business Category")
    preferred_format: Optional[PreferredFormatEnum] = Field(None, description="Preferred Format")
    preferred_format_stickers: Optional[PreferredFormatEnum] = Field(None, description="Preferred Format Stickers")
    product_group: Optional[ProductGroupEnum] = Field(None, description="Product Group")
    product_group_2: Optional[ProductGroupEnum] = Field(None, description="Product Group 2")
    promotional_product_distributor_: Optional[bool] = Field(None, description="Promotional Product Distributor?")
    total_quantity_: Optional[float] = Field(None, description="Total Quantity")
    upload_your_design: Optional[str] = Field(None, description="Upload your design")
    upload_your_vector_artwork: Optional[str] = Field(None, description="Upload your vector artwork")
    use_type: Optional[UseTypeEnum] = Field(None, description="Use Type")
    what_kind_of_content_would_you_like_to_hear_about_: Optional[ContentPreferenceEnum] = Field(None, description="What kind of content would you like to hear about?")
    what_made_you_come_back_to_sticker_you_: Optional[WhatMadeYouComeBackEnum] = Field(None, description="What made you come back to Sticker You?")
    what_size_of_tape_: Optional[TapeSizeEnum] = Field(None, description="What size of tape?")
    width_in_inches_: Optional[float] = Field(None, description="Width in Inches")
    
    # Product Type Properties
    type_of_cling_: Optional[TypeOfClingEnum] = Field(None, description="Type of Cling")
    type_of_decal_: Optional[TypeOfDecalEnum] = Field(None, description="Type of Decal")
    type_of_image_transfer_: Optional[TypeOfImageTransferEnum] = Field(None, description="Type of Image Transfer")
    type_of_label_: Optional[TypeOfLabelEnum] = Field(None, description="Type of Label")
    type_of_magnet_: Optional[TypeOfMagnetEnum] = Field(None, description="Type of Magnet")
    type_of_packaging_: Optional[TypeOfPackagingEnum] = Field(None, description="Type of Packaging")
    type_of_patch_: Optional[TypeOfPatchEnum] = Field(None, description="Type of Patch")
    type_of_sticker_: Optional[TypeOfStickerEnum] = Field(None, description="Type of Sticker")
    type_of_tape_: Optional[TypeOfTapeEnum] = Field(None, description="Type of Tape")
    type_of_tattoo_: Optional[TypeOfTattooEnum] = Field(None, description="Type of Tattoo")
    
    # Pouch Properties (alternative naming)
    pouch_label_material_: Optional[PouchesLabelMaterialFinishEnum] = Field(None, description="Pouch Label Material")
    pouch_size_: Optional[PouchesPouchSizeFinishEnum] = Field(None, description="Pouch Size")

    # --- Ticket Information - Custom Properties ---
    # These properties are from the ticket_information_-_custom group in HubSpot
    was_handed_off: Optional[YesNoEnum] = Field(None, description="Was handed off")
    created_on_business_hours: Optional[YesNoEnum] = Field(None, description="Was created on business hours")

    # --- HubSpot-Defined Ticket Properties ---
    created_by: Optional[float] = Field(None, description="VID of contact that created the ticket")
    hs_file_upload: Optional[str] = Field(None, description="Files attached to a support form by a contact")
    hs_in_helpdesk: Optional[bool] = Field(None, description="Is this Ticket rendered in the Help Desk")
    hs_inbox_id: Optional[float] = Field(None, description="Inbox the ticket is in")
    hs_object_id: Optional[float] = Field(None, description="The unique ID for this record. This value is set automatically by HubSpot")
    hs_pipeline_stage: Optional[str] = Field(None, description="The ID of the pipeline stage (status) of the ticket")
    hs_ticket_category: Optional[HubSpotTicketCategoryEnum] = Field(None, description="Main reason customer reached out for help")
    hs_ticket_id: Optional[float] = Field(None, description="The unique id for this ticket. This unique id is automatically populated by HubSpot")
    hs_ticket_language_ai_tag: Optional[HubSpotTicketLanguageEnum] = Field(None, description="Language identified by AI based on the visitor's messages within a ticket")
    hs_unique_creation_key: Optional[str] = Field(None, description="Unique property used for idempotent creates")
    hubspot_owner_id: Optional[str] = Field(None, description="User the ticket is assigned to")
    source_type: Optional[HubSpotSourceTypeEnum] = Field(None, description="Channel where ticket was originally submitted")

    model_config = {"extra": "allow"}


class CreateTicketRequest(BaseModel):
    """Request model for the create_ticket tool."""

    properties: TicketProperties = Field(
        ..., description="The properties of the ticket to create."
    )
    associations: Optional[List[AssociationToCreate]] = Field(
        None,
        description="List of associations to create with the ticket. For example, to link to a conversation.",
    )
