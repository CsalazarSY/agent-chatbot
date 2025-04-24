# pylint: disable=line-too-long
"""Defines Pydantic models for StickerYou API requests and responses."""
# agents/stickeryou/types/sy_api_types.py

from typing import List, Optional
from enum import IntEnum
from pydantic import BaseModel, Field

# --- Enums --- #

class OrderStatusId(IntEnum):
    """Enum for StickerYou Order Status IDs, used in functions like sy_list_orders_by_status_get/post."""
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
    price: float = Field(description="The total price for this quantity of the accessory (required in responses, context-dependent in requests).")
    name: Optional[str] = Field(None, description="The display name of the accessory (often present in responses).")
    pricePerItem: Optional[float] = Field(None, description="The price per individual item of the accessory (often present in responses).")
    currencyCode: Optional[str] = Field(None, description="The currency code for the accessory price (e.g., 'USD') (often present in responses).")

class ShipToAddress(BaseModel):
    """Represents the shipping address details used in order creation and order detail responses."""
    firstname: Optional[str] = Field(None, description="Recipient's first name (Max Length: 50). Required in Order creation.")
    lastname: Optional[str] = Field(None, description="Recipient's last name (Max Length: 50). Required in Order creation.")
    company: Optional[str] = Field(None, description="Recipient's company name, if applicable (Max Length: 50).")
    email: Optional[str] = Field(None, description="Recipient's email address. Required in Order creation.", pattern=r"^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$")
    phone: Optional[str] = Field(None, description="Recipient's phone number.")
    addressLine1: str = Field(description="Primary address line (Max Length: 35).")
    addressLine2: Optional[str] = Field(None, description="Secondary address line (e.g., apartment, suite) (Max Length: 35).")
    city: str = Field(description="City name.")
    stateProvince: Optional[str] = Field(None, description="State or province code/name. Swagger marks as required for Order creation.")
    zipPostalCode: str = Field(description="ZIP or postal code.")
    countryCode: str = Field(description="Two-letter ISO country code (e.g., 'US', 'CA').")

class OrderItemBase(BaseModel):
    """Base model containing common fields for items within an order, used in various requests and responses. Fields map closely to Swagger's OrderItemResponse."""
    itemIdentifier: Optional[str] = Field(None, description="Client-defined identifier for the item (used in CreateOrderRequest). Required in OrderItem/OrderItemDesign requests.")
    orderItemIdentifier: Optional[str] = Field(None, description="API-defined identifier for the order item (returned in responses/status).")
    notes: Optional[str] = Field(None, description="Optional notes specific to this order item.")
    price: Optional[float] = Field(None, description="The total price for the specified quantity of this item. Swagger: 'Item Price per Unit'. Required in OrderItem/OrderItemDesign requests.")
    quantity: Optional[int] = Field(None, description="The number of units for this order item. Required in OrderItem/OrderItemDesign requests.")
    productId: Optional[int] = Field(None, description="The product ID provided by StickerYou (used when not creating from a design).")
    width: Optional[float] = Field(None, description="The width of the item in inches (used when not creating from a design).")
    height: Optional[float] = Field(None, description="The height of the item in inches (used when not creating from a design).")
    artworkUrl: Optional[str] = Field(None, description="URL to the artwork image/PDF (used when not creating from a design).")
    accessoryOptions: Optional[List[AccessoryOption]] = Field(None, description="List of selected accessory options for this item.")
    # Fields primarily for responses/status:
    reason: Optional[str] = Field(None, description="Reason text, often associated with specific statuses like 'Error' or 'OnHold'.")
    statusId: Optional[int] = Field(None, description="Numerical status ID of the order item (maps to OrderStatusId enum).")
    status: Optional[str] = Field(None, description="Textual description of the order item status.")

class OrderItemCreate(OrderItemBase):
    """Represents an item structure specifically for creating a new order via sy_create_order (POST /v1/Orders/new). Based on Swagger's OrderItem."""
    productId: int = Field(description="The product ID provided by StickerYou. Required.")
    width: float = Field(description="The width of the product in inches. Required.")
    height: float = Field(description="The height of the product in inches. Required.")
    artworkUrl: str = Field(description="URL pointing to the artwork file (PDF) for this item. Required.")
    itemIdentifier: str = Field(description="Client-defined identifier for the item. Required.")
    price: float = Field(description="Item Price per Unit (or total for quantity?). Required.")
    quantity: int = Field(description="Quantity to fulfill. Required.")

