"""
Tools for interacting with the WismoLabs API for order tracking.
"""

# /src/tools/wismoLabs/orders.py

from typing import Optional, Dict, List
from urllib.parse import urlencode
import httpx
from pydantic import ValidationError

# Import the new, detailed response model
from src.tools.wismoLabs.dtos.response import WismoApiResponse, Activity
import config

WISMO_ORDER_TOOL_ERROR_PREFIX = "WISMO_ORDER_TOOL_FAILED:"


async def get_order_status_by_details(
    order_id: Optional[str] = None,
    tracking_number: Optional[str] = None,
    customer_name: Optional[str] = None,
    page_size: int = 1,  # Default to returning only the LATEST activity
) -> Dict | str:
    """
    Searches WismoLabs for an order and returns a simplified summary. The number
    of recent activities returned is controlled by the page_size parameter.

    Args:
        order_id: The order ID to search for.
        tracking_number: The tracking number to search for.
        customer_name: The customer's name to search for.
        page_size: The number of recent activities to return. Defaults to 1.
                   Use a larger number (e.g., 5) for a more detailed history.

    Returns:
        A simplified dictionary with key order details on success, or an error string.
    """
    if not any([order_id, tracking_number, customer_name]):
        return f"{WISMO_ORDER_TOOL_ERROR_PREFIX} At least one of the following must be provided: order_id, tracking_number, or customer_name."

    params = {"ON": order_id, "TRK": tracking_number, "NAME": customer_name}
    query_params = {k: v for k, v in params.items() if v is not None}

    if not config.WISMOLABS_API_URL:
        return f"{WISMO_ORDER_TOOL_ERROR_PREFIX} WismoLabs API URL is not configured."

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(config.WISMOLABS_API_URL, params=query_params)
            response.raise_for_status()
            wismo_response = WismoApiResponse.model_validate(response.json())

            if wismo_response.data.errors:
                error_message = (
                    str(wismo_response.data.errors[0])
                    if wismo_response.data.errors
                    else "Unknown API error"
                )
                return f"{WISMO_ORDER_TOOL_ERROR_PREFIX} {error_message}"

            if not wismo_response.data.activities:
                return f"{WISMO_ORDER_TOOL_ERROR_PREFIX} No order found matching the provided details."

            # Slice the activities based on the requested page_size
            activities_to_return = wismo_response.data.activities[:page_size]
            activity_dicts = [
                activity.model_dump(by_alias=True) for activity in activities_to_return
            ]

            # Gather all known parameters for the link. Note that customer_name comes from the function input, not the API response.
            link_params = {
                "TRK": wismo_response.data.tracking_number,
                "ON": wismo_response.data.order_number,
                "Name": customer_name,
            }

            # Filter out any parameters that are None or empty.
            valid_link_params = {k: v for k, v in link_params.items() if v}

            # Use urlencode to safely build the query string.
            query_string = urlencode(valid_link_params)

            # Construct the final, clean URL.
            tracking_link = (
                f"{config.WISMOLABS_CONSULT_URL}?{query_string}"
                if query_string
                else config.WISMOLABS_CONSULT_URL
            )

            # Assemble the final, simplified dictionary
            simplified_result = {
                "orderId": wismo_response.data.order_number,
                "trackingNumber": wismo_response.data.tracking_number,
                "trackingLink": tracking_link,
                "carrierName": wismo_response.data.carrier_name,
                "statusSummary": wismo_response.data.status_desc,
                "activities": activity_dicts,  # This will contain 1 or more activities
            }

            return simplified_result

        except httpx.HTTPStatusError as e:
            return f"{WISMO_ORDER_TOOL_ERROR_PREFIX} API request failed with status {e.response.status_code}."
        except (ValidationError, Exception) as e:
            return f"{WISMO_ORDER_TOOL_ERROR_PREFIX} An unexpected error occurred: {e}"
