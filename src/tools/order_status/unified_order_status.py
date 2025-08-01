"""
This module provides a unified tool to get order status, checking the internal
StickerYou API first and then delegating to WismoLabs if the order is finalized.
"""
from typing import Dict
from src.services.logger_config import log_message

# --- First Party Imports ---
from src.tools.sticker_api.sy_api import sy_get_internal_order_status
from src.tools.sticker_api.dtos.responses import SYOrderStatusResponse
from src.tools.wismoLabs.orders import get_wismo_order_status
from src.tools.order_status.dtos.responses import (
    INTERNAL_STATUS_MESSAGES,
    UnifiedOrderStatusResponse,
)

# --- Constants ---
UNIFIED_TOOL_ERROR_PREFIX = "UNIFIED_ORDER_TOOL_FAILED:"

# --- Public Unified Tool Function ---
async def get_unified_order_status(order_id: str) -> Dict:
    """
    Retrieves a comprehensive order status, returning a standardized dictionary.

    It checks the internal API first. If the status is 'Finalized', it fetches
    detailed tracking from WismoLabs. Otherwise, it formats the internal status
    into the same standardized response model.

    Args:
        order_id: The unique identifier for the order.

    Returns:
        A dictionary conforming to the UnifiedOrderStatusResponse model.
        On failure, returns a dictionary with 'status': 'Error' and a descriptive message.
    """
    if not order_id:
        return {
            "orderId": order_id or "Unknown",
            "status": "Error",
            "statusDetails": f"{UNIFIED_TOOL_ERROR_PREFIX} An Order ID must be provided.",
            "trackingNumber": None,
            "lastUpdate": None,
        }

    # --- Step 1: Check the internal API ---
    internal_result = await sy_get_internal_order_status(order_id)

    # Handle structured failure from the internal tool
    if isinstance(internal_result, dict) and internal_result.get("status") == "failed":
        return {
            "orderId": order_id,
            "status": "Error",
            "statusDetails": internal_result.get("message", "An unknown error occurred."),
            "trackingNumber": None,
            "lastUpdate": None,
        }

    # --- Step 2: Process the result ---
    if isinstance(internal_result, SYOrderStatusResponse):
        internal_status = internal_result.status

        # --- Case A: Order is Finalized -> Get WismoLabs Details ---
        if internal_status == "Finalized":
            wismo_result = await get_wismo_order_status(order_id)

            if isinstance(wismo_result, dict) and 'shipments' in wismo_result:
                # Successfully fetched from WismoLabs, now map to our unified model
                shipment = wismo_result['shipments'][0] if wismo_result['shipments'] else {}
                unified_response = UnifiedOrderStatusResponse(
                    orderId=wismo_result.get("orderId", order_id),
                    status=shipment.get("status"),
                    statusDetails=shipment.get("statusDetails"),
                    trackingNumber=shipment.get("trackingNumber"),
                    lastUpdate=shipment.get("lastUpdate"),
                )
                final_result = unified_response.model_dump(by_alias=True)
                return final_result
            else:
                # Wismo call failed, return a structured error
                error_msg = str(wismo_result) # Convert potential error string to message
                return {
                    "orderId": order_id,
                    "status": "Error",
                    "statusDetails": f"{UNIFIED_TOOL_ERROR_PREFIX} Order is Finalized, but failed to get tracking details. Error: {error_msg}",
                    "trackingNumber": None,
                    "lastUpdate": None,
                }

        # --- Case B: Order is in a normal internal state ---
        else:
            status_details = INTERNAL_STATUS_MESSAGES.get(internal_status, "Your order is currently being processed.")
            unified_response = UnifiedOrderStatusResponse(
                orderId=order_id,
                status=internal_status,
                statusDetails=status_details,
                trackingNumber=None, # No tracking yet
                lastUpdate=None,      # No last update from internal API
            )
            final_result = unified_response.model_dump(by_alias=True)
            return final_result

    # Fallback for unexpected type from internal tool
    return {
        "orderId": order_id,
        "status": "Error",
        "statusDetails": f"{UNIFIED_TOOL_ERROR_PREFIX} Unexpected response type from internal API tool.",
        "trackingNumber": None,
        "lastUpdate": None,
    }