from typing import Tuple

from src.tools.hubspot.tickets.dto_requests import TicketCreationProperties
from src.tools.hubspot.tickets.constants import TypeOfTicketEnum
from config import (
    HUBSPOT_PIPELINE_ID_SUPPORT,
    HUBSPOT_SUPPORT_STAGE_ID,
    HUBSPOT_PIPELINE_ID_ASSISTED_SALES,
    HUBSPOT_AS_STAGE_ID,
    HUBSPOT_PIPELINE_ID_PROMO_RESELLER,
    HUBSPOT_PR_STAGE_ID,
)


def _is_promo_reseller_ticket(properties: TicketCreationProperties) -> bool:
    """Determines if the ticket should go to the Promo Reseller pipeline."""
    promo_value = properties.promotional_product_distributor_
    if isinstance(promo_value, str):
        return promo_value.lower() in ["true", "yes"]
    return bool(promo_value)


def determine_pipeline_and_stage(
    properties: TicketCreationProperties,
) -> Tuple[str, str]:
    """
    Determines the HubSpot pipeline and stage based on ticket properties.
    - If the ticket is for a promotional reseller, it goes to the Promo Reseller pipeline.
    - If the ticket is a Quote, it defaults to the Assisted Sales pipeline.
    - Otherwise, it defaults to the Support pipeline.
    Returns a tuple of (pipeline_id, pipeline_stage_id).
    """
    if _is_promo_reseller_ticket(properties):
        return HUBSPOT_PIPELINE_ID_PROMO_RESELLER, HUBSPOT_PR_STAGE_ID

    if properties.type_of_ticket == TypeOfTicketEnum.QUOTE:
        return HUBSPOT_PIPELINE_ID_ASSISTED_SALES, HUBSPOT_AS_STAGE_ID

    # Default for all other ticket types is the Support pipeline.
    return HUBSPOT_PIPELINE_ID_SUPPORT, HUBSPOT_SUPPORT_STAGE_ID
