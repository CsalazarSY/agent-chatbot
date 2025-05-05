"""Defines Pydantic models for StickerYou API **responses** and common types."""

# src/tools/sticker_api/dto_responses.py

from typing import List, Optional
from pydantic import BaseModel, Field, RootModel

# Import common models
from src.tools.sticker_api.dtos.common import (
    AccessoryOption,
    ShipToAddress,
    OrderItemBase,
)


# --- Response Models --- #
class LoginResponse(BaseModel):
    """Response body model for a successful sy_perform_login (POST /users/login)."""

    token: str = Field(
        description="The authentication token to be used for subsequent API calls."
    )
    expirationMinutes: str = Field(
        description="The duration in minutes for which the token is valid (provided as a string)."
    )


class LoginStatusResponse(BaseModel):
    """Response body model for sy_verify_login (GET /users/login), indicating current token validity. Based on Swagger's LoggedUserModel."""

    name: str = Field(
        description="The name associated with the authenticated user/token."
    )
    authenticated: bool = Field(
        description="Boolean flag indicating if the current token is valid."
    )


class Country(BaseModel):
    """Represents a single country supported by the API."""

    code: str = Field(description="The two-letter ISO country code.")
    name: str = Field(description="The full name of the country.")


class CountriesResponse(BaseModel):
    """Response body model for sy_list_countries (POST /api/v1/Pricing/countries)."""

    countries: List[Country] = Field(
        description="A list of supported countries with their codes and names."
    )


class ShippingMethod(BaseModel):
    """Represents a shipping method available for an order or quote."""

    id: int = Field(description="Unique identifier for the shipping method.")
    name: str = Field(description="Display name of the shipping method.")
    price: float = Field(description="Cost of this shipping method.")
    deliveryEstimate: int = Field(
        description="Estimated delivery time in business days."
    )


class PriceTier(BaseModel):
    """Represents a single quantity-based price tier within a pricing response (e.g., within ProductPricing's priceTiers list)."""

    quantity: int = Field(description="The quantity threshold for this price tier.")
    price: float = Field(description="The total price for this quantity tier.")
    # Add other relevant tier fields if known, e.g., pricePerSticker


class ProductPricing(BaseModel):
    """Contains detailed pricing information returned by pricing endpoints. Used in SpecificPriceResponse and PriceTiersResponse. Maps to Swagger's ProductPricing."""

    quantity: Optional[int] = Field(
        None,
        description="The specific quantity priced (present in specific price responses).",
    )
    unitMeasure: Optional[str] = Field(
        None, description="The unit of measurement (e.g., 'Stickers')."
    )
    price: float = Field(description="The calculated total price.")
    pricePerSticker: Optional[float] = Field(
        None, description="Calculated price per individual sticker, if applicable."
    )
    stickersPerPage: Optional[int] = Field(
        None,
        description="Number of stickers that fit on a single page/sheet, if applicable.",
    )
    currency: str = Field(
        description="ISO currency code for the price (e.g., 'USD', 'CAD')."
    )
    shippingMethods: Optional[List[ShippingMethod]] = Field(
        [], description="List of available shipping methods and their costs/estimates."
    )
    accessories: Optional[List[AccessoryOption]] = Field(
        [],
        description="List of available accessories for the product. Maps to Swagger's Accessory model.",
    )  # Uses imported AccessoryOption
    priceTiers: Optional[List[PriceTier]] = Field(
        None,
        description="List of price tiers showing price variations by quantity (present in PriceTiersResponse, representing Swagger's ProductPricingGridResponse structure).",
    )


class SpecificPriceResponse(BaseModel):
    """Response body model for sy_get_specific_price (POST /api/v1/Pricing/{productId}/pricing). Based on Swagger's ProductPricingResponse."""

    productPricing: ProductPricing = Field(
        description="Contains the calculated pricing details for the specific quantity requested."
    )


class PriceTiersResponse(BaseModel):
    """Response body model for sy_get_price_tiers (POST /api/v1/Pricing/{productId}/pricings). Represents Swagger's ProductPricingGridResponse."""

    productPricing: ProductPricing = Field(
        description="Contains pricing details, including a list of price tiers for different quantities in the `priceTiers` field."
    )


