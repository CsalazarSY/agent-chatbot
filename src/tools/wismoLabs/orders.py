"""
Mock tools for interacting with a WismoLabs-like API for order tracking.
"""

# /src/tools/wismoLabs/orders.py

from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field

WISMO_ORDER_TOOL_ERROR_PREFIX = "WISMO_ORDER_TOOL_FAILED:"

# --- Data Transfer Objects (DTOs) ---


class WismoOrderData(BaseModel):
    """Represents the structure of the mock order data."""

    customer_name: str = Field(..., alias="customerName")
    email: str
    tracking_number: str = Field(..., alias="trackingNumber")
    status_summary: str = Field(..., alias="statusSummary")
    order_id: str = Field(..., alias="orderId")
    tracking_link: str = Field(..., alias="trackingLink")

    model_config = {
        "populate_by_name": True,
        "extra": "ignore",
    }


class WismoOrderStatusResponse(BaseModel):
    """Response model when an order is found."""

    order_id: str = Field(..., alias="orderId")
    customer_name: str = Field(..., alias="customerName")
    email: str
    tracking_number: str = Field(..., alias="trackingNumber")
    status_summary: str = Field(..., alias="statusSummary")
    tracking_link: str = Field(..., alias="trackingLink")
    message: str = "Order found."

    model_config = {"populate_by_name": True}


# --- Mock Data Store ---

MOCK_ORDER_DATABASE: List[WismoOrderData] = [
    WismoOrderData(
        customerName="Elliot Walters",
        email="elliot.walters@shopify.com",
        trackingNumber="410665048309",
        statusSummary="Delivered on Monday, April 21",
        orderId="2503181923260992401",
        trackingLink="https://app.wismolabs.com/stickeryou/tracking?TRK=410665048309&ON=84686083&Name=Elliot",
    ),
    WismoOrderData(
        customerName="Kristi Allen",
        email="kristi.allen@proforma.com",
        trackingNumber="410665047622",
        statusSummary="Delivered on Wednesday, March 19",
        orderId="2503112111546482924",
        trackingLink="https://app.wismolabs.com/stickeryou/tracking?TRK=410665047622&ON=84686083&Name=Kristi",
    ),
    WismoOrderData(
        customerName="Patrick Ganino",
        email="pganino@gmail.com",
        trackingNumber="880312555814",
        statusSummary="Delivered on Friday, May 2",
        orderId="2503291511551367931",
        trackingLink="https://app.wismolabs.com/stickeryou/tracking?TRK=880312555814&ON=84686083&Name=Patrick",
    ),
]

# --- Tool Implementation ---


async def get_order_status_by_details(
    order_id: Optional[str] = None,
    tracking_number: Optional[str] = None,
    email: Optional[str] = None,
    customer_name: Optional[
        str
    ] = None,  # Added for completeness, though might be less reliable for unique match
) -> Union[WismoOrderStatusResponse, str]:
    """
    Searches the mock order database for an order matching the provided details.
    Returns order status information if a unique match is found, otherwise an error string.

    Args:
        order_id: The order ID to search for.
        tracking_number: The tracking number to search for.
        email: The customer's email address to search for.
        customer_name: The customer's name to search for.

    Returns:
        A WismoOrderStatusResponse object if a unique match is found, or an error string
        prefixed with WISMO_ORDER_TOOL_ERROR_PREFIX.
    """
    if not any([order_id, tracking_number, email, customer_name]):
        return f"{WISMO_ORDER_TOOL_ERROR_PREFIX} At least one search parameter (order_id, tracking_number, email, or customer_name) must be provided."

    found_orders: List[WismoOrderData] = []

    for order in MOCK_ORDER_DATABASE:
        match = False
        if order_id and order.order_id == order_id:
            match = True
        elif tracking_number and order.tracking_number == tracking_number:
            match = True
        elif email and order.email.lower() == email.lower():
            match = True
        elif customer_name and order.customer_name.lower() == customer_name.lower():
            # Name matching can be ambiguous, but included for now
            match = True

        if match:
            found_orders.append(order)

    if not found_orders:
        return f"{WISMO_ORDER_TOOL_ERROR_PREFIX} No order found matching the provided details."

    if len(found_orders) > 1:
        # This case might happen if searching by a non-unique field like customer_name,
        # or if the mock data had duplicates.
        # For a real API, we'd expect more specific lookups.
        return f"{WISMO_ORDER_TOOL_ERROR_PREFIX} Multiple orders found matching the details. Please provide more specific information (e.g., Order ID or Tracking Number)."

    # Unique match found
    matched_order = found_orders[0]
    return WismoOrderStatusResponse(
        orderId=matched_order.order_id,
        customerName=matched_order.customer_name,
        email=matched_order.email,
        trackingNumber=matched_order.tracking_number,
        statusSummary=matched_order.status_summary,
        trackingLink=matched_order.tracking_link,
    )
