"""Defines Pydantic models specifically for StickerYou API **request** bodies / payloads."""

# src/tools/sticker_api/requests.py

from typing import List, Optional
from pydantic import BaseModel, Field

from src.tools.sticker_api.dtos.common import (
    AccessoryOption,
    OrderItemBase,
    OrderStatusId,
    ShipToAddress,
)


class OrderItemCreate(OrderItemBase):
    """Represents an item structure specifically for creating a new order via sy_create_order (POST /v1/Orders/new). Inherits common fields from OrderItemBase."""

    # Fields inherited from OrderItemBase: itemIdentifier, notes, price, quantity, accessoryOptions
    # Fields specific to this request type:
    productId: int = Field(
        description="The product ID provided by StickerYou. Required."
    )
    width: float = Field(description="The width of the product in inches. Required.")
    height: float = Field(description="The height of the product in inches. Required.")
    artworkUrl: str = Field(
        description="URL pointing to the artwork file (PDF) for this item. Required."
    )
    # Ensure required fields from base are handled by caller or have defaults if applicable
    itemIdentifier: str = Field(
        description="Client-defined identifier for the item. Required."
    )  # Re-declare as non-optional for this specific type
    price: float = Field(
        description="The total price for the specified quantity of this item. Required."
    )  # Re-declare as non-optional
    quantity: int = Field(
        description="The number of units for this order item. Required."
    )  # Re-declare as non-optional


class OrderItemCreateDesign(OrderItemBase):
    """Represents an item structure specifically for creating a new order from existing designs via sy_create_order_from_designs (POST /v1/Orders/designs/new). Inherits common fields from OrderItemBase."""

    # Fields inherited from OrderItemBase: itemIdentifier, notes, price, quantity, accessoryOptions
    # Fields specific to this request type:
    designId: str = Field(
        description="The unique identifier of the pre-uploaded design to be used for this item. Required."
    )
    # Ensure required fields from base are handled by caller or have defaults if applicable
    itemIdentifier: str = Field(
        description="Client-defined identifier for the item. Required."
    )  # Re-declare as non-optional
    price: float = Field(
        description="The total price for the specified quantity of this item. Required."
    )  # Re-declare as non-optional
    quantity: int = Field(
        description="The number of units for this order item. Required."
    )  # Re-declare as non-optional


# --- Request Body Models --- #


class LoginRequest(BaseModel):
    """Request body model for sy_perform_login (POST /users/login). Based on Swagger's LoginModel."""

    userName: str = Field(description="The username for API authentication.")
    password: str = Field(description="The password for API authentication.")


class SpecificPriceRequest(BaseModel):
    """Request body structure for sy_get_specific_price and sy_get_price_tiers (POST /api/v1/Pricing/{productId}/pricing|pricings). Based on Swagger's ProductPricingRequest."""

    width: float = Field(
        description="The desired width of the product in inches (Min: 0)."
    )
    height: float = Field(
        description="The desired height of the product in inches (Min: 0)."
    )
    countryCode: Optional[str] = Field(
        None,
        description="Optional two-letter ISO country code (e.g., 'US', 'CA') for accurate pricing/shipping (defaults to config).",
    )
    quantity: Optional[int] = Field(
        None,
        description="The specific quantity required (mandatory for /pricing, optional for /pricings).",
    )
    currencyCode: Optional[str] = Field(
        None,
        description="Optional ISO currency code (e.g., 'USD', 'CAD') (defaults to config).",
    )
    accessoryOptions: Optional[List[AccessoryOption]] = Field(
        None, description="Optional list of selected accessory options."
    )  # Uses imported AccessoryOption


class CreateOrderRequest(BaseModel):
    """Request body model for sy_create_order (POST /v1/Orders/new), creating an order with full item details. Based on Swagger's Order model."""

    orderIdentifier: str = Field(
        description="Client-defined identifier for the order. Required."
    )
    orderDate: str = Field(
        description="Order date in ISO 8601 format string (e.g., 'YYYY-MM-DDTHH:MM:SSZ'). Required."
    )
    shipTo: ShipToAddress = Field(
        description="The shipping address details. Required."
    )  # Uses imported ShipToAddress
    orderTotal: float = Field(
        description="Total amount for the order (e.g., in USD). Required."
    )
    notes: Optional[str] = Field(
        None, description="Optional notes for the entire order."
    )
    items: List[OrderItemCreate] = Field(
        description="A list of items to include in the order, providing full product details."
    )  # Uses derived OrderItemCreate


class CreateOrderFromDesignsRequest(BaseModel):
    """Request body model for sy_create_order_from_designs (POST /v1/Orders/designs/new), creating an order using pre-uploaded design IDs. Based on Swagger's OrderDesign model."""

    orderIdentifier: str = Field(
        description="Client-defined identifier for the order. Required."
    )
    orderDate: str = Field(
        description="Order date in ISO 8601 format string (e.g., 'YYYY-MM-DDTHH:MM:SSZ'). Required."
    )
    shipTo: ShipToAddress = Field(
        description="The shipping address details. Required."
    )  # Uses imported ShipToAddress
    orderTotal: float = Field(
        description="Total amount for the order (e.g., in USD). Required."
    )
    notes: Optional[str] = Field(
        None, description="Optional notes for the entire order."
    )
    items: List[OrderItemCreateDesign] = Field(
        description="A list of items to include in the order, referencing existing design IDs."
    )  # Uses derived OrderItemCreateDesign


class ListOrdersByStatusRequest(BaseModel):
    """Request body model for sy_list_orders_by_status_post (POST /v1/Orders/status/list). Based on Swagger's OrdersByStatusRequest."""

    take: int = Field(
        100, description="The maximum number of orders to retrieve (pagination limit)."
    )
    skip: int = Field(
        0, description="The number of orders to skip (pagination offset)."
    )
    status: OrderStatusId = Field(
        description="The status ID (from OrderStatusId enum) to filter orders by. Required."
    )
