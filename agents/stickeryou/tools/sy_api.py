# pylint: disable=line-too-long, broad-exception-caught
# agents/stickeryou/tools/sy_api.py
"""Defines tools (functions) for interacting with the StickerYou API."""

import asyncio
import json
import traceback
from typing import Optional, List, Dict

import httpx

# Import necessary configuration constants and the refresh function
import config # Import the whole module to access globals

# Import Pydantic models
from agents.stickeryou.types.sy_api_types import (
    LoginResponse, LoginStatusResponse, CountriesResponse, SpecificPriceResponse,
    PriceTiersResponse, ProductListResponse, OrderItemStatus,
    OrderDetailResponse, OrderListResponse, SuccessResponse, DesignResponse, DesignPreviewResponse
)

# Standardized Error Prefix
API_ERROR_PREFIX = "SY_TOOL_FAILED:"

# --- Helper Function for API Requests with Retry ---
async def _make_sy_api_request(
    method: str,
    api_url: str,
    headers_base: Optional[Dict] = None,
    json_payload: Optional[Dict] = None,
    timeout: float = 30.0,
    max_retries: int = 1 # Only retry once on 401
) -> Dict | List | str:
    """
    Internal helper to make SY API requests, handling dynamic token auth and 401 retry.
    """
    if not config.API_BASE_URL:
        return f"{API_ERROR_PREFIX} Configuration Error - Missing API Base URL."

    auth_token = config.SY_API_AUTH_TOKEN_DYNAMIC or config.API_AUTH_TOKEN # Prioritize dynamic
    if not auth_token:
        return f"{API_ERROR_PREFIX} Configuration Error - No SY API auth token available (static or dynamic)."

    headers = headers_base or {}
    headers["Authorization"] = f"Bearer {auth_token}"
    headers.setdefault("Accept", "application/json") # Ensure Accept header is present

    response: Optional[httpx.Response] = None # Initialize with type hint
    retry_count = 0

    while retry_count <= max_retries:
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                request_method = method.upper()
                if request_method == "GET":
                    response = await client.get(api_url, headers=headers)
                elif request_method == "POST":
                    headers.setdefault("Content-Type", "application/json")
                    response = await client.post(api_url, headers=headers, json=json_payload)
                elif request_method == "PUT": # Add PUT method handling
                    headers.setdefault("Content-Type", "application/json") # Often needed for PUT too
                    response = await client.put(api_url, headers=headers, json=json_payload)
                elif request_method == "DELETE":
                    response = await client.delete(api_url, headers=headers)
                else:
                    return f"{API_ERROR_PREFIX} Unsupported HTTP method: {method}"

            if response.status_code == 200:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    # If 200 OK but not JSON, return raw text if useful, else error
                    # Check content-type? For now, assume JSON expected on 200 OK
                    return f"{API_ERROR_PREFIX} Failed to decode successful JSON response (Status 200)."

            elif response.status_code == 401 and retry_count < max_retries:
                print(f"SY API request received 401 Unauthorized. " 
                      f"Attempting token refresh (Retry {retry_count + 1}/{max_retries})...")
                refresh_successful = await config.refresh_sy_token()
                retry_count += 1

                if refresh_successful and config.SY_API_AUTH_TOKEN_DYNAMIC:
                    auth_token = config.SY_API_AUTH_TOKEN_DYNAMIC
                    headers["Authorization"] = f"Bearer {auth_token}"
                    print("Token refreshed. Retrying API call...")
                    await asyncio.sleep(0.5)
                    continue
                else:
                    print("Token refresh failed or new token not available. Aborting retries.")
                    return f"{API_ERROR_PREFIX} Unauthorized (401) and token refresh failed."

            else:
                # --- Enhanced Error Message Extraction ---
                status_code = response.status_code
                error_message_detail = ""
                try:
                    # Attempt to parse JSON body first
                    error_json = response.json()
                    if isinstance(error_json, dict):
                        # Look for common error message keys
                        if 'message' in error_json:
                            # Handle nested JSON string in message field
                            if isinstance(error_json['message'], str):
                                try:
                                    nested_error = json.loads(error_json['message'])
                                    if isinstance(nested_error, dict) and 'Error' in nested_error:
                                        error_message_detail = f" Detail: {nested_error['Error']}"
                                    else:
                                         error_message_detail = f" Detail: {error_json['message'][:200]}" # Use raw message if nested parse fails
                                except json.JSONDecodeError:
                                     error_message_detail = f" Detail: {error_json['message'][:200]}" # Use raw message if not valid JSON string

                            else:
                                # Use the message directly if not a string or nested JSON isn't found
                                error_message_detail = f" Detail: {str(error_json['message'])[:200]}"

                        elif 'error' in error_json:
                            error_message_detail = f" Detail: {str(error_json['error'])[:200]}"
                        elif 'detail' in error_json:
                             error_message_detail = f" Detail: {str(error_json['detail'])[:200]}"
                        else:
                            # Fallback to string representation of the dict if no known key
                            error_message_detail = f" Detail: {str(error_json)[:200]}"
                    else:
                        # If JSON but not a dict, use string representation
                         error_message_detail = f" Detail: {str(error_json)[:200]}"

                except json.JSONDecodeError:
                    # If body is not JSON, use raw text
                    try:
                        error_message_detail = f" Detail: {response.text[:200]}"
                    except Exception:
                        error_message_detail = " Detail: [Could not read response body]"
                except Exception:
                    # Catch any other parsing errors
                     error_message_detail = " Detail: [Error parsing response body]"


                # Construct the final error message
                if status_code == 400:
                    return f"{API_ERROR_PREFIX} Bad Request (400).{error_message_detail}"
                elif status_code == 401: # Should only hit this if retries failed or max_retries=0
                     return f"{API_ERROR_PREFIX} Unauthorized (401) after retries.{error_message_detail}"
                elif status_code == 403:
                    return f"{API_ERROR_PREFIX} Forbidden (403).{error_message_detail}"
                elif status_code == 404:
                    return f"{API_ERROR_PREFIX} Not Found (404).{error_message_detail}"
                elif status_code >= 500:
                    return f"{API_ERROR_PREFIX} Server Error ({status_code}).{error_message_detail}"
                else:
                    return f"{API_ERROR_PREFIX} Unexpected HTTP {status_code}.{error_message_detail}"
                # --- End Enhanced Error Message Extraction ---

        except httpx.TimeoutException:
            return f"{API_ERROR_PREFIX} Request timed out."
        except httpx.RequestError as req_err:
            # Provide more specific network error info if possible
            return f"{API_ERROR_PREFIX} Network/Connection Error: {req_err}"
        except json.JSONDecodeError: # Should be less likely to hit here now
            status_code_str = str(response.status_code) if response else 'Unknown'
            raw_text = response.text[:200] if response else "[No Response]"
            return f"{API_ERROR_PREFIX} Failed to decode response as JSON. Status: {status_code_str}. Body starts: {raw_text}"
        except Exception as e:
            traceback.print_exc()
            return f"{API_ERROR_PREFIX} Unexpected error in request helper: {type(e).__name__} - {e}"

        # This break should only be reached if a non-401 error occurred within the loop
        # or if max_retries was reached for a 401 without successful refresh.
        # The specific error should have already been returned above.
        break

    # Fallback if loop finishes unexpectedly (should ideally not happen)
    return f"{API_ERROR_PREFIX} API request helper finished unexpectedly."


