# agents/stickeryou/tools/sy_api.py
import httpx
import json
import traceback
import asyncio # Added for retry delay
from typing import Optional, Any, List, Dict, Callable, Awaitable

# Import necessary configuration constants and the refresh function
import config # Import the whole module to access globals

# Standardized Error Prefix
ERROR_PREFIX = "SY_TOOL_FAILED:"

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
    if not config.API_BASE_URL: return f"{ERROR_PREFIX} Configuration Error - Missing API Base URL."

    auth_token = config.SY_API_AUTH_TOKEN_DYNAMIC or config.API_AUTH_TOKEN # Prioritize dynamic
    if not auth_token: return f"{ERROR_PREFIX} Configuration Error - No SY API auth token available (static or dynamic)."

    headers = headers_base or {}
    headers["Authorization"] = f"Bearer {auth_token}"
    headers.setdefault("Accept", "application/json") # Ensure Accept header is present

    response = None
    retry_count = 0

    while retry_count <= max_retries:
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                if method.upper() == "GET":
                    response = await client.get(api_url, headers=headers)
                elif method.upper() == "POST":
                    headers.setdefault("Content-Type", "application/json") # Ensure Content-Type for POST
                    response = await client.post(api_url, headers=headers, json=json_payload)
                elif method.upper() == "DELETE":
                    response = await client.delete(api_url, headers=headers)
                else:
                    return f"{ERROR_PREFIX} Unsupported HTTP method: {method}"

            if response.status_code == 200:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    return f"{ERROR_PREFIX} Failed to decode successful JSON response (Status 200)."

            elif response.status_code == 401 and retry_count < max_retries:
                print(f"SY API request received 401 Unauthorized. Attempting token refresh (Retry {retry_count + 1}/{max_retries})...")
                refresh_successful = await config.refresh_sy_token()
                retry_count += 1

                if refresh_successful and config.SY_API_AUTH_TOKEN_DYNAMIC:
                    # Update token for the retry
                    auth_token = config.SY_API_AUTH_TOKEN_DYNAMIC
                    headers["Authorization"] = f"Bearer {auth_token}"
                    print("Token refreshed. Retrying API call...")
                    await asyncio.sleep(0.5) # Small delay before retry
                    continue # Go to next iteration of the while loop
                else:
                    print("Token refresh failed or new token not available. Aborting retries.")
                    return f"{ERROR_PREFIX} Unauthorized (401) and token refresh failed."

            else:
                # Handle non-401 errors or final 401 failure
                error_body = response.text[:500]
                if response.status_code == 401: return f"{ERROR_PREFIX} Unauthorized (401) after retries."
                elif response.status_code == 400: return f"{ERROR_PREFIX} Bad Request (400). Check parameters/payload."
                elif response.status_code == 404: return f"{ERROR_PREFIX} Not Found (404)."
                elif response.status_code >= 500: return f"{ERROR_PREFIX} Server Error ({response.status_code})."
                else: return f"{ERROR_PREFIX} Unexpected HTTP {response.status_code}. Body: {error_body}"

        except httpx.TimeoutException:
            return f"{ERROR_PREFIX} Request timed out."
        except httpx.RequestError as req_err:
            return f"{ERROR_PREFIX} Network or connection error. Details: {req_err}"
        except json.JSONDecodeError:
            # This JSONDecodeError is for decoding the *error* response, not success
            status_code = response.status_code if response else 'Unknown'
            return f"{ERROR_PREFIX} Failed to decode error response as JSON. Status: {status_code}"
        except Exception as e:
            traceback.print_exc() # Print traceback for unexpected errors
            return f"{ERROR_PREFIX} An unexpected error occurred. Details: {e}"

        # If we got here without continuing or returning, it means an error occurred
        # Break the loop for non-401 errors or if max_retries is reached for 401
        break

    # Fallback if loop finishes unexpectedly (shouldn't happen with current logic)
    return f"{ERROR_PREFIX} API request failed after processing."