class OrderItemCreateDesign(OrderItemBase):
    """Represents an item structure specifically for creating a new order from existing designs via sy_create_order_from_designs (POST /v1/Orders/designs/new). Based on Swagger's OrderItemDesign."""
    designId: str = Field(description="The unique identifier of the pre-uploaded design to be used for this item. Required.")
    itemIdentifier: str = Field(description="Client-defined identifier for the item. Required.")
    price: float = Field(description="Item Price per Unit (or total for quantity?). Required.")
    quantity: int = Field(description="Quantity to fulfill. Required.")
    # Inherits optional field notes from OrderItemBase
    # Excludes fields not relevant when creating from a design ID
    productId: Optional[int] = Field(None, exclude=True)
    width: Optional[float] = Field(None, exclude=True)
    height: Optional[float] = Field(None, exclude=True)
    artworkUrl: Optional[str] = Field(None, exclude=True)
    accessoryOptions: Optional[List[AccessoryOption]] = Field(None, exclude=True)


# --- Request Models --- #

class LoginRequest(BaseModel):
    """Request body model for sy_perform_login (POST /users/login). Based on Swagger's LoginModel."""
    userName: str = Field(description="The username for API authentication.")
    password: str = Field(description="The password for API authentication.")

class SpecificPriceRequest(BaseModel):
    """Request body structure for sy_get_specific_price and sy_get_price_tiers (POST /api/v1/Pricing/{productId}/pricing|pricings). Based on Swagger's ProductPricingRequest."""
    width: float = Field(description="The desired width of the product in inches (Min: 0).")
    height: float = Field(description="The desired height of the product in inches (Min: 0).")
    countryCode: Optional[str] = Field(None, description="Optional two-letter ISO country code (e.g., 'US', 'CA') for accurate pricing/shipping (defaults to config). Swagger requires this, Pydantic makes optional.")
    quantity: Optional[int] = Field(None, description="The specific quantity required (mandatory for /pricing, optional for /pricings).")
    currencyCode: Optional[str] = Field(None, description="Optional ISO currency code (e.g., 'USD', 'CAD') (defaults to config).")
    accessoryOptions: Optional[List[AccessoryOption]] = Field(None, description="Optional list of selected accessory options.")

class CreateOrderRequest(BaseModel):
    """Request body model for sy_create_order (POST /v1/Orders/new), creating an order with full item details. Based on Swagger's Order model."""
    orderIdentifier: Optional[str] = Field(None, description="Client-defined identifier for the order. Swagger marks as required.")
    orderDate: Optional[str] = Field(None, description="Optional order date in ISO 8601 format string (e.g., 'YYYY-MM-DDTHH:MM:SSZ'). Swagger marks as required.")
    shipTo: ShipToAddress = Field(description="The shipping address details. Required.")
    orderTotal: Optional[float] = Field(None, description="Optional total amount for the order (e.g., in USD). Swagger marks as required.")
    notes: Optional[str] = Field(None, description="Optional notes for the entire order.")
    items: List[OrderItemCreate] = Field(description="A list of items to include in the order, providing full product details.")

class CreateOrderFromDesignsRequest(BaseModel):
    """Request body model for sy_create_order_from_designs (POST /v1/Orders/designs/new), creating an order using pre-uploaded design IDs. Based on Swagger's OrderDesign model."""
    orderIdentifier: Optional[str] = Field(None, description="Client-defined identifier for the order. Swagger marks as required.")
    orderDate: Optional[str] = Field(None, description="Optional order date in ISO 8601 format string (e.g., 'YYYY-MM-DDTHH:MM:SSZ'). Swagger marks as required.")
    shipTo: ShipToAddress = Field(description="The shipping address details. Required.")
    orderTotal: Optional[float] = Field(None, description="Optional total amount for the order (e.g., in USD). Swagger marks as required.")
    notes: Optional[str] = Field(None, description="Optional notes for the entire order.")
    items: List[OrderItemCreateDesign] = Field(description="A list of items to include in the order, referencing existing design IDs.")

class ListOrdersByStatusRequest(BaseModel):
    """Request body model for sy_list_orders_by_status_post (POST /v1/Orders/status/list). Based on Swagger's OrdersByStatusRequest."""
    take: int = Field(100, description="The maximum number of orders to retrieve (pagination limit).")
    skip: int = Field(0, description="The number of orders to skip (pagination offset).")
    status: int = Field(description="The status ID (from OrderStatusId enum) to filter orders by. Required.")


# --- Response Models --- #

class LoginResponse(BaseModel):
    """Response body model for a successful sy_perform_login (POST /users/login)."""
    token: str = Field(description="The authentication token to be used for subsequent API calls.")
    expirationMinutes: str = Field(description="The duration in minutes for which the token is valid (provided as a string).")

