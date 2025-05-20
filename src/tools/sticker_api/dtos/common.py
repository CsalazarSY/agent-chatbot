"""""Defines common Pydantic models and enums shared between StickerYou API requests and responses."""
# src/tools/sticker_api/common.py

from typing import List, Optional
from enum import IntEnum
from pydantic import BaseModel, Field

# --- Enums --- #

class OrderStatusId(IntEnum):
    """Enum for StickerYou Order Status IDs, used in various requests and responses."""
    CANCELLED = 1
    ERROR = 2
    NEW = 10
    ACCEPTED = 20
    INPROGRESS = 30
    ONHOLD = 40
    PRINTED = 50
    SHIPPED = 100

# --- Common Reusable Models --- #

class AccessoryOption(BaseModel):
    """Represents an accessory option for a product, used in pricing and order requests/responses."""
    accessoryId: int = Field(description="The unique identifier for the accessory.")
    quantity: int = Field(description="The quantity of this accessory.")
    # Fields often present in responses, optional in requests
    price: Optional[float] = Field(None, description="The total price for this quantity of the accessory (required in some responses).")
    name: Optional[str] = Field(None, description="The display name of the accessory (often present in responses).")
    pricePerItem: Optional[float] = Field(None, description="The price per individual item of the accessory (often present in responses).")
    currencyCode: Optional[str] = Field(None, description="The currency code for the accessory price (e.g., 'USD') (often present in responses).")

class ShipToAddress(BaseModel):
    """Represents the shipping address details used in order creation requests and returned in order details."""
    firstname: str = Field(description="Recipient's first name (Max Length: 50). Required for creation.")
    lastname: str = Field(description="Recipient's last name (Max Length: 50). Required for creation.")
    company: Optional[str] = Field(None, description="Recipient's company name, if applicable (Max Length: 50).")
    email: str = Field(description="Recipient's email address. Required for creation.", pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    phone: Optional[str] = Field(None, description="Recipient's phone number.")
    addressLine1: str = Field(description="Primary address line (Max Length: 35). Required.")
    addressLine2: Optional[str] = Field(None, description="Secondary address line (e.g., apartment, suite) (Max Length: 35).")
    city: str = Field(description="City name. Required.")
    stateProvince: str = Field(description="State or province code/name. Required for creation.") # Required for creation, might be optional in some responses but keep as required here.
    zipPostalCode: str = Field(description="ZIP or postal code. Required.")
    countryCode: str = Field(description="Two-letter ISO country code (e.g., 'US', 'CA'). Required.")

class OrderItemBase(BaseModel):
    """Base model containing common fields for items within an order, used across requests and responses."""
    # Common across requests & responses (though sometimes optional)
    itemIdentifier: Optional[str] = Field(None, description="Client-defined identifier for the item (required in CreateOrderRequest).")
    notes: Optional[str] = Field(None, description="Optional notes specific to this order item.")
    price: Optional[float] = Field(None, description="The total price for the specified quantity of this item (required in CreateOrderRequest, may be per unit in responses).")
    quantity: Optional[int] = Field(None, description="The number of units for this order item (required in CreateOrderRequest).")
    accessoryOptions: Optional[List[AccessoryOption]] = Field(None, description="List of selected accessory options for this item.")

    # Primarily used in responses or specific request types
    orderItemIdentifier: Optional[str] = Field(None, description="API-defined identifier for the order item (returned in responses/status).")
    productId: Optional[int] = Field(None, description="The product ID provided by StickerYou (used when not creating from a design).")
    width: Optional[float] = Field(None, description="The width of the item in inches (used when not creating from a design).")
    height: Optional[float] = Field(None, description="The height of the item in inches (used when not creating from a design).")
    artworkUrl: Optional[str] = Field(None, description="URL to the artwork image/PDF (used when not creating from a design).")
    designId: Optional[str] = Field(None, description="The unique identifier of a pre-uploaded design (used in CreateOrderFromDesignsRequest).") # Added from OrderItemCreateDesign

    # Primarily for responses/status:
    reason: Optional[str] = Field(None, description="Reason text, often associated with specific statuses like 'Error' or 'OnHold'.")
    statusId: Optional[int] = Field(None, description="Numerical status ID of the order item (maps to OrderStatusId enum).")
    status: Optional[str] = Field(None, description="Textual description of the order item status.") 