# --- Tool Functions (Refactored to use _make_sy_api_request) ---
# --- Designs ---
async def sy_create_design(
    product_id: int,
    width: float,
    height: float,
    image_base64: str,
) -> Dict | str:
    """(POST /api/v{version}/Designs/new) Sends a new design to StickerYou."""
    api_url = f"{config.API_BASE_URL}/api/{config.API_VERSION}/Designs/new"
    payload = {"productId": product_id, "width": width, "height": height, "imageBase64": image_base64}
    result = await _make_sy_api_request("POST", api_url, json_payload=payload, timeout=60.0) # Increased timeout

    # POST requests often return simple success messages, ensure Dict is returned if expected
    if isinstance(result, dict):
        return result
    elif isinstance(result, str) and result.startswith(ERROR_PREFIX):
        return result
    else: # Handle unexpected success types (e.g., list, plain string)
        return f"{ERROR_PREFIX} Unexpected successful response type: {type(result)}. Expected Dict."


async def sy_get_design_preview(
    design_id: str,
) -> Dict | str:
    """(GET /api/v{version}/Designs/{designId}/preview) Returns a design preview using its Design ID.
       Note: API docs show an *order* response. Returns the raw response."""
    api_url = f"{config.API_BASE_URL}/api/{config.API_VERSION}/Designs/{design_id}/preview"
    result = await _make_sy_api_request("GET", api_url)

    if isinstance(result, dict):
        return result
    elif isinstance(result, str) and result.startswith(ERROR_PREFIX):
        return result
    else:
        return f"{ERROR_PREFIX} Unexpected successful response type: {type(result)}. Expected Dict."


# --- Orders ---

async def sy_list_orders_by_status_get(
    status_id: int,
) -> List[Dict] | str:
    """(GET /v{version}/Orders/status/list/{status}) Lists orders matching a specific status using a path parameter (GET)."""
    api_url = f"{config.API_BASE_URL}/v{config.API_VERSION}/Orders/status/list/{status_id}"
    result = await _make_sy_api_request("GET", api_url)

    if isinstance(result, list):
        return result
    elif isinstance(result, str) and result.startswith(ERROR_PREFIX):
        # Specific check for 404 which might mean invalid status ID for this endpoint style
        if "Not Found (404)" in result:
             return f"{ERROR_PREFIX} Invalid Status ID {status_id} provided? (404)."
        return result
    else:
        return f"{ERROR_PREFIX} Unexpected successful response type: {type(result)}. Expected List."


async def sy_list_orders_by_status_post(
    status_id: int,
    take: int = 100,
    skip: int = 0,
) -> List[Dict] | str:
    """(POST /v{version}/Orders/status/list) Lists orders matching a specific status using a request body (POST)."""
    api_url = f"{config.API_BASE_URL}/v{config.API_VERSION}/Orders/status/list"
    payload = {"take": take, "skip": skip, "status": status_id}
    result = await _make_sy_api_request("POST", api_url, json_payload=payload)

    if isinstance(result, list):
        return result
    elif isinstance(result, str) and result.startswith(ERROR_PREFIX):
        return result
    else:
        return f"{ERROR_PREFIX} Unexpected successful response type: {type(result)}. Expected List."


async def sy_create_order(
    order_data: Dict,
) -> Dict | str:
    """(POST /v{version}/Orders/new) Sends a new order"""
    api_url = f"{config.API_BASE_URL}/v{config.API_VERSION}/Orders/new"
    result = await _make_sy_api_request("POST", api_url, json_payload=order_data)

    if isinstance(result, dict):
        return result
    elif isinstance(result, str) and result.startswith(ERROR_PREFIX):
        return result
    else:
        return f"{ERROR_PREFIX} Unexpected successful response type: {type(result)}. Expected Dict."


async def sy_create_order_from_designs(
    order_data: Dict,
) -> Dict | str:
    """(POST /v{version}/Orders/designs/new) Sends a new order with designs"""
    api_url = f"{config.API_BASE_URL}/v{config.API_VERSION}/Orders/designs/new"
    result = await _make_sy_api_request("POST", api_url, json_payload=order_data)

    if isinstance(result, dict):
        return result
    elif isinstance(result, str) and result.startswith(ERROR_PREFIX):
        return result
    else:
        return f"{ERROR_PREFIX} Unexpected successful response type: {type(result)}. Expected Dict."


async def sy_get_order_details(
    order_id: str,
) -> Dict | str:
    """(GET /v{version}/Orders/{id}) Returns order details by its identifier."""
    api_url = f"{config.API_BASE_URL}/v{config.API_VERSION}/Orders/{order_id}"
    result = await _make_sy_api_request("GET", api_url)

    if isinstance(result, dict):
        return result
    elif isinstance(result, str) and result.startswith(ERROR_PREFIX):
        if "Not Found (404)" in result: return f"{ERROR_PREFIX} Order not found (404)." # More specific error
        return result
    else:
        return f"{ERROR_PREFIX} Unexpected successful response type: {type(result)}. Expected Dict."


