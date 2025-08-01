"""
Defines constants and Pydantic models for the unified order status tool.
"""
from typing import Optional
from pydantic import BaseModel, Field

# --- User-Friendly Messages for Internal Order Statuses ---

INTERNAL_STATUS_MESSAGES = {
    "Approved": "Your order has been received and is being prepared for printing.",
    "Printed": "Your order has been successfully printed! It's now being prepared for shipment and will be on its way to you very soon.",
    "Placed": "Your order has been successfully placed and is currently awaiting approval from our team.",
    "OnHold": "Your order is currently on hold. Our team may need to review it, and will contact you if any action is needed.",
    "Cancelled": "This order has been cancelled in our system.",
    "Declined": "Unfortunately, your order has been declined. Please contact our customer support team for more information.",
    "Deleted": "This order has been deleted from our system.",
    "Error": "There appears to be an error with your order.",
    "BeingFixed": "Our team is currently addressing an issue with your order to ensure it's perfect. We appreciate your patience.",
    # 'Finalized' is handled by the WismoLabs response, so it doesn't need a default message here.
}

# --- Unified Response DTO ---

class UnifiedOrderStatusResponse(BaseModel):
    """
    A standardized response model that the unified order status tool will always return.
    This provides a consistent structure for the Planner Agent to interpret.
    """
    order_id: str = Field(..., alias="orderId")
    status: str
    status_details: str = Field(..., alias="statusDetails")
    tracking_number: Optional[str] = Field(None, alias="trackingNumber")
    last_update: Optional[str] = Field(None, alias="lastUpdate")

    model_config = {
        "populate_by_name": True, # Allows using aliases like 'orderId'
        "extra": "ignore",
    }