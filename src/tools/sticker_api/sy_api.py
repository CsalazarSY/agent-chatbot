# pylint: disable=broad-exception-caught, unused-argument, too-many-lines
# agents/stickeryou/tools/sy_api.py
"""Defines tools (functions) for interacting with the StickerYou API."""

import asyncio
import json
import traceback
from typing import Optional, List, Dict, Union

import httpx

# Import necessary configuration constants
import config # Import the whole module to access globals & trigger refresh

# Import specific DTOs using absolute paths from src
from src.tools.sticker_api.dto_requests import (
    LoginRequest,
    SpecificPriceRequest,
    CreateOrderRequest,
    CreateOrderFromDesignsRequest,
    ListOrdersByStatusRequest
)
from src.tools.sticker_api.dto_responses import (
    LoginResponse,
    LoginStatusResponse,
    CountriesResponse,
    SpecificPriceResponse,
    PriceTiersResponse,
    ProductListResponse,
    OrderDetailResponse,
    OrderListResponse,
    SuccessResponse,
    DesignResponse,
    DesignPreviewResponse,
    OrderItemStatus,
    # OrderStatusId removed from here
)
# Import the common Enum
from src.tools.sticker_api.dto_common import OrderStatusId

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

    # Get the token using the accessor function
    auth_token = config.get_sy_api_token()
    if not auth_token:
        # If no dynamic token exists initially, try to refresh it via config trigger
        print("No initial dynamic token found. Triggering refresh via config...")
        refresh_successful = await config.trigger_sy_token_refresh() # Call config trigger
        if refresh_successful:
            auth_token = config.get_sy_api_token() # Re-read the token via accessor
            if not auth_token: # Should not happen if refresh_successful is True, but check defensively
                 print("!!! Config reported refresh success, but token is still None.")
                 return f"{API_ERROR_PREFIX} Internal Error - Token refresh state mismatch."
            print("Initial token obtained successfully via config trigger.")
        else:
             print("Initial token refresh failed via config trigger. Cannot proceed.")
             return f"{API_ERROR_PREFIX} Configuration Error - Could not obtain initial SY API auth token."

    headers = headers_base or {}
    headers["Authorization"] = f"Bearer {auth_token}"
    headers.setdefault("Accept", "application/json") # Ensure Accept header is present

    response: Optional[httpx.Response] = None
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
                    # If 200 OK but not JSON, return raw text.
                    # It might be the expected plain string response (e.g., tracking code).
                    try:
                        # Return the response object itself for the caller to handle .text
                        return response
                    except Exception as text_err:
                        return f"{API_ERROR_PREFIX} Status 200 OK, but failed to decode JSON and failed to read response text: {text_err}"

            elif response.status_code == 401 and retry_count < max_retries:
                print(f"SY API request received 401 Unauthorized. \n Triggering token refresh via config (Retry {retry_count + 1}/{max_retries})...")
                # Call the config trigger function
                refresh_successful = await config.trigger_sy_token_refresh()
                retry_count += 1

                if refresh_successful:
                    # Re-read the potentially updated token from config via accessor
                    auth_token = config.get_sy_api_token()
                    if not auth_token: # Should not happen, but check
                        print("!!! Config reported refresh success on 401, but token is still None.")
                        return f"{API_ERROR_PREFIX} Unauthorized (401) and subsequent refresh state mismatch."

                    headers["Authorization"] = f"Bearer {auth_token}" # Update header for retry
                    print("Token refreshed via config trigger. Retrying API call...")
                    await asyncio.sleep(0.5)
                    continue # Retry the request with the new token
                else:
                    print("Token refresh failed via config trigger. Aborting retries.")
                    return f"{API_ERROR_PREFIX} Unauthorized (401) and token refresh failed."

            else:
                # --- Error Message Extraction ---
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
                                         # Use raw message if nested parse fails
                                         error_message_detail = f" Detail: {error_json['message'][:200]}"
                                except json.JSONDecodeError:
                                     # Use raw message if not valid JSON string
                                     error_message_detail = f" Detail: {error_json['message'][:200]}"

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
    elif isinstance(result, httpx.Response): # Handle non-JSON 200 OK
        return f"{API_ERROR_PREFIX} Unexpected response format (non-JSON 200 OK) for create design."
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
    elif isinstance(result, httpx.Response): # Handle non-JSON 200 OK
        return f"{API_ERROR_PREFIX} Unexpected response format (non-JSON 200 OK) for design preview."
    else:
        return (
            f"{API_ERROR_PREFIX} Unexpected successful response type: "
            f"{type(result)}. Expected Dict."
        )