# --- Tool Functions (Refactored to use _make_sy_api_request) ---
# --- Designs ---
async def sy_create_design(
    product_id: int,
    width: float,
    height: float,
    image_base64: str,
) -> DesignResponse | str:
    """
    (POST /api/{version}/Designs/new)
    Description: Sends a new design image and its details (product, dimensions) to StickerYou.

    Parameters:
        product_id (int): Identifier for the product the design is for.
        width (float): Desired width of the design in inches.
        height (float): Desired height of the design in inches.
        image_base64 (str): The design image encoded as a Base64 string.

    Request body example:
        {
            "productId": 123,
            "width": 3.0,
            "height": 2.5,
            "imageBase64": "data:image/png;base64,..."
        }

    Response body template (on success, type: DesignResponse):
        {
            "designId": str,
            "previewUrl": Optional[str],
            "message": Optional[str]
        }
    """
    api_url = f"{config.API_BASE_URL}/api/{config.API_VERSION}/Designs/new"
    payload = {"productId": product_id, "width": width, "height": height, "imageBase64": image_base64}
    result = await _make_sy_api_request("POST", api_url, json_payload=payload, timeout=60.0)

    if isinstance(result, dict):
        return result
    elif isinstance(result, str) and result.startswith(API_ERROR_PREFIX):
        return result
    else:
        return (
            f"{API_ERROR_PREFIX} Unexpected successful response type: "
            f"{type(result)}. Expected Dict."
        )


