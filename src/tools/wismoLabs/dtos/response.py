""" This module contains the response DTOs for the WismoLabs API. """
from typing import List
from pydantic import BaseModel, Field

# --- Auth Response DTO ---

class WismoAuthResponse(BaseModel):
    """
    Represents the successful response from the WismoLabs auth endpoint.
    """
    message: str
    token: str

# --- Order Status v1 Response DTOs ---

class WismoShipmentDates(BaseModel):
    """Represents the date fields within a shipment."""
    order_date: str = Field(..., alias="orderDate")
    shipped_date: str = Field(..., alias="shippedDate")
    delivered_date: str = Field(..., alias="deliveredDate")
    eta: str
    eta_begin: str = Field(..., alias="etaBegin")
    eta_end: str = Field(..., alias="etaEnd")

    model_config = {
        "populate_by_name": True,
        "extra": "ignore",
    }


class WismoShipmentDetails(BaseModel):
    """Represents a single shipment within the order status response."""
    tracking_number: str = Field(..., alias="trackingNumber")
    carrier: str
    carrier_code: str = Field(..., alias="carrierCode")
    status: str
    status_code: str = Field(..., alias="statusCode")
    status_details: str = Field(..., alias="statusDetails")
    last_update: str = Field(..., alias="lastUpdate")
    dates: WismoShipmentDates

    model_config = {
        "populate_by_name": True,
        "extra": "ignore",
    }


class WismoCustomerDetails(BaseModel):
    """Represents the customer details in the order status response."""
    first_name: str = Field(..., alias="firstName")
    email: str

    model_config = {
        "populate_by_name": True,
        "extra": "ignore",
    }


class WismoOrderStatusResponse(BaseModel):
    """
    The root object for the WismoLabs v1/order-status API response.
    """
    order_id: str = Field(..., alias="orderId")
    tracking_url: str = Field(..., alias="trackingUrl")
    customer: WismoCustomerDetails
    order_date: str = Field(..., alias="orderDate")
    shipments: List[WismoShipmentDetails]

    model_config = {
        "populate_by_name": True,
        "extra": "ignore",
    }
