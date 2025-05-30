from typing import Tuple, Optional

from src.tools.hubspot.tickets.dto_requests import TicketCreationProperties
from src.tools.hubspot.tickets.constants import TypeOfTicketEnum
from src.models.custom_quote.constants import (
    ProductGroupEnum,
    TypeOfStickerEnum,
    TypeOfTattooEnum,
    TypeOfPatchEnum,
    TypeOfDecalEnum,
    TypeOfLabelEnum,
    TypeOfTapeEnum,
    PreferredFormatEnum,
)
from config import (
    HUBSPOT_PIPELINE_ID_SUPPORT,
    HUBSPOT_SUPPORT_STAGE_ID,
    HUBSPOT_PIPELINE_ID_ASSISTED_SALES,
    HUBSPOT_AS_STAGE_ID,
    HUBSPOT_PIPELINE_ID_PROMO_RESELLER,
    HUBSPOT_PR_STAGE_ID,
)

# Keywords for Assisted Sales logic
ASSISTED_SALES_CONTENT_KEYWORDS = [
    "art service",
    "design service",
    "purchase order",
    "color matching",
    "colour matching",
    "pms",
    "design assistance",
    "color management",
    "help with artwork",
    "help designing",
    "frosted",
    "sequential",
    "bulk discount",
    "corn hole",
    "cornhole",
    "serial number",
    "kraft paper",
    "kraft",
    "proof",
    "vinyl graphic",
    "reflective",
]

ASSISTED_SALES_INSTRUCTIONS_KEYWORDS = [
    "color matching",
    "colour matching",
    "pms",
    "design assistance",
    "color management",
    "help with artwork",
    "help designing",
    "frosted",
    "sequential",
    "bulk discount",
    "corn hole",
    "cornhole",
    "serial number",
    "kraft",
    "proof",
    "vinyl graphic",
]


def _check_keywords(text: Optional[str], keywords: list[str]) -> bool:
    """Checks if any keyword is present in the text (case-insensitive)."""
    if not text:
        return False
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in keywords)


def _is_promo_reseller_ticket(properties: TicketCreationProperties) -> bool:
    """Determines if the ticket should go to the Promo Reseller pipeline."""
    promo_value = properties.promotional_product_distributor_
    if isinstance(promo_value, str):
        return promo_value.lower() == "true" or promo_value.lower() == "yes"
    return bool(promo_value)