async def sy_get_design_preview(
    design_id: str,
) -> DesignPreviewResponse | str:
    """
    (GET /api/{version}/Designs/{designId}/preview)
    Description: Retrieves preview details for a previously created design using its unique ID.
                 The response structure often resembles order details.
    Allowed Scopes: [User, Dev, Internal]

    Parameters:
        design_id (str): The unique identifier of the design (e.g., 'dz_123abc456def').

    Request body example: None (GET request)

    Response body template (on success, type: DesignPreviewResponse):
        {
            "orderIdentifier": Optional[str],
            "orderDate": Optional[str],
            "shipTo": Optional[Dict], # ShipToAddress structure
            "orderTotal": Optional[float],
            "notes": Optional[str],
            "statusId": Optional[int],
            "status": Optional[str],
            "items": Optional[List[Dict]] # List of OrderItemBase structure
        }
        (Note: Response structure is inferred and might vary based on actual API behavior.)
    """
    api_url = f"{config.API_BASE_URL}/api/{config.API_VERSION}/Designs/{design_id}/preview"
    result = await _make_sy_api_request("GET", api_url)

    if isinstance(result, dict):
        return result
    elif isinstance(result, str) and result.startswith(API_ERROR_PREFIX):
        return result
    else:
        return (
            f"{API_ERROR_PREFIX} Unexpected successful response type: "
            f"{type(result)}. Expected Dict."
        )


# --- Orders ---

async def sy_list_orders_by_status_get(
    status_id: int,
) -> OrderListResponse | str:
    """
    (GET /v{version}/Orders/status/list/{status})
    Description: Retrieves a list of orders matching a specific status ID using a GET request.
    Allowed Scopes: [Dev, Internal]

    Parameters:
        status_id (int): The status ID to filter orders by. Valid values:
                         1 (Cancelled), 2 (Error), 10 (New), 20 (Accepted),
                         30 (InProgress), 40 (OnHold), 50 (Printed), 100 (Shipped).

    Request body example: None (GET request)

    Response body template (on success, type: OrderListResponse - List[OrderDetailResponse]):
        [
            {
                "orderIdentifier": str,
                "orderDate": str,
                "shipTo": Dict, # ShipToAddress structure
                "orderTotal": float,
                "notes": Optional[str],
                "statusId": Optional[int],
                "status": str,
                "items": List[Dict] # List of OrderItemBase structure
            }
            # ... more orders ...
        ]
    """
    api_url = f"{config.API_BASE_URL}/{config.API_VERSION}/Orders/status/list/{status_id}"
    result = await _make_sy_api_request("GET", api_url)

    if isinstance(result, list):
        return result
    elif isinstance(result, str) and result.startswith(API_ERROR_PREFIX):
        if "Not Found (404)" in result:
            return f"{API_ERROR_PREFIX} Invalid Status ID {status_id} provided? (404)."
        return result
    else:
        return (
            f"{API_ERROR_PREFIX} Unexpected successful response type: "
            f"{type(result)}. Expected List."
        )


async def sy_list_orders_by_status_post(
    status_id: int,
    take: int = 100,
    skip: int = 0,
) -> OrderListResponse | str:
    """
    (POST /{version}/Orders/status/list)
    Description: Retrieves a paginated list of orders matching a specific status ID using a POST request.
    Allowed Scopes: [Dev, Internal]
    Note: Raw results should generally not be presented directly to the user.

    Parameters:
        status_id (int): The status ID (from OrderStatusId enum) to filter orders by. Required.
        take (int): The maximum number of orders to retrieve (pagination limit). Default: 100.
        skip (int): The number of orders to skip (pagination offset). Default: 0.

    Request body example (type: ListOrdersByStatusRequest):
        {
            "take": 50,
            "skip": 0,
            "status": 20
        }

    Response body template (on success, type: OrderListResponse - List[OrderDetailResponse]):
        [
            {
                "orderIdentifier": str,
                "orderDate": str,
                "shipTo": Dict, # ShipToAddress structure
                "orderTotal": float,
                "notes": Optional[str],
                "statusId": Optional[int],
                "status": str,
                "items": List[Dict] # List of OrderItemBase structure
            }
            # ... more orders ...
        ]
    """
    api_url = f"{config.API_BASE_URL}/{config.API_VERSION}/Orders/status/list"
    payload = {"take": take, "skip": skip, "status": status_id}
    result = await _make_sy_api_request("POST", api_url, json_payload=payload)

    if isinstance(result, list):
        return result
    elif isinstance(result, str) and result.startswith(API_ERROR_PREFIX):
        return result
    else:
        return (
            f"{API_ERROR_PREFIX} Unexpected successful response type: "
            f"{type(result)}. Expected List."
        )