async def sy_cancel_order(
    order_id: str,
) -> Dict | str:
    """(PUT /v{version}/Orders/{id}/cancel) Cancels an order using its identifier."""
    api_url = f"{config.API_BASE_URL}/v{config.API_VERSION}/Orders/{order_id}/cancel"
    result = await _make_sy_api_request("PUT", api_url)

    if isinstance(result, dict):
        return result
    # The API might return non-JSON on successful DELETE, check docs or handle based on observation
    # Example: elif isinstance(result, str) and not result.startswith(ERROR_PREFIX): return {"status": "success", "message": result}
    elif isinstance(result, str) and result.startswith(ERROR_PREFIX):
         if "Not Found (404)" in result: return f"{ERROR_PREFIX} Order not found (404)."
         return result
    else:
        return f"{ERROR_PREFIX} Unexpected successful response type: {type(result)}. Expected Dict (or simple confirmation)."


async def sy_get_order_item_statuses(
    order_id: str,
) -> List[Dict] | str:
    """(GET /v{version}/Orders/{id}/items/status) Gets the status for all items within a specific order."""
    api_url = f"{config.API_BASE_URL}/v{config.API_VERSION}/Orders/{order_id}/items/status"
    result = await _make_sy_api_request("GET", api_url)

    if isinstance(result, list):
        return result
    elif isinstance(result, str) and result.startswith(ERROR_PREFIX):
        if "Not Found (404)" in result: return f"{ERROR_PREFIX} Order not found (404)."
        return result
    else:
        return f"{ERROR_PREFIX} Unexpected successful response type: {type(result)}. Expected List."


async def sy_get_order_tracking(
    order_id: str,
) -> Dict | str:
    """(GET /v{version}/Orders/{id}/trackingcode) Retrieves the tracking code for a specific order."""
    api_url = f"{config.API_BASE_URL}/v{config.API_VERSION}/Orders/{order_id}/trackingcode"
    result = await _make_sy_api_request("GET", api_url)

    if isinstance(result, dict):
        return result
    elif isinstance(result, str) and result.startswith(ERROR_PREFIX):
        # API might return 404 if tracking not available *yet*, not just if order doesn't exist
        if "Not Found (404)" in result: return f"{ERROR_PREFIX} Tracking not available or order not found (404)."
        return result
    else:
        return f"{ERROR_PREFIX} Unexpected successful response type: {type(result)}. Expected Dict."


# --- Pricing ---

async def sy_list_products(
) -> Dict | str:
    """(GET /api/v{version}/Pricing/list) Returns a list of available products and their configurable options."""
    api_url = f"{config.API_BASE_URL}/api/{config.API_VERSION}/Pricing/list"
    result = await _make_sy_api_request("GET", api_url)

    # Check if it's a dict (as per doc sig) or list (common pattern)
    if isinstance(result, (dict, list)):
        return result
    elif isinstance(result, str) and result.startswith(ERROR_PREFIX):
        return result
    else:
        return f"{ERROR_PREFIX} Unexpected successful response type: {type(result)}. Expected Dict or List."


async def sy_get_price_tiers(
    product_id: int,
    width: float,
    height: float,
    country_code: Optional[str] = None,
    currency_code: Optional[str] = None,
    accessory_options: Optional[List[Dict]] = None,
    quantity: Optional[int] = None,
) -> Dict | str:
    """(POST /api/v{version}/Pricing/{productId}/pricings) Returns a list of prices for different quantity tiers for a specific product."""
    api_url = f"{config.API_BASE_URL}/api/{config.API_VERSION}/Pricing/{product_id}/pricings"
    payload = {
        "width": float(width), "height": float(height),
        "countryCode": country_code or config.DEFAULT_COUNTRY_CODE,
        "currencyCode": currency_code or config.DEFAULT_CURRENCY_CODE,
        "accessoryOptions": accessory_options or [],
    }
    if quantity is not None: payload["quantity"] = int(quantity)

    result = await _make_sy_api_request("POST", api_url, json_payload=payload)

    if isinstance(result, dict):
        return result
    elif isinstance(result, str) and result.startswith(ERROR_PREFIX):
        return result
    else:
        return f"{ERROR_PREFIX} Unexpected successful response type: {type(result)}. Expected Dict."