class LoginStatusResponse(BaseModel):
    """Response body model for sy_verify_login (GET /users/login), indicating current token validity. Based on Swagger's LoggedUserModel."""
    name: str = Field(description="The name associated with the authenticated user/token.")
    authenticated: bool = Field(description="Boolean flag indicating if the current token is valid.")

class Country(BaseModel):
    """Represents a single country supported by the API."""
    code: str = Field(description="The two-letter ISO country code.")
    name: str = Field(description="The full name of the country.")

class CountriesResponse(BaseModel):
    """Response body model for sy_list_countries (POST /api/v1/Pricing/countries)."""
    countries: List[Country] = Field(description="A list of supported countries with their codes and names.")

class ShippingMethod(BaseModel):
    """Represents a shipping method available for an order or quote."""
    id: int = Field(description="Unique identifier for the shipping method.")
    name: str = Field(description="Display name of the shipping method.")
    price: float = Field(description="Cost of this shipping method.")
    deliveryEstimate: int = Field(description="Estimated delivery time in business days.")

class PriceTier(BaseModel):
    """Represents a single quantity-based price tier within a pricing response (e.g., within ProductPricing's priceTiers list)."""
    quantity: int = Field(description="The quantity threshold for this price tier.")
    price: float = Field(description="The total price for this quantity tier.")
    # Add other relevant tier fields if known, e.g., pricePerSticker

class ProductPricing(BaseModel):
    """Contains detailed pricing information returned by pricing endpoints. Used in SpecificPriceResponse and PriceTiersResponse. Maps to Swagger's ProductPricing."""
    quantity: Optional[int] = Field(None, description="The specific quantity priced (present in specific price responses).")
    unitMeasure: Optional[str] = Field(None, description="The unit of measurement (e.g., 'Stickers').")
    price: float = Field(description="The calculated total price.")
    pricePerSticker: Optional[float] = Field(None, description="Calculated price per individual sticker, if applicable.")
    stickersPerPage: Optional[int] = Field(None, description="Number of stickers that fit on a single page/sheet, if applicable.")
    currency: str = Field(description="ISO currency code for the price (e.g., 'USD', 'CAD').")
    shippingMethods: Optional[List[ShippingMethod]] = Field([], description="List of available shipping methods and their costs/estimates.")
    accessories: Optional[List[AccessoryOption]] = Field([], description="List of available accessories for the product. Maps to Swagger's Accessory model.")
    priceTiers: Optional[List[PriceTier]] = Field(None, description="List of price tiers showing price variations by quantity (present in PriceTiersResponse, representing Swagger's ProductPricingGridResponse structure).")

class SpecificPriceResponse(BaseModel):
    """Response body model for sy_get_specific_price (POST /api/v1/Pricing/{productId}/pricing). Based on Swagger's ProductPricingResponse."""
    productPricing: ProductPricing = Field(description="Contains the calculated pricing details for the specific quantity requested.")

class PriceTiersResponse(BaseModel):
    """Response body model for sy_get_price_tiers (POST /api/v1/Pricing/{productId}/pricings). Represents Swagger's ProductPricingGridResponse."""
    productPricing: ProductPricing = Field(description="Contains pricing details, including a list of price tiers for different quantities in the `priceTiers` field.")

class ProductDetail(BaseModel):
    """Represents detailed information about a single product returned by sy_list_products. Based on Swagger's Product model."""
    id: int = Field(description="Unique identifier for the product.")
    name: str = Field(description="Display name of the product.")
    format: Optional[str] = Field(None, description="Product format (e.g., 'Die-Cut', 'Kiss-Cut', 'Roll').")
    material: Optional[str] = Field(None, description="Material type (e.g., 'Vinyl', 'Paper').")
    adhesives: Optional[List[str]] = Field([], description="List of available adhesive options.")
    leadingEdgeOptions: Optional[List[str]] = Field([], description="List of available leading edge options (for roll labels).")
    whiteInkOptions: Optional[List[str]] = Field([], description="List of available white ink options.")
    finishes: Optional[List[str]] = Field([], description="List of available finish options (e.g., 'Glossy', 'Matte').")
    defaultWidth: Optional[float] = Field(None, description="Default width suggested for this product (inches).")
    defaultHeight: Optional[float] = Field(None, description="Default height suggested for this product (inches).")
    accessories: Optional[List[AccessoryOption]] = Field([], description="List of accessories available for this product. Maps to Swagger's Accessory model.")