class ProductDetail(BaseModel):
    """Represents detailed information about a single product returned by sy_list_products. Based on Swagger's Product model."""

    id: int = Field(description="Unique identifier for the product.")
    name: str = Field(description="Display name of the product.")
    format: Optional[str] = Field(
        None, description="Product format (e.g., 'Die-Cut', 'Kiss-Cut', 'Roll')."
    )
    material: Optional[str] = Field(
        None, description="Material type (e.g., 'Vinyl', 'Paper')."
    )
    adhesives: Optional[List[str]] = Field(
        [], description="List of available adhesive options."
    )
    leadingEdgeOptions: Optional[List[str]] = Field(
        [], description="List of available leading edge options (for roll labels)."
    )
    whiteInkOptions: Optional[List[str]] = Field(
        [], description="List of available white ink options."
    )
    finishes: Optional[List[str]] = Field(
        [], description="List of available finish options (e.g., 'Glossy', 'Matte')."
    )
    defaultWidth: Optional[float] = Field(
        None, description="Default width suggested for this product (inches)."
    )
    defaultHeight: Optional[float] = Field(
        None, description="Default height suggested for this product (inches)."
    )
    accessories: Optional[List[AccessoryOption]] = Field(
        [],
        description="List of accessories available for this product. Maps to Swagger's Accessory model.",
    )  # Uses imported AccessoryOption


class ProductListResponse(RootModel[List[ProductDetail]]):
    """Response type for sy_list_products (GET /api/v1/Pricing/list), containing a list of products."""

    root: List[ProductDetail] = Field(
        description="A list containing detailed information for each available product."
    )

    def __iter__(self):
        # Allow iteration over the list
        return iter(self.root)

    def __getitem__(self, item):
        # Allow direct indexing
        return self.root[item]


class OrderItemStatus(OrderItemBase):
    """Represents the status of a single item within an order, returned by sy_get_order_item_statuses (GET /v1/Orders/{id}/items/status). Inherits fields from the imported OrderItemBase."""

    orderItemIdentifier: str = Field(
        description="API-defined identifier for the specific order item."
    )  # Re-declare as required
    status: str = Field(
        description="Textual description of the order item's current status."
    )  # Re-declare as required
    # statusId inherited from OrderItemBase, remains Optional


class OrderDetailResponse(BaseModel):
    """Response body model for sy_get_order_details (GET /v1/Orders/{id}) and also represents a single order in list responses. Based on Swagger's OrderResponse."""

    orderIdentifier: str = Field(
        description="The unique identifier for the order. Swagger: 'Orders Identifier, Must be unique'."
    )
    orderDate: str = Field(
        description="Date and time the order was placed, in ISO 8601 format string. Swagger: 'Date that the Orders was Placed'."
    )
    shipTo: ShipToAddress = Field(
        description="The shipping address associated with the order."
    )  # Uses imported ShipToAddress
    orderTotal: float = Field(
        description="The total monetary value of the order (e.g., in USD). Swagger: 'Orders Total in USD'."
    )
    notes: Optional[str] = Field(
        None,
        description="Notes associated with the entire order. Swagger: 'Orders Notes'.",
    )
    statusId: Optional[int] = Field(
        None,
        description="Numerical status ID of the order (maps to OrderStatusId enum in dto_common). Swagger: 'Orders StatusId'.",
    )
    status: str = Field(
        description="Textual description of the order's current status."
    )
    items: List[OrderItemBase] = Field(
        description="A list of items included in the order. Uses imported OrderItemBase."
    )  # Uses imported OrderItemBase


class OrderListResponse(RootModel[List[OrderDetailResponse]]):
    """Response type for order list endpoints (sy_list_orders_by_status_get/post), containing a list of orders."""

    root: List[OrderDetailResponse] = Field(
        description="A list containing detailed information for each order matching the query."
    )

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class SuccessResponse(BaseModel):
    """Generic response model indicating the success or failure of an action (e.g., sy_create_order). Based on Swagger's ApiResponse."""

    success: bool = Field(
        description="Boolean flag indicating if the operation was successful."
    )
    message: Optional[str] = Field(
        None,
        description="An optional message providing more details about the success or failure.",
    )


class DesignResponse(BaseModel):
    """Response body model for sy_create_design (POST /api/v1/Designs/new)."""

    designId: str = Field(
        description="The unique identifier assigned to the newly created design."
    )
    previewUrl: Optional[str] = Field(
        None, description="An optional URL to preview the created design."
    )
    message: Optional[str] = Field(
        None,
        description="An optional message related to the design creation process (potentially from ApiResponse).",
    )


class DesignPreviewResponse(BaseModel):
    """Response body model for sy_get_design_preview (GET /api/v1/Designs/{designId}/preview)."""

    orderIdentifier: Optional[str] = Field(
        None, description="Optional associated order identifier, if applicable."
    )
    orderDate: Optional[str] = Field(
        None, description="Optional associated order date."
    )
    shipTo: Optional[ShipToAddress] = Field(
        None, description="Optional associated shipping address."
    )  # Uses imported ShipToAddress
    orderTotal: Optional[float] = Field(
        None, description="Optional associated order total."
    )
    notes: Optional[str] = Field(None, description="Optional notes.")
    statusId: Optional[int] = Field(None, description="Optional status ID.")
    status: Optional[str] = Field(None, description="Optional status text.")
    items: Optional[List[OrderItemBase]] = Field(
        None, description="List of items associated with the design preview."
    )  # Uses imported OrderItemBase