async def sy_create_order(
    order_data: Dict,
) -> SuccessResponse | str:
    """
    (POST /{version}/Orders/new)
    Description: Submits a new order containing items defined with product details (ID, dimensions, artwork URL).

    Parameters:
        order_data (Dict): A dictionary conforming to the CreateOrderRequest model structure.

    Request body example (type: CreateOrderRequest):
        {
            "orderIdentifier": "client-order-xyz",
            "orderDate": "2023-10-27T11:00:00Z",
            "shipTo": { /* ... ShipToAddress fields ... */ },
            "orderTotal": 99.99,
            "notes": "Standard shipping.",
            "items": [ { /* ... OrderItemCreate fields ... */ } ]
        }
        (Note: Pydantic model marks some root fields Optional, Swagger marks them Required. Use required fields for successful creation.)

    Response body template (on success, type: SuccessResponse):
        {
            "success": bool,
            "message": Optional[str]
        }
    """
    api_url = f"{config.API_BASE_URL}/{config.API_VERSION}/Orders/new"
    result = await _make_sy_api_request("POST", api_url, json_payload=order_data)

    if isinstance(result, dict):
        return result
    elif isinstance(result, str) and result.startswith(API_ERROR_PREFIX):
        return result
    else:
        return (
            f"{API_ERROR_PREFIX} Unexpected successful response type: "
            f"{type(result)}. Expected Dict."
        )


async def sy_create_order_from_designs(
    order_data: Dict,
) -> SuccessResponse | str:
    """
    (POST /{version}/Orders/designs/new)
    Description: Submits a new order containing items linked to pre-uploaded design IDs.

    Parameters:
        order_data (Dict): A dictionary conforming to the CreateOrderFromDesignsRequest model structure.

    Request body example (type: CreateOrderFromDesignsRequest):
        {
            "orderIdentifier": "client-design-order-123",
            "orderDate": "2023-10-27T12:00:00Z",
            "shipTo": { /* ... ShipToAddress fields ... */ },
            "orderTotal": 75.00,
            "notes": "Use designs dz_abc and dz_def.",
            "items": [ { /* ... OrderItemCreateDesign fields ... */ } ]
        }
        (Note: Pydantic model marks some root fields Optional, Swagger marks them Required. Use required fields for successful creation.)

    Response body template (on success, type: SuccessResponse):
        {
            "success": bool,
            "message": Optional[str]
        }
    """
    api_url = f"{config.API_BASE_URL}/{config.API_VERSION}/Orders/designs/new"
    result = await _make_sy_api_request("POST", api_url, json_payload=order_data)

    if isinstance(result, dict):
        return result
    elif isinstance(result, str) and result.startswith(API_ERROR_PREFIX):
        return result
    else:
        return (
            f"{API_ERROR_PREFIX} Unexpected successful response type: "
            f"{type(result)}. Expected Dict."
        )


async def sy_get_order_details(
    order_id: str,
) -> OrderDetailResponse | str:
    """
    (GET /{version}/Orders/{id})
    Description: Retrieves the full details for a specific order using its unique identifier.
    Allowed Scopes: [User, Dev, Internal]

    Parameters:
        order_id (str): The StickerYou identifier for the order (e.g., 'ORD-12345').

    Request body example: None (GET request)

    Response body template (on success, type: OrderDetailResponse):
        {
            "orderIdentifier": str,
            "orderDate": str,
            "shipTo": Dict, # ShipToAddress structure
            "orderTotal": float,
            "notes": Optional[str],
            "statusId": Optional[int],
            "status": str,
            "items": List[Dict] # List of OrderItemBase structure
        }
    """
    api_url = f"{config.API_BASE_URL}/{config.API_VERSION}/Orders/{order_id}"
    result = await _make_sy_api_request("GET", api_url)

    if isinstance(result, dict):
        return result
    elif isinstance(result, str) and result.startswith(API_ERROR_PREFIX):
        if "Not Found (404)" in result:
            return f"{API_ERROR_PREFIX} Order not found (404)."  # More specific error
        return result
    else:
        return (
            f"{API_ERROR_PREFIX} Unexpected successful response type: "
            f"{type(result)}. Expected Dict."
        )