def _is_assisted_sales_ticket(properties: TicketCreationProperties) -> bool:
    """Determines if the ticket should go to the Assisted Sales pipeline based on complex conditions."""
    # Condition 1: Content/Summary Keywords
    # Using subject as a fallback if content is None or empty, or combining them.
    search_text_content = (properties.content or "") + " " + (properties.subject or "")
    if _check_keywords(search_text_content.strip(), ASSISTED_SALES_CONTENT_KEYWORDS):
        return True

    # Condition 2: Additional Instructions Keywords
    if _check_keywords(
        properties.additional_instructions_, ASSISTED_SALES_INSTRUCTIONS_KEYWORDS
    ):
        return True

    is_quote = properties.type_of_ticket == TypeOfTicketEnum.QUOTE

    # Dimension Checks
    if is_quote:
        if properties.width_in_inches_ is not None and properties.width_in_inches_ > 72:
            return True
        if (
            properties.height_in_inches_ is not None
            and properties.height_in_inches_ > 72
        ):
            return True
        if (
            properties.width_in_inches_ is not None
            and properties.width_in_inches_ < 0.75
        ):
            return True
        if (
            properties.height_in_inches_ is not None
            and properties.height_in_inches_ < 0.75
        ):
            return True

    # Specific Product/Type Checks
    # Helper to safely get enum values or handle strings
    def get_value(prop_value):
        return prop_value.value if hasattr(prop_value, "value") else prop_value

    pg_val = get_value(properties.product_group)
    tos_val = get_value(properties.type_of_sticker_)
    tot_val = get_value(properties.type_of_tattoo_)
    topa_val = get_value(properties.type_of_patch_)
    tode_val = get_value(properties.type_of_decal_)
    tola_val = get_value(properties.type_of_label_)
    tota_val = get_value(properties.type_of_tape_)
    pf_val = get_value(properties.preferred_format)
    tq = properties.total_quantity_

    if is_quote:
        if (
            pg_val == ProductGroupEnum.PATCH.value
            and topa_val == TypeOfPatchEnum.EMBROIDERED.value
        ):
            return True
        if pg_val in [ProductGroupEnum.PACKING_TAPE.value] and tota_val in [
            TypeOfTapeEnum.CUSTOM_CLEAR.value,
            TypeOfTapeEnum.CUSTOM_WHITE.value,
            TypeOfTapeEnum.BLANK_CLEAR.value,
            TypeOfTapeEnum.BLANK_WHITE.value,
        ]:  # Assuming Signage is not in ProductGroupEnum or handled differently
            return True
        if pg_val == ProductGroupEnum.DECAL.value and tode_val in [
            TypeOfDecalEnum.FROSTED_VINYL_WINDOW_GRAPHIC.value,
            TypeOfDecalEnum.DRY_ERASE_VINYL.value,
            TypeOfDecalEnum.VINYL_GRAPHIC.value,
        ]:
            return True
        if (
            pg_val == ProductGroupEnum.STICKER.value
            and tos_val == TypeOfStickerEnum.HANG_TAG.value
        ):
            return True
        if pg_val == ProductGroupEnum.ROLL_LABEL.value and tola_val in [
            TypeOfLabelEnum.VAR_BARCODE.value,
            TypeOfLabelEnum.VAR_QR_CODE.value,
            TypeOfLabelEnum.VAR_SERIAL_NUMBER.value,
            TypeOfLabelEnum.VAR_SEQUENTIAL_NUMBER.value,  # Corrected from VAR_SEQUENTIAL_NUMBER
            TypeOfLabelEnum.KRAFT_PAPER.value,  # Corrected, was "Kraft Paper"
            TypeOfLabelEnum.VAR_ASSET_TAG.value,
        ]:
            return True
        if pg_val == ProductGroupEnum.STICKER.value and tos_val in [
            TypeOfStickerEnum.MINI_PAGES.value,
            TypeOfStickerEnum.SCRATCH_SNIFF.value,
        ]:
            return True
        if (
            pg_val == ProductGroupEnum.STICKER.value
            and tos_val == TypeOfStickerEnum.REMOVABLE_SMART_SAVE.value
            and tq is not None
            and tq >= 500
        ):
            return True
        if pg_val == ProductGroupEnum.TATTOO.value and tot_val in [
            TypeOfTattooEnum.GLOW_IN_DARK.value,
            TypeOfTattooEnum.GLITTER.value,
            TypeOfTattooEnum.METALLIC_FOIL.value,
        ]:
            return True
        if (
            pg_val == ProductGroupEnum.STICKER.value
            and pf_val == PreferredFormatEnum.PAGES.value
            and tq is not None
            and tq > 500
        ):
            return True
        if (
            pg_val == ProductGroupEnum.ROLL_LABEL.value
            and tq is not None
            and tq > 40000
        ):
            return True
        if (
            pg_val == ProductGroupEnum.STICKER.value
            and pf_val == PreferredFormatEnum.DIE_CUT_SINGLES.value
            and tos_val
            in [
                TypeOfStickerEnum.REMOVABLE_WHITE_VINYL.value,
                TypeOfStickerEnum.PERMANENT_WHITE_VINYL.value,
                TypeOfStickerEnum.CLEAR_VINYL.value,
            ]
            and tq is not None
            and tq > 20000
        ):
            return True
        if (
            pg_val == ProductGroupEnum.STICKER.value
            and tos_val == TypeOfStickerEnum.HOLOGRAPHIC.value
            and tq is not None
            and tq > 2000
        ):
            return True
        if (
            pg_val == ProductGroupEnum.STICKER.value
            and pf_val == PreferredFormatEnum.DIE_CUT_SINGLES.value
            and tos_val
            in [TypeOfStickerEnum.GLITTER.value, TypeOfStickerEnum.ECO_SAFE.value]
            and tq is not None
            and tq > 5000
        ):
            return True
        if (
            pg_val == ProductGroupEnum.STICKER.value
            and pf_val == PreferredFormatEnum.KISS_CUT_SINGLES.value
            and tos_val
            in [
                TypeOfStickerEnum.REMOVABLE_WHITE_VINYL.value,
                TypeOfStickerEnum.MATTE_WHITE_VINYL.value,
            ]
            and tq is not None
            and tq > 20000
        ):
            return True
        if (
            pg_val == ProductGroupEnum.STICKER.value
            and pf_val == PreferredFormatEnum.KISS_CUT_SINGLES.value
            and tos_val == TypeOfStickerEnum.CLEAR_VINYL.value
            and tq is not None
            and tq > 2000
        ):
            return True
        if (
            pg_val in [ProductGroupEnum.STICKER.value, ProductGroupEnum.DECAL.value]
            and pf_val
            in [
                PreferredFormatEnum.KISS_CUT_SINGLES.value,
                PreferredFormatEnum.DIE_CUT_SINGLES.value,
            ]
            and tos_val
            == TypeOfStickerEnum.UV_DTF_TRANSFER_STICKER.value  # This is TypeOfStickerEnum but used for Decals too
            and tq is not None
            and tq > 1000
        ):
            return True
        if (
            pg_val == ProductGroupEnum.DECAL.value
            and tode_val
            in [
                TypeOfDecalEnum.INDOOR_FLOOR_VINYL.value,
                TypeOfDecalEnum.INDOOR_WALL_VINYL.value,
            ]
            and tq is not None
            and tq > 50
        ):
            return True
        if (
            pg_val == ProductGroupEnum.DECAL.value
            and tode_val == TypeOfDecalEnum.CLEAR_WINDOW.value
            and tq is not None
            and tq > 500
        ):
            return True
        if (
            pg_val == ProductGroupEnum.TATTOO.value
            and pf_val == PreferredFormatEnum.PAGES.value
            and tq is not None
            and tq > 2000
        ):
            return True
        if (
            pg_val == ProductGroupEnum.TATTOO.value
            and pf_val
            in [
                PreferredFormatEnum.KISS_CUT_SINGLES.value,
                PreferredFormatEnum.DIE_CUT_SINGLES.value,
            ]
            and tq is not None
            and tq > 5000
        ):
            return True
        if pg_val == ProductGroupEnum.IRON_ON.value and tq is not None and tq > 500:
            return True
        if pg_val == ProductGroupEnum.MAGNET.value and tq is not None and tq > 2000:
            return True
        if (
            pg_val == ProductGroupEnum.PATCH.value
            and topa_val == TypeOfPatchEnum.PRINTED.value
            and tq is not None
            and tq > 500
        ):
            return True
        if pg_val == ProductGroupEnum.CLING.value and tq is not None and tq > 500:
            return True
        if pg_val == ProductGroupEnum.BADGE.value and tq is not None and tq > 250:
            return True
        if pg_val == ProductGroupEnum.PACKAGING.value and tq is not None and tq > 2500:
            return True
        if (
            pg_val == ProductGroupEnum.STICKER.value
            and tos_val == TypeOfStickerEnum.PERMANENT_GLOW_DIE_CUT.value
            and pf_val == PreferredFormatEnum.DIE_CUT_SINGLES.value
            and tq is not None
            and tq > 2000
        ):
            return True
        if (
            pg_val == ProductGroupEnum.TATTOO.value
            and tot_val == TypeOfTattooEnum.WHITE_INK.value
            and tq is not None
            and tq > 1000
        ):
            return True

    return False