async def sy_get_specific_price(
    product_id: int,
    width: float,
    height: float,
    quantity: int,
    country_code: Optional[str] = None,
    currency_code: Optional[str] = None,
    accessory_options: Optional[List[Dict]] = None
) -> Dict | str:
    """(POST /api/v{version}/Pricing/{productId}/pricing) Calls the SY pricing API for a *specific* quantity of a product."""
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
    elif isinstance(result, str) and result.startswith(ERROR_PREFIX):
        return result
    else:
        return f"{ERROR_PREFIX} Unexpected successful response type: {type(result)}. Expected Dict."

async def sy_list_countries(
) -> Dict | str:
    """(POST /api/v{version}/Pricing/countries) Returns a list of supported countries for pricing/shipping."""
    api_url = f"{config.API_BASE_URL}/api/{config.API_VERSION}/Pricing/countries"
    result = await _make_sy_api_request("POST", api_url)

    if isinstance(result, dict):
        return result
    elif isinstance(result, str) and result.startswith(ERROR_PREFIX):
        return result
    else:
        return f"{ERROR_PREFIX} Unexpected successful response type: {type(result)}. Expected Dict."

# --- Users ---

async def sy_verify_login(
) -> Dict | str:
    """(GET /users/login) Verifies if the current authentication token is valid."""
    api_url = f"{config.API_BASE_URL}/users/login"
    result = await _make_sy_api_request("GET", api_url, max_retries=0) # No retry on verify, just report status

    if isinstance(result, dict):
        # A successful GET to login might return user info or just 200 OK
        return {"status": "success", "message": "Token appears valid (received 200 OK or data).", "details": result}
    elif isinstance(result, str) and result.startswith(ERROR_PREFIX):
        # Specifically handle the expected failure modes for verification
        if "Unauthorized (401)" in result: return {"status": "failed", "message": "Token is invalid (Unauthorized 401)."}
        elif "timed out" in result: return f"{ERROR_PREFIX} Verification request timed out."
        elif "Network or connection error" in result: return f"{ERROR_PREFIX} Network error during verification."
        else: return result # Return other SY_TOOL_FAILED errors
    else:
        return f"{ERROR_PREFIX} Unexpected response type during verification: {type(result)}."


async def sy_perform_login(
    username: str,
    password: str,
) -> Dict | str:
    """(POST /users/login) Performs user login to obtain an authentication token."""
    if not config.API_BASE_URL: return f"{ERROR_PREFIX} Configuration Error - Missing API Base URL."
    # No auth token needed for login request itself

    api_url = f"{config.API_BASE_URL}/users/login" # Corrected URL pattern (no version)
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    payload = {"userName": username, "password": password}

    response = None
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(api_url, headers=headers, json=payload)

        if response.status_code == 200:
            try:
                # Expecting {"token": "...", "expirationMinutes": "..."}
                return response.json()
            except json.JSONDecodeError:
                return f"{ERROR_PREFIX} Failed to decode successful JSON response from login (Status 200)."
        else:
            error_body = response.text[:500]
            # Assuming 400/401 for bad credentials, but API might vary
            if response.status_code == 400: return f"{ERROR_PREFIX} Bad Request (400). Invalid credentials or request format?"
            elif response.status_code == 401: return f"{ERROR_PREFIX} Unauthorized (401). Invalid username or password?"
            elif response.status_code >= 500: return f"{ERROR_PREFIX} Server Error ({response.status_code})."
            else: return f"{ERROR_PREFIX} Unexpected HTTP {response.status_code} during login. Body: {error_body}"

    except httpx.TimeoutException:
        return f"{ERROR_PREFIX} Request timed out during login."
    except httpx.RequestError as req_err:
        return f"{ERROR_PREFIX} Network or connection error during login. Details: {req_err}"
    except json.JSONDecodeError:
        status_code = response.status_code if response else 'Unknown'
        return f"{ERROR_PREFIX} Failed to decode error response as JSON during login. Status: {status_code}"
    except Exception as e:
        traceback.print_exc() # Print traceback for unexpected errors
        return f"{ERROR_PREFIX} An unexpected error occurred during login. Details: {e}"