async def sy_cancel_order(
    order_id: str,
) -> OrderDetailResponse | str:
    """
    (PUT /{version}/Orders/{id}/cancel)
    Description: Attempts to cancel an existing order using its identifier. Cancellation may only be possible
                 if the order has not progressed too far in the production process.
    Allowed Scopes: [Dev Only] (User requests to cancel should be handled via handoff for now).

    Parameters:
        order_id (str): The StickerYou identifier for the order to cancel.

    Request body example: None (PUT request)

    Response body template (on success, type: OrderDetailResponse - often returns the updated order detail):
        {
            "orderIdentifier": str,
            "orderDate": str,
            "shipTo": Dict, # ShipToAddress structure
            "orderTotal": float,
            "notes": Optional[str],
            "statusId": Optional[int], # Should be updated to 1 (Cancelled)
            "status": str, # Should be updated to "Cancelled"
            "items": List[Dict] # List of OrderItemBase structure
        }
        (Note: Success might also be indicated by a simple 200 OK with no body, or a different structure.)
    """
    api_url = f"{config.API_BASE_URL}/{config.API_VERSION}/Orders/{order_id}/cancel"
    # Assuming PUT might not need a payload, adjust if needed
    result = await _make_sy_api_request("PUT", api_url)

    if isinstance(result, dict):
        return result
    # The API might return non-JSON on successful PUT/DELETE, check docs or handle based on observation
    # Example: elif isinstance(result, str) and not result.startswith(API_ERROR_PREFIX): return {"status": "success", "message": result}
    elif isinstance(result, str) and result.startswith(API_ERROR_PREFIX):
        if "Not Found (404)" in result:
            return f"{API_ERROR_PREFIX} Order not found (404)."
        return result
    else:
        # Consider if a plain string might be a valid success confirmation
        return (
            f"{API_ERROR_PREFIX} Unexpected successful response type: "
            f"{type(result)}. Expected Dict (or confirmation)."
        )


async def sy_get_order_item_statuses(
    order_id: str,
) -> List[OrderItemStatus] | str:
    """
    (GET /{version}/Orders/{id}/items/status)
    Description: Retrieves the status for each individual item within a specific order.
    Allowed Scopes: [User, Dev, Internal]
    Note: This information is usually included in `sy_get_order_details`. Use that tool preferably unless only item statuses are needed.

    Parameters:
        order_id (str): The StickerYou identifier for the parent order.

    Request body example: None (GET request)

    Response body template (on success, type: List[OrderItemStatus]):
        [
            {
                # Inherited fields from OrderItemBase:
                "itemIdentifier": Optional[str],
                "orderItemIdentifier": str, # Overridden to be required in OrderItemStatus
                "notes": Optional[str],
                "price": Optional[float],
                "quantity": Optional[int],
                "productId": Optional[int],
                "width": Optional[float],
                "height": Optional[float],
                "artworkUrl": Optional[str],
                "accessoryOptions": Optional[List[Dict]], # List of AccessoryOption structure
                "reason": Optional[str],
                # OrderItemStatus specific fields:
                "status": str,
                "statusId": Optional[int]
            }
            # ... more items ...
        ]
    """
    api_url = f"{config.API_BASE_URL}/{config.API_VERSION}/Orders/{order_id}/items/status"
    result = await _make_sy_api_request("GET", api_url)

    if isinstance(result, list):
        return result
    elif isinstance(result, str) and result.startswith(API_ERROR_PREFIX):
        if "Not Found (404)" in result:
            return f"{API_ERROR_PREFIX} Order not found (404)."
        return result
    else:
        return (
            f"{API_ERROR_PREFIX} Unexpected successful response type: "
            f"{type(result)}. Expected List."
        )


async def sy_get_order_tracking(
    order_id: str,
) -> Dict | str: # Changed return type hint to Dict | str
    """
    (GET /{version}/Orders/{id}/trackingcode)
    Description: Retrieves the shipping tracking information (code, URL, carrier) for a shipped order.
    Allowed Scopes: [User, Dev, Internal]
    Note: Returns a raw string, not a dict.The API might return 404 if the order doesn't exist or tracking isn't populated.

    Parameters:
        order_id (str): The StickerYou identifier for the order.

    Request body example: None (GET request)

    Response body template (on success, type: TrackingCodeResponse):
        {
            "trackingCode": Optional[str],
            "trackingUrl": Optional[str],
            "carrier": Optional[str],
            "orderIdentifier": Optional[str],
            "message": Optional[str]
        }
        (Note: Fields might be null if tracking is not yet available or if the order hasn't shipped.)
    """
    api_url = f"{config.API_BASE_URL}/{config.API_VERSION}/Orders/{order_id}/trackingcode"
    result = await _make_sy_api_request("GET", api_url)

    if isinstance(result, dict):
        # Check if tracking info is actually present
        if result.get("trackingCode") or result.get("trackingUrl"):
             return result
        else:
            # Return a specific message if tracking is not populated yet
            return f"{API_ERROR_PREFIX} Tracking information not yet available for this order."
            # Alternatively return the dict as is: return result
    elif isinstance(result, str) and result.startswith(API_ERROR_PREFIX):
        if "Not Found (404)" in result:
            # Keep specific error for order not found / no tracking
            return f"{API_ERROR_PREFIX} Tracking not available or order not found (404)."
        return result # Return other errors with details from helper
    else:
        return (
            f"{API_ERROR_PREFIX} Unexpected successful response type: "
            f"{type(result)}. Expected Dict."
        )