# --- Orders ---

async def sy_list_orders_by_status_get(
    status_id: int, # Can now use OrderStatusId if desired, but int for direct API call
) -> OrderListResponse | str:
    """
    (GET /v{version}/Orders/status/list/{status})
    Description: Retrieves a list of orders matching a specific status ID using a GET request.
    Allowed Scopes: [Dev, Internal]

    Parameters:
        status_id (int): The status ID to filter orders by. See OrderStatusId enum in dto_common.

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
    elif isinstance(result, httpx.Response): # Handle non-JSON 200 OK
        return f"{API_ERROR_PREFIX} Unexpected response format (non-JSON 200 OK) for list orders by status."
    else:
        return (
            f"{API_ERROR_PREFIX} Unexpected successful response type: "
            f"{type(result)}. Expected List."
        )


async def sy_list_orders_by_status_post(
    status_id: int, # Can use OrderStatusId if desired, but int for direct API call
    take: int = 100,
    skip: int = 0,
) -> OrderListResponse | str:
    """
    (POST /{version}/Orders/status/list)
    Description: Retrieves a paginated list of orders matching a specific status ID using a POST request.
    Allowed Scopes: [Dev, Internal]
    Note: Raw results should generally not be presented directly to the user.

    Parameters:
        status_id (int): The status ID (from OrderStatusId enum in dto_common) to filter orders by. Required.
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
    elif isinstance(result, httpx.Response): # Handle non-JSON 200 OK
        return f"{API_ERROR_PREFIX} Unexpected response format (non-JSON 200 OK) for list orders by status (POST)."
    else:
        return (
            f"{API_ERROR_PREFIX} Unexpected successful response type: "
            f"{type(result)}. Expected List."
        )