def determine_pipeline_and_stage(
    properties: TicketCreationProperties,
) -> Tuple[str, str]:
    """
    Determines the HubSpot pipeline and stage based on ticket properties.
    Returns a tuple of (pipeline_id, pipeline_stage_id).
    """
    if _is_promo_reseller_ticket(properties):
        return HUBSPOT_PIPELINE_ID_PROMO_RESELLER, HUBSPOT_PR_STAGE_ID

    if _is_assisted_sales_ticket(properties):
        return HUBSPOT_PIPELINE_ID_ASSISTED_SALES, HUBSPOT_AS_STAGE_ID

    # Fallback for general "Quote" type if not caught by specific Assisted Sales rules
    if properties.type_of_ticket == TypeOfTicketEnum.QUOTE:
        return HUBSPOT_PIPELINE_ID_ASSISTED_SALES, HUBSPOT_AS_STAGE_ID

    # Default if no other conditions are met
    # Use pipeline/stage from properties if provided, otherwise default to Support.
    default_pipeline = (
        properties.hs_pipeline
        if properties.hs_pipeline is not None
        else HUBSPOT_PIPELINE_ID_SUPPORT
    )
    default_stage = (
        properties.hs_pipeline_stage
        if properties.hs_pipeline_stage is not None
        else HUBSPOT_SUPPORT_STAGE_ID
    )

    # Ensure that if a custom pipeline is provided, its corresponding default stage is also considered if not provided.
    # This logic might need refinement based on how hs_pipeline and hs_pipeline_stage are expected to be coupled
    # when passed in `properties`. For now, if one is None, use the system default for that part.
    if default_pipeline == HUBSPOT_PIPELINE_ID_SUPPORT and (
        properties.hs_pipeline_stage is None
    ):
        default_stage = HUBSPOT_SUPPORT_STAGE_ID
    elif default_pipeline == HUBSPOT_PIPELINE_ID_ASSISTED_SALES and (
        properties.hs_pipeline_stage is None
    ):
        default_stage = HUBSPOT_AS_STAGE_ID
    elif default_pipeline == HUBSPOT_PIPELINE_ID_PROMO_RESELLER and (
        properties.hs_pipeline_stage is None
    ):
        default_stage = HUBSPOT_PR_STAGE_ID
    # If properties.hs_pipeline is something else custom, and hs_pipeline_stage is None,
    # it will use the HUBSPOT_SUPPORT_STAGE_ID as a fallback, which might not be ideal.

    return default_pipeline, default_stage