# --- Pricing ---

async def sy_list_products(
) -> ProductListResponse | str:
    """
    (GET /api/{version}/Pricing/list)
    Description: Retrieves a list of all available products and their configurable options.
    Allowed Scopes: [User, Dev, Internal]

    Parameters: None

    Request body example: None (GET request)

    Response body template (on success, type: ProductListResponse - List[ProductDetail]):
        [
            {
                "id": int,
                "name": str,
                "format": Optional[str],
                "material": Optional[str],
                "adhesives": Optional[List[str]],
                "leadingEdgeOptions": Optional[List[str]],
                "whiteInkOptions": Optional[List[str]],
                "finishes": Optional[List[str]],
                "defaultWidth": Optional[float],
                "defaultHeight": Optional[float],
                "accessories": Optional[List[Dict]] # List of AccessoryOption structure
            }
            # ... more products ...
        ]
    """
    api_url = f"{config.API_BASE_URL}/api/{config.API_VERSION}/Pricing/list"
    result = await _make_sy_api_request("GET", api_url)

    # ProductListResponse is RootModel[List], so result should be a list on success
    if isinstance(result, list):
        return result # Direct list matches Pydantic model
    elif isinstance(result, dict) and 'root' in result:
         # Handle case if it incorrectly comes back as a dict { "root": [...] }
        if isinstance(result['root'], list):
            return result['root']
        else:
             return f"{API_ERROR_PREFIX} Unexpected structure in product list response dict."

    elif isinstance(result, str) and result.startswith(API_ERROR_PREFIX):
        return result
    else:
        return (
            f"{API_ERROR_PREFIX} Unexpected successful response type for product list: "
            f"{type(result)}. Expected List."
        )


async def sy_get_price_tiers(
    product_id: int,
    width: float,
    height: float,
    country_code: Optional[str] = None,
    currency_code: Optional[str] = None,
    accessory_options: Optional[List[Dict]] = None,
    quantity: Optional[int] = None,
) -> PriceTiersResponse | str:
    """
    (POST /api/{version}/Pricing/{productId}/pricings)
    Description: Retrieves pricing information for different quantity tiers of a specific product.
    Allowed Scopes: [User, Dev, Internal]

    Parameters:
        product_id (int): The unique identifier of the product.
        width (float): The desired width in inches.
        height (float): The desired height in inches.
        country_code (Optional[str]): Two-letter ISO country code for shipping/pricing context (defaults to config).
        currency_code (Optional[str]): ISO currency code (e.g., 'USD', 'CAD') (defaults to config).
        accessory_options (Optional[List[Dict]]): List of selected accessories, each a dict like {"accessoryId": int, "quantity": int}.
        quantity (Optional[int]): A specific quantity to potentially center the price tiers around (optional for this endpoint).

    Request body example (type: SpecificPriceRequest - with optional quantity):
        {
            "width": 4.0,
            "height": 3.0,
            "countryCode": "US",
            "currencyCode": "USD",
            "accessoryOptions": [
                {"accessoryId": 501, "quantity": 1}
            ],
            "quantity": 500 # Optional for /pricings
        }

    Response body template (on success, type: PriceTiersResponse):
        {
            "productPricing": {
                "quantity": Optional[int],
                "unitMeasure": Optional[str],
                "price": float,
                "pricePerSticker": Optional[float],
                "stickersPerPage": Optional[int],
                "currency": str,
                "shippingMethods": Optional[List[Dict]], # List of ShippingMethod structure
                "accessories": Optional[List[Dict]], # List of AccessoryOption structure
                "priceTiers": Optional[List[Dict]] # List of PriceTier structure
            }
        }
        (Note: The Pydantic PriceTiersResponse model nests tiers under productPricing.priceTiers.)
    """
    api_url = f"{config.API_BASE_URL}/api/{config.API_VERSION}/Pricing/{product_id}/pricings"
    payload = {
        "width": float(width),
        "height": float(height),
        "countryCode": country_code or config.DEFAULT_COUNTRY_CODE,
        "currencyCode": currency_code or config.DEFAULT_CURRENCY_CODE,
        "accessoryOptions": accessory_options or [],
    }
    if quantity is not None:
        payload["quantity"] = int(quantity)

    result = await _make_sy_api_request("POST", api_url, json_payload=payload)

    if isinstance(result, dict):
        return result
    elif isinstance(result, str) and result.startswith(API_ERROR_PREFIX):
        return result
    else:
        return (
            f"{API_ERROR_PREFIX} Unexpected successful response type: "
            f"{type(result)}. Expected Dict."
        )