async def sy_create_order(
    order_data: Dict, # Expects data conforming to CreateOrderRequest
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
    elif isinstance(result, httpx.Response): # Handle non-JSON 200 OK
        return f"{API_ERROR_PREFIX} Unexpected response format (non-JSON 200 OK) for create order."
    else:
        return (
            f"{API_ERROR_PREFIX} Unexpected successful response type: "
            f"{type(result)}. Expected Dict."
        )


async def sy_create_order_from_designs(
    order_data: Dict, # Expects data conforming to CreateOrderFromDesignsRequest
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
    # Validate order_data against Pydantic model before sending?
    result = await _make_sy_api_request("POST", api_url, json_payload=order_data)

    if isinstance(result, dict):
        return result
    elif isinstance(result, str) and result.startswith(API_ERROR_PREFIX):
        return result
    elif isinstance(result, httpx.Response): # Handle non-JSON 200 OK
        return f"{API_ERROR_PREFIX} Unexpected response format (non-JSON 200 OK) for create order from designs."
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
    elif isinstance(result, httpx.Response): # Handle non-JSON 200 OK
        return f"{API_ERROR_PREFIX} Unexpected response format (non-JSON 200 OK) for get order details."
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
    # Handle non-JSON 200 OK for PUT (e.g., empty body)
    elif isinstance(result, httpx.Response) and result.status_code == 200:
        # Success, but no JSON body - return a generic success message or structure
        return {"success": True, "message": f"Order {order_id} cancellation request processed (received 200 OK)."}
    elif isinstance(result, str) and result.startswith(API_ERROR_PREFIX):
        if "Not Found (404)" in result:
            return f"{API_ERROR_PREFIX} Order not found (404)."
        return result
    else:
        # Consider if a plain string might be a valid success confirmation
        return (
            f"{API_ERROR_PREFIX} Unexpected successful response type: "
            f"{type(result)}. Expected Dict or 200 OK Response."
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
    elif isinstance(result, httpx.Response): # Handle non-JSON 200 OK
         return f"{API_ERROR_PREFIX} Unexpected response format (non-JSON 200 OK) for get order item statuses."
    else:
        return (
            f"{API_ERROR_PREFIX} Unexpected successful response type: "
            f"{type(result)}. Expected List."
        )


async def sy_get_order_tracking(
    order_id: str,
) -> Dict | str:
    """
    (GET /{version}/Orders/{id}/trackingcode)
    Description: Retrieves the shipping tracking information (code, URL, carrier) for a shipped order.
    Allowed Scopes: [User, Dev, Internal]
    Note: This endpoint returns a **raw string** response containing only the tracking code on success (200 OK).
          The helper function `_make_sy_api_request` will return the `httpx.Response` object in this case.

    Parameters:
        order_id (str): The StickerYou identifier for the order.

    Returns:
        Dict | str: A dictionary `{"tracking_code": str}` on success, or an error string.
    """
    api_url = f"{config.API_BASE_URL}/{config.API_VERSION}/Orders/{order_id}/trackingcode"
    result = await _make_sy_api_request("GET", api_url)

    # Check if the result is an httpx.Response object (indicating 200 OK, non-JSON)
    if isinstance(result, httpx.Response):
        if result.status_code == 200:
            try:
                tracking_code = result.text
                if tracking_code:
                    # Return structured dict on success
                    return {"tracking_code": tracking_code}
                else:
                    # Handle empty string case
                    return f"{API_ERROR_PREFIX} Tracking code retrieved successfully but was empty."
            except Exception as e:
                return f"{API_ERROR_PREFIX} Error reading tracking code text from response: {e}"
        else:
            # Should not happen if helper worked, but handle defensively
            return f"{API_ERROR_PREFIX} Received unexpected status code {result.status_code} in response object for tracking code."

    # Handle error strings from the helper
    elif isinstance(result, str) and result.startswith(API_ERROR_PREFIX):
        if "Not Found (404)" in result:
            # Keep specific error for order not found / no tracking yet
            return f"{API_ERROR_PREFIX} No tracking code available (404)."
        return result # Return other specific errors

    # Handle unexpected dictionary or other types (shouldn't occur for this endpoint on success)
    else:
        return f"{API_ERROR_PREFIX} Unexpected result type ({type(result)}) for tracking code request."

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
    elif isinstance(result, httpx.Response): # Handle non-JSON 200 OK
         return f"{API_ERROR_PREFIX} Unexpected response format (non-JSON 200 OK) for list products."
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
    elif isinstance(result, httpx.Response): # Handle non-JSON 200 OK
         return f"{API_ERROR_PREFIX} Unexpected response format (non-JSON 200 OK) for get price tiers."
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
    elif isinstance(result, httpx.Response): # Handle non-JSON 200 OK
         return f"{API_ERROR_PREFIX} Unexpected response format (non-JSON 200 OK) for get specific price."
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
    if isinstance(result, dict):
        # If it's the expected dict structure
        return result
    elif isinstance(result, list):
        return f"{API_ERROR_PREFIX} Received unexpected list format, expected dict wrapping countries list."
    elif isinstance(result, str) and result.startswith(API_ERROR_PREFIX):
        return result
    elif isinstance(result, httpx.Response): # Handle non-JSON 200 OK
         return f"{API_ERROR_PREFIX} Unexpected response format (non-JSON 200 OK) for list countries."
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
                 Returns a structured dictionary indicating status.
    Allowed Scopes: [Internal, Dev] (Used by the request helper for token checks).

    Parameters: None

    Request body example: None (GET request)

    Response body template (on success - 200 OK, type: LoginStatusResponse):
        {
            "name": str,
            "authenticated": bool
        }

    Returns:
        Dict | str: A dictionary like {"status": "success", "details": {...}} or
                     {"status": "failed", "message": "..."} on failure, or an error string.
    """
    api_url = f"{config.API_BASE_URL}/users/login"
    result = await _make_sy_api_request("GET", api_url, max_retries=0)

    if isinstance(result, dict):
        # Successful call, return custom status dict
        return {
            "status": "success",
            "message": "Token appears valid (received 200 OK with data).",
            "details": result
        }
    elif isinstance(result, str) and result.startswith(API_ERROR_PREFIX):
        # Specific handling for 401 on verify
        if "Unauthorized (401)" in result:
            return {"status": "failed", "message": "Token is invalid (Unauthorized 401)."}
        # Return other detailed errors from helper as a string
        return result
    elif isinstance(result, httpx.Response): # Handle non-JSON 200 OK
         # Treat non-JSON 200 OK as potentially valid but lacking expected data
         if result.status_code == 200:
            return {
            "status": "success",
            "message": "Token appears valid (received 200 OK, but no JSON data).",
            "details": None # Or result.text if needed
            }
         else:
            return f"{API_ERROR_PREFIX} Unexpected response status {result.status_code} in response object during verification."
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