class ProductListResponse(BaseModel):
    """Response type for sy_list_products (GET /api/v1/Pricing/list), containing a list of products. Based on Swagger's ProductListResponse."""
    __root__: List[ProductDetail] = Field(description="A list containing detailed information for each available product.")

    def __iter__(self):
        # Allow iteration over the list
        return iter(self.__root__)

    def __getitem__(self, item):
        # Allow direct indexing
        return self.__root__[item]

class TrackingCodeResponse(BaseModel):
    """Response body model for sy_get_order_tracking (GET /v1/Orders/{id}/trackingcode)."""
    trackingCode: Optional[str] = Field(None, description="The shipping tracking code/number.")
    trackingUrl: Optional[str] = Field(None, description="A direct URL to track the shipment.")
    carrier: Optional[str] = Field(None, description="The name of the shipping carrier.")
    orderIdentifier: Optional[str] = Field(None, description="The identifier of the order this tracking belongs to.")
    message: Optional[str] = Field(None, description="An optional message, e.g., indicating tracking is not yet available.")

class OrderItemStatus(OrderItemBase):
    """Represents the status of a single item within an order, returned by sy_get_order_item_statuses (GET /v1/Orders/{id}/items/status). Inherits fields from OrderItemBase (maps to Swagger's OrderItemResponse)."""
    orderItemIdentifier: str = Field(description="API-defined identifier for the specific order item.")
    status: str = Field(description="Textual description of the order item's current status.")
    statusId: Optional[int] = Field(None, description="Numerical status ID (maps to OrderStatusId enum).")

class OrderDetailResponse(BaseModel):
    """Response body model for sy_get_order_details (GET /v1/Orders/{id}) and also represents a single order in list responses. Based on Swagger's OrderResponse."""
    orderIdentifier: str = Field(description="The unique identifier for the order. Swagger: 'Orders Identifier, Must be unique'.")
    orderDate: str = Field(description="Date and time the order was placed, in ISO 8601 format string. Swagger: 'Date that the Orders was Placed'.")
    shipTo: ShipToAddress = Field(description="The shipping address associated with the order.")
    orderTotal: float = Field(description="The total monetary value of the order (e.g., in USD). Swagger: 'Orders Total in USD'.")
    notes: Optional[str] = Field(None, description="Notes associated with the entire order. Swagger: 'Orders Notes'.")
    statusId: Optional[int] = Field(None, description="Numerical status ID of the order (maps to OrderStatusId enum). Swagger: 'Orders StatusId'.")
    status: str = Field(description="Textual description of the order's current status.")
    items: List[OrderItemBase] = Field(description="A list of items included in the order. Maps to list of Swagger's OrderItemResponse.")

class OrderListResponse(BaseModel):
    """Response type for order list endpoints (sy_list_orders_by_status_get/post), containing a list of orders."""
    __root__: List[OrderDetailResponse] = Field(description="A list containing detailed information for each order matching the query.")

    def __iter__(self):
        return iter(self.__root__)

    def __getitem__(self, item):
        return self.__root__[item]

class SuccessResponse(BaseModel):
    """Generic response model indicating the success or failure of an action (e.g., sy_create_order). Based on Swagger's ApiResponse."""
    success: bool = Field(description="Boolean flag indicating if the operation was successful.")
    message: Optional[str] = Field(None, description="An optional message providing more details about the success or failure.")

class DesignResponse(BaseModel):
    """Response body model for sy_create_design (POST /api/v1/Designs/new)."""
    designId: str = Field(description="The unique identifier assigned to the newly created design.")
    previewUrl: Optional[str] = Field(None, description="An optional URL to preview the created design.")
    message: Optional[str] = Field(None, description="An optional message related to the design creation process (potentially from ApiResponse).")

class DesignPreviewResponse(BaseModel):
    """Response body model for sy_get_design_preview (GET /api/v1/Designs/{designId}/preview)."""
    orderIdentifier: Optional[str] = Field(None, description="Optional associated order identifier, if applicable.")
    orderDate: Optional[str] = Field(None, description="Optional associated order date.")
    shipTo: Optional[ShipToAddress] = Field(None, description="Optional associated shipping address.")
    orderTotal: Optional[float] = Field(None, description="Optional associated order total.")
    notes: Optional[str] = Field(None, description="Optional notes.")
    statusId: Optional[int] = Field(None, description="Optional status ID.")
    status: Optional[str] = Field(None, description="Optional status text.")
    items: Optional[List[OrderItemBase]] = Field(None, description="List of items associated with the design preview.")


# Note: Generic Error models (UnauthorizedError, BadRequestError, ServerError)
# are omitted here as the agent primarily handles errors via the
# SY_TOOL_FAILED string, but they could be defined for completeness if needed.