async def sy_get_specific_price(
    product_id: int,
    width: float,
    height: float,
    quantity: int, # Quantity is required here
    country_code: Optional[str] = None,
    currency_code: Optional[str] = None,
    accessory_options: Optional[List[Dict]] = None
) -> SpecificPriceResponse | str:
    """
    (POST /api/{version}/Pricing/{productId}/pricing)
    Description: Calculates and returns the exact price for a specific quantity of a product,
                 based on its dimensions and selected options. Also returns shipping methods.
    Allowed Scopes: [User, Dev, Internal]

    Parameters:
        product_id (int): The unique identifier of the product.
        width (float): The desired width in inches.
        height (float): The desired height in inches.
        quantity (int): The specific quantity required for pricing. Required.
        country_code (Optional[str]): Two-letter ISO country code for shipping/pricing context (defaults to config).
        currency_code (Optional[str]): ISO currency code (e.g., 'USD', 'CAD') (defaults to config).
        accessory_options (Optional[List[Dict]]): List of selected accessories, each a dict like {"accessoryId": int, "quantity": int}.

    Request body example (type: SpecificPriceRequest):
        {
            "width": 2.0,
            "height": 2.0,
            "countryCode": "CA",
            "quantity": 250,
            "currencyCode": "CAD",
            "accessoryOptions": []
        }

    Response body template (on success, type: SpecificPriceResponse):
        {
            "productPricing": {
                "quantity": Optional[int],
                "unitMeasure": Optional[str],
                "price": float,
                "pricePerSticker": Optional[float],
                "stickersPerPage": Optional[int],
                "currency": str,
                "shippingMethods": Optional[List[Dict]], # List of ShippingMethod structure
                "accessories": Optional[List[Dict]], # List of AccessoryOption structure
                "priceTiers": Optional[List[Dict]] # List of PriceTier structure (usually null here)
            }
        }
    """
    api_url = f"{config.API_BASE_URL}/api/{config.API_VERSION}/Pricing/{product_id}/pricing"
    payload = {
        "width": float(width),
        "height": float(height),
        "countryCode": country_code or config.DEFAULT_COUNTRY_CODE,
        "quantity": int(quantity),
        "currencyCode": currency_code or config.DEFAULT_CURRENCY_CODE,
        "accessoryOptions": accessory_options or [],
    }
    result = await _make_sy_api_request("POST", api_url, json_payload=payload)

    if isinstance(result, dict):
        return result
    elif isinstance(result, str) and result.startswith(API_ERROR_PREFIX):
        return result
    else:
        return (
            f"{API_ERROR_PREFIX} Unexpected successful response type: "
            f"{type(result)}. Expected Dict."
        )

async def sy_list_countries(
) -> CountriesResponse | str:
    """
    (POST /api/{version}/Pricing/countries)
    Description: Retrieves a list of countries supported by the StickerYou API for pricing and shipping.
    Allowed Scopes: [User, Dev, Internal]

    Parameters: None

    Request body example: None (POST request, but typically empty)

    Response body template (on success, type: CountriesResponse):
        {
            "countries": List[Dict] # List of Country structure ({ "code": str, "name": str })
        }
        (Note: Pydantic model CountriesResponse has `countries` list directly. Response might wrap it in a dict.)
    """
    api_url = f"{config.API_BASE_URL}/api/{config.API_VERSION}/Pricing/countries"
    # Send POST request, assuming no payload is needed based on typical usage for lists
    result = await _make_sy_api_request("POST", api_url)

    # Response might be a dict {'countries': [...]} or just the list [...]
    if isinstance(result, (dict, list)):
        return result
    elif isinstance(result, str) and result.startswith(API_ERROR_PREFIX):
        return result
    else:
        return (
            f"{API_ERROR_PREFIX} Unexpected successful response type: "
            f"{type(result)}. Expected Dict or List."
        )

# --- Users ---

async def sy_verify_login(
) -> LoginStatusResponse | str:
    """
    (GET /users/login)
    Description: Verifies if the currently configured authentication token (Bearer) is valid.
    Allowed Scopes: [Internal, Dev] (Used by the request helper for token checks).

    Parameters: None

    Request body example: None (GET request)

    Response body template (on success - 200 OK, type: LoginStatusResponse):
        {
            "name": str,
            "authenticated": bool
        }
        (Note: This function actually returns a custom dictionary status for success/failure interpretation:
         e.g., {"status": "success", "message": "...", "details": { ... actual response ... } }
         e.g., {"status": "failed", "message": "Token is invalid (Unauthorized 401)."} for 401)
    """
    api_url = f"{config.API_BASE_URL}/users/login"
    result = await _make_sy_api_request("GET", api_url, max_retries=0)

    if isinstance(result, dict):
        # Successful call, return custom status dict
        return {
            "status": "success",
            "message": "Token appears valid (received 200 OK or data).",
            "details": result
        }
    elif isinstance(result, str) and result.startswith(API_ERROR_PREFIX):
        # Specific handling for 401 on verify
        if "Unauthorized (401)" in result:
            return {"status": "failed", "message": "Token is invalid (Unauthorized 401)."}
        # Return other detailed errors from helper
        return result
    else:
        return f"{API_ERROR_PREFIX} Unexpected response type during verification: {type(result)}."


async def sy_perform_login(
    username: str,
    password: str,
) -> LoginResponse | str:
    """
    (POST /users/login)
    Description: Authenticates using username and password to obtain a temporary API Bearer token.
                 The token and its expiration are returned upon successful login.
                 Note: This function makes a direct HTTP request, bypassing the standard helper,
                 as it doesn't use an existing token for authorization.
    Allowed Scopes: [Internal, Dev] (Used by the token refresh mechanism).
                 
    Parameters:
        username (str): The API username.
        password (str): The API password.

    Request body example (type: LoginRequest):
        {
            "userName": "your_api_username",
            "password": "your_api_password"
        }

    Response body template (on success, type: LoginResponse):
        {
            "token": str,
            "expirationMinutes": str
        }
    """
    if not config.API_BASE_URL:
        return f"{API_ERROR_PREFIX} Configuration Error - Missing API Base URL."

    api_url = f"{config.API_BASE_URL}/users/login"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    payload = {"userName": username, "password": password}

    response: Optional[httpx.Response] = None
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(api_url, headers=headers, json=payload)

        # Ensure response is checked after the with block
        if response is None:
            # This case should be rare but handles potential early exit from context manager
            return f"{API_ERROR_PREFIX} Failed to get response from login request."

        if response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError:
                return (
                    f"{API_ERROR_PREFIX} Failed to decode successful JSON "
                    f"response from login (Status 200)."
                )
        else:
            # Try to get more detail for login failure
            status_code = response.status_code
            error_detail = ""
            try:
                error_json = response.json()
                if isinstance(error_json, dict):
                     error_detail = f" Detail: {str(error_json)[:200]}"
            except json.JSONDecodeError:
                 try:
                     error_detail = f" Detail: {response.text[:200]}"
                 except Exception:
                     error_detail = " Detail: [Could not read response body]"
            except Exception:
                error_detail = " Detail: [Error parsing response body]"


            if status_code == 400:
                return (
                    f"{API_ERROR_PREFIX} Bad Request (400). Invalid credentials "
                    f"or request format?{error_detail}"
                )
            elif status_code == 401:
                return f"{API_ERROR_PREFIX} Unauthorized (401). Invalid username or password?{error_detail}"
            elif status_code >= 500:
                return f"{API_ERROR_PREFIX} Server Error ({status_code}).{error_detail}"
            else:
                return (
                    f"{API_ERROR_PREFIX} Unexpected HTTP {status_code} during login.{error_detail}"
                )

    except httpx.TimeoutException:
        return f"{API_ERROR_PREFIX} Request timed out during login."
    except httpx.RequestError as req_err:
        return f"{API_ERROR_PREFIX} Network or connection error during login. Details: {req_err}"
    except Exception as e: # Catch other potential errors like JSONDecodeError if response parsing fails outside status check
        traceback.print_exc()
        return f"{API_ERROR_PREFIX} An unexpected error occurred during login. Details: {e}"
