# agents/stickeryou/tools/sy_api.py
import httpx
import json
import traceback
from typing import Optional, Any, List, Dict

# Import necessary configuration constants from config.py
from config import (
    API_BASE_URL,
    API_VERSION,
    API_AUTH_TOKEN,
    DEFAULT_COUNTRY_CODE,
    DEFAULT_CURRENCY_CODE
)

# Standardized Error Prefix
ERROR_PREFIX = "SY_TOOL_FAILED:"

# --- Tool Functions ---
# --- Designs ---
async def sy_create_design(
    product_id: int,
    width: float,
    height: float,
    image_base64: str,
) -> Dict | str:
    """(POST /api/v{version}/Designs/new) Sends a new design to StickerYou."""
    if not API_BASE_URL: return f"{ERROR_PREFIX} Configuration Error - Missing API Base URL."
    if not API_AUTH_TOKEN: return f"{ERROR_PREFIX} Configuration Error - Missing API authentication token."

    api_url = f"{API_BASE_URL}/api/{API_VERSION}/Designs/new"
    headers = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": f"Bearer {API_AUTH_TOKEN}"}
    payload = {"productId": product_id, "width": width, "height": height, "imageBase64": image_base64}

    response = None
    try:
        async with httpx.AsyncClient(timeout=60.0) as client: # Increased timeout for potential image upload
            response = await client.post(api_url, headers=headers, json=payload)

        if response.status_code == 200:
            try:
                # Expecting {"success": true, "message": "string"}
                return response.json()
            except json.JSONDecodeError:
                return f"{ERROR_PREFIX} Failed to decode successful JSON response (Status 200)."
        else:
            error_body = response.text[:500]
            if response.status_code == 401: return f"{ERROR_PREFIX} Unauthorized (401)."
            elif response.status_code == 400: return f"{ERROR_PREFIX} Bad Request (400). Check design parameters/image format."
            elif response.status_code >= 500: return f"{ERROR_PREFIX} Server Error ({response.status_code})."
            else: return f"{ERROR_PREFIX} Unexpected HTTP {response.status_code}. Body: {error_body}"

    except httpx.TimeoutException:
        return f"{ERROR_PREFIX} Request timed out (create design)."
    except httpx.RequestError as req_err:
        return f"{ERROR_PREFIX} Network or connection error. Details: {req_err}"
    except json.JSONDecodeError:
        status_code = response.status_code if response else 'Unknown'
        return f"{ERROR_PREFIX} Failed to decode error response as JSON. Status: {status_code}"
    except Exception as e:
        return f"{ERROR_PREFIX} An unexpected error occurred. Details: {e}"


async def sy_get_design_preview(
    design_id: str,
) -> Dict | str:
    """(GET /api/v{version}/Designs/{designId}/preview) Returns a design preview using its Design ID.
       Note: API docs show an *order* response. Returns the raw response."""
    if not API_BASE_URL: return f"{ERROR_PREFIX} Configuration Error - Missing API Base URL."
    if not API_AUTH_TOKEN: return f"{ERROR_PREFIX} Configuration Error - Missing API authentication token."

    api_url = f"{API_BASE_URL}/api/{API_VERSION}/Designs/{design_id}/preview"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {API_AUTH_TOKEN}"}

    response = None
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(api_url, headers=headers)

        if response.status_code == 200:
            try:
                return response.json() # Return whatever the API gives
            except json.JSONDecodeError:
                return f"{ERROR_PREFIX} Failed to decode successful JSON response (Status 200)."
        else:
            error_body = response.text[:500]
            if response.status_code == 404: return f"{ERROR_PREFIX} Design not found (404)."
            elif response.status_code == 401: return f"{ERROR_PREFIX} Unauthorized (401)."
            elif response.status_code >= 500: return f"{ERROR_PREFIX} Server Error ({response.status_code})."
            else: return f"{ERROR_PREFIX} Unexpected HTTP {response.status_code}. Body: {error_body}"

    except httpx.TimeoutException:
        return f"{ERROR_PREFIX} Request timed out."
    except httpx.RequestError as req_err:
        return f"{ERROR_PREFIX} Network or connection error. Details: {req_err}"
    except json.JSONDecodeError:
        status_code = response.status_code if response else 'Unknown'
        return f"{ERROR_PREFIX} Failed to decode error response as JSON. Status: {status_code}"
    except Exception as e:
        return f"{ERROR_PREFIX} An unexpected error occurred. Details: {e}"


# --- Orders ---

async def sy_list_orders_by_status_get(
    status_id: int,
) -> List[Dict] | str:
    """(GET /v{version}/Orders/status/list/{status}) Lists orders matching a specific status using a path parameter (GET)."""
    if not API_BASE_URL: return f"{ERROR_PREFIX} Configuration Error - Missing API Base URL."
    if not API_AUTH_TOKEN: return f"{ERROR_PREFIX} Configuration Error - Missing API authentication token."

    api_url = f"{API_BASE_URL}/v{API_VERSION}/Orders/status/list/{status_id}"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {API_AUTH_TOKEN}"}

    response = None
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(api_url, headers=headers)

        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list): return data
                else: return f"{ERROR_PREFIX} Unexpected response type: {type(data)}. Expected list."
            except json.JSONDecodeError:
                return f"{ERROR_PREFIX} Failed to decode successful JSON response (Status 200)."
        else:
            error_body = response.text[:500]
            if response.status_code == 401: return f"{ERROR_PREFIX} Unauthorized (401)."
            elif response.status_code == 400: return f"{ERROR_PREFIX} Bad Request (400). Invalid status ID?"
            elif response.status_code == 404: return f"{ERROR_PREFIX} Invalid Status ID {status_id} provided? (404)."
            elif response.status_code >= 500: return f"{ERROR_PREFIX} Server Error ({response.status_code})."
            else: return f"{ERROR_PREFIX} Unexpected HTTP {response.status_code}. Body: {error_body}"

    except httpx.TimeoutException:
        return f"{ERROR_PREFIX} Request timed out."
    except httpx.RequestError as req_err:
        return f"{ERROR_PREFIX} Network or connection error. Details: {req_err}"
    except json.JSONDecodeError:
        status_code = response.status_code if response else 'Unknown'
        return f"{ERROR_PREFIX} Failed to decode error response as JSON. Status: {status_code}"
    except Exception as e:
        return f"{ERROR_PREFIX} An unexpected error occurred. Details: {e}"


async def sy_list_orders_by_status_post(
    status_id: int,
    take: int = 100,
    skip: int = 0,
) -> List[Dict] | str:
    """(POST /v{version}/Orders/status/list) Lists orders matching a specific status using a request body (POST)."""
    if not API_BASE_URL: return f"{ERROR_PREFIX} Configuration Error - Missing API Base URL."
    if not API_AUTH_TOKEN: return f"{ERROR_PREFIX} Configuration Error - Missing API authentication token."

    api_url = f"{API_BASE_URL}/v{API_VERSION}/Orders/status/list"
    headers = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": f"Bearer {API_AUTH_TOKEN}"}
    payload = {"take": take, "skip": skip, "status": status_id}

    response = None
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(api_url, headers=headers, json=payload)

        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list): return data
                else: return f"{ERROR_PREFIX} Unexpected response type: {type(data)}. Expected list."
            except json.JSONDecodeError:
                return f"{ERROR_PREFIX} Failed to decode successful JSON response (Status 200)."
        else:
            error_body = response.text[:500]
            if response.status_code == 401: return f"{ERROR_PREFIX} Unauthorized (401)."
            elif response.status_code == 400: return f"{ERROR_PREFIX} Bad Request (400). Invalid status ID or pagination params?"
            elif response.status_code >= 500: return f"{ERROR_PREFIX} Server Error ({response.status_code})."
            else: return f"{ERROR_PREFIX} Unexpected HTTP {response.status_code}. Body: {error_body}"

    except httpx.TimeoutException:
        return f"{ERROR_PREFIX} Request timed out."
    except httpx.RequestError as req_err:
        return f"{ERROR_PREFIX} Network or connection error. Details: {req_err}"
    except json.JSONDecodeError:
        status_code = response.status_code if response else 'Unknown'
        return f"{ERROR_PREFIX} Failed to decode error response as JSON. Status: {status_code}"
    except Exception as e:
        return f"{ERROR_PREFIX} An unexpected error occurred. Details: {e}"


async def sy_create_order(
    order_data: Dict,
) -> Dict | str:
    """(POST /v{version}/Orders/new) Sends a new order"""
    if not API_BASE_URL: return f"{ERROR_PREFIX} Configuration Error - Missing API Base URL."
    if not API_AUTH_TOKEN: return f"{ERROR_PREFIX} Configuration Error - Missing API authentication token."

    api_url = f"{API_BASE_URL}/v{API_VERSION}/Orders/new"
    headers = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": f"Bearer {API_AUTH_TOKEN}"}

    response = None
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(api_url, headers=headers, json=order_data)

        if response.status_code == 200:
            try:
                # Expecting {"success": true, "message": "string"}
                return response.json()
            except json.JSONDecodeError:
                return f"{ERROR_PREFIX} Failed to decode successful JSON response (Status 200)."
        else:
            error_body = response.text[:500]
            if response.status_code == 401: return f"{ERROR_PREFIX} Unauthorized (401)."
            elif response.status_code == 400: return f"{ERROR_PREFIX} Bad Request (400). Check order data format/product IDs/artwork URLs."
            elif response.status_code >= 500: return f"{ERROR_PREFIX} Server Error ({response.status_code})."
            else: return f"{ERROR_PREFIX} Unexpected HTTP {response.status_code}. Body: {error_body}"

    except httpx.TimeoutException:
        return f"{ERROR_PREFIX} Request timed out."
    except httpx.RequestError as req_err:
        return f"{ERROR_PREFIX} Network or connection error. Details: {req_err}"
    except json.JSONDecodeError:
        status_code = response.status_code if response else 'Unknown'
        return f"{ERROR_PREFIX} Failed to decode error response as JSON. Status: {status_code}"
    except Exception as e:
        return f"{ERROR_PREFIX} An unexpected error occurred. Details: {e}"


async def sy_create_order_from_designs(
    order_data: Dict,
) -> Dict | str:
    """(POST /v{version}/Orders/designs/new) Sends a new order with designs"""
    if not API_BASE_URL: return f"{ERROR_PREFIX} Configuration Error - Missing API Base URL."
    if not API_AUTH_TOKEN: return f"{ERROR_PREFIX} Configuration Error - Missing API authentication token."

    api_url = f"{API_BASE_URL}/v{API_VERSION}/Orders/designs/new"
    headers = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": f"Bearer {API_AUTH_TOKEN}"}

    response = None
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(api_url, headers=headers, json=order_data)

        if response.status_code == 200:
            try:
                 # Expecting {"success": true, "message": "string"}
                return response.json()
            except json.JSONDecodeError:
                return f"{ERROR_PREFIX} Failed to decode successful JSON response (Status 200)."
        else:
            error_body = response.text[:500]
            if response.status_code == 401: return f"{ERROR_PREFIX} Unauthorized (401)."
            elif response.status_code == 400: return f"{ERROR_PREFIX} Bad Request (400). Check order data format or design IDs."
            elif response.status_code >= 500: return f"{ERROR_PREFIX} Server Error ({response.status_code})."
            else: return f"{ERROR_PREFIX} Unexpected HTTP {response.status_code}. Body: {error_body}"

    except httpx.TimeoutException:
        return f"{ERROR_PREFIX} Request timed out."
    except httpx.RequestError as req_err:
        return f"{ERROR_PREFIX} Network or connection error. Details: {req_err}"
    except json.JSONDecodeError:
        status_code = response.status_code if response else 'Unknown'
        return f"{ERROR_PREFIX} Failed to decode error response as JSON. Status: {status_code}"
    except Exception as e:
        return f"{ERROR_PREFIX} An unexpected error occurred. Details: {e}"


async def sy_get_order_details(
    order_id: str,
) -> Dict | str:
    """(GET /v{version}/Orders/{id}) Returns order details by its identifier."""
    if not API_BASE_URL: return f"{ERROR_PREFIX} Configuration Error - Missing API Base URL."
    if not API_AUTH_TOKEN: return f"{ERROR_PREFIX} Configuration Error - Missing API authentication token."

    api_url = f"{API_BASE_URL}/v{API_VERSION}/Orders/{order_id}"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {API_AUTH_TOKEN}"}

    response = None
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(api_url, headers=headers)

        if response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError:
                return f"{ERROR_PREFIX} Failed to decode successful JSON response (Status 200)."
        else:
            error_body = response.text[:500]
            if response.status_code == 404: return f"{ERROR_PREFIX} Order not found (404)."
            elif response.status_code == 401: return f"{ERROR_PREFIX} Unauthorized (401)."
            elif response.status_code >= 500: return f"{ERROR_PREFIX} Server Error ({response.status_code})."
            else: return f"{ERROR_PREFIX} Unexpected HTTP {response.status_code}. Body: {error_body}"

    except httpx.TimeoutException:
        return f"{ERROR_PREFIX} Request timed out."
    except httpx.RequestError as req_err:
        return f"{ERROR_PREFIX} Network or connection error. Details: {req_err}"
    except json.JSONDecodeError:
        status_code = response.status_code if response else 'Unknown'
        return f"{ERROR_PREFIX} Failed to decode error response as JSON. Status: {status_code}"
    except Exception as e:
        return f"{ERROR_PREFIX} An unexpected error occurred. Details: {e}"


async def sy_cancel_order(
    order_id: str,
) -> Dict | str:
    """(PUT /v{version}/Orders/{id}/cancel) Cancels an order using its identifier."""
    if not API_BASE_URL: return f"{ERROR_PREFIX} Configuration Error - Missing API Base URL."
    if not API_AUTH_TOKEN: return f"{ERROR_PREFIX} Configuration Error - Missing API authentication token."

    api_url = f"{API_BASE_URL}/v{API_VERSION}/Orders/{order_id}/cancel"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {API_AUTH_TOKEN}"}

    response = None
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.put(api_url, headers=headers)

        if response.status_code == 200:
            try:
                # Assuming PUT returns the updated order details
                return response.json()
            except json.JSONDecodeError:
                # Some APIs might return 200 OK with no body on successful PUT/DELETE
                return {"success": True, "message": "Order cancellation processed successfully (Status 200)."}
        else:
            error_body = response.text[:500]
            if response.status_code == 404: return f"{ERROR_PREFIX} Order not found (404)."
            elif response.status_code == 401: return f"{ERROR_PREFIX} Unauthorized (401)."
            elif response.status_code == 400: return f"{ERROR_PREFIX} Bad Request (400). Order may already be cancelled or unable to be cancelled."
            elif response.status_code >= 500: return f"{ERROR_PREFIX} Server Error ({response.status_code})."
            else: return f"{ERROR_PREFIX} Unexpected HTTP {response.status_code}. Body: {error_body}"

    except httpx.TimeoutException:
        return f"{ERROR_PREFIX} Request timed out."
    except httpx.RequestError as req_err:
        return f"{ERROR_PREFIX} Network or connection error. Details: {req_err}"
    except json.JSONDecodeError:
        status_code = response.status_code if response else 'Unknown'
        return f"{ERROR_PREFIX} Failed to decode error response as JSON. Status: {status_code}"
    except Exception as e:
        return f"{ERROR_PREFIX} An unexpected error occurred. Details: {e}"


async def sy_get_order_item_statuses(
    order_id: str,
) -> List[Dict] | str:
    """(GET /v{version}/Orders/{id}/items/status) Gets the status for all items within a specific order."""
    if not API_BASE_URL: return f"{ERROR_PREFIX} Configuration Error - Missing API Base URL."
    if not API_AUTH_TOKEN: return f"{ERROR_PREFIX} Configuration Error - Missing API authentication token."

    api_url = f"{API_BASE_URL}/v{API_VERSION}/Orders/{order_id}/items/status"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {API_AUTH_TOKEN}"}

    response = None
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(api_url, headers=headers)

        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    return data
                else:
                    return f"{ERROR_PREFIX} Unexpected response type: {type(data)}. Expected a list."
            except json.JSONDecodeError:
                return f"{ERROR_PREFIX} Failed to decode successful JSON response (Status 200)."
        else:
            error_body = response.text[:500]
            if response.status_code == 404: return f"{ERROR_PREFIX} Order not found (404)."
            elif response.status_code == 401: return f"{ERROR_PREFIX} Unauthorized (401)."
            elif response.status_code >= 500: return f"{ERROR_PREFIX} Server Error ({response.status_code})."
            else: return f"{ERROR_PREFIX} Unexpected HTTP {response.status_code}. Body: {error_body}"

    except httpx.TimeoutException:
        return f"{ERROR_PREFIX} Request timed out."
    except httpx.RequestError as req_err:
        return f"{ERROR_PREFIX} Network or connection error. Details: {req_err}"
    except json.JSONDecodeError:
        status_code = response.status_code if response else 'Unknown'
        return f"{ERROR_PREFIX} Failed to decode error response as JSON. Status: {status_code}"
    except Exception as e:
        return f"{ERROR_PREFIX} An unexpected error occurred. Details: {e}"


async def sy_get_order_tracking(
    order_id: str,
) -> Dict | str:
    """(GET /v{version}/Orders/{id}/trackingcode) Retrieves the tracking code for a specific order."""
    if not API_BASE_URL: return f"{ERROR_PREFIX} Configuration Error - Missing API Base URL."
    if not API_AUTH_TOKEN: return f"{ERROR_PREFIX} Configuration Error - Missing API authentication token."

    api_url = f"{API_BASE_URL}/v{API_VERSION}/Orders/{order_id}/trackingcode"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {API_AUTH_TOKEN}"}

    response = None
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(api_url, headers=headers)

        if response.status_code == 200:
            try:
                # Assuming JSON response, structure wasn't documented
                return response.json()
            except json.JSONDecodeError:
                 # If it's plain text tracking code? Return as content.
                 return {"tracking_info": response.text}
        else:
            error_body = response.text[:500]
            if response.status_code == 404: return f"{ERROR_PREFIX} Order not found (404)."
            elif response.status_code == 401: return f"{ERROR_PREFIX} Unauthorized (401)."
            elif response.status_code >= 500: return f"{ERROR_PREFIX} Server Error ({response.status_code})."
            else: return f"{ERROR_PREFIX} Unexpected HTTP {response.status_code}. Body: {error_body}"

    except httpx.TimeoutException:
        return f"{ERROR_PREFIX} Request timed out."
    except httpx.RequestError as req_err:
        return f"{ERROR_PREFIX} Network or connection error. Details: {req_err}"
    except json.JSONDecodeError:
        status_code = response.status_code if response else 'Unknown'
        return f"{ERROR_PREFIX} Failed to decode error response as JSON. Status: {status_code}"
    except Exception as e:
        return f"{ERROR_PREFIX} An unexpected error occurred. Details: {e}"


# --- Pricing ---

async def sy_list_products(
) -> Dict | str:
    """(GET /api/v{version}/Pricing/list) Returns a list of available products and their configurable options."""
    if not API_BASE_URL: return f"{ERROR_PREFIX} Configuration Error - Missing API Base URL."
    if not API_AUTH_TOKEN: return f"{ERROR_PREFIX} Configuration Error - Missing API authentication token."

    api_url = f"{API_BASE_URL}/api/{API_VERSION}/Pricing/list"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {API_AUTH_TOKEN}"}

    response = None
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(api_url, headers=headers)

        if response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError:
                return f"{ERROR_PREFIX} Failed to decode successful JSON response (Status 200)."
        else:
            error_body = response.text[:500]
            if response.status_code == 401: return f"{ERROR_PREFIX} Unauthorized (401)."
            elif response.status_code >= 500: return f"{ERROR_PREFIX} Server Error ({response.status_code})."
            else: return f"{ERROR_PREFIX} Unexpected HTTP {response.status_code}. Body: {error_body}"

    except httpx.TimeoutException:
        return f"{ERROR_PREFIX} Request timed out."
    except httpx.RequestError as req_err:
        return f"{ERROR_PREFIX} Network or connection error. Details: {req_err}"
    except json.JSONDecodeError:
        status_code = response.status_code if response else 'Unknown'
        return f"{ERROR_PREFIX} Failed to decode error response as JSON. Status: {status_code}"
    except Exception as e:
        return f"{ERROR_PREFIX} An unexpected error occurred. Details: {e}"


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
    if not API_BASE_URL: return f"{ERROR_PREFIX} Configuration Error - Missing API Base URL."
    if not API_AUTH_TOKEN: return f"{ERROR_PREFIX} Configuration Error - Missing API authentication token."

    final_country_code = country_code or DEFAULT_COUNTRY_CODE
    final_currency_code = currency_code or DEFAULT_CURRENCY_CODE

    api_url = f"{API_BASE_URL}/api/{API_VERSION}/Pricing/{product_id}/pricings"
    headers = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": f"Bearer {API_AUTH_TOKEN}"}

    try:
        payload = {
            "width": float(width), "height": float(height),
            "countryCode": str(final_country_code), "currencyCode": str(final_currency_code),
            "accessoryOptions": accessory_options or [],
        }
        if quantity is not None: payload["quantity"] = int(quantity)
    except ValueError as e:
        return f"{ERROR_PREFIX} Invalid parameter type. Error: {e}"

    response = None
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(api_url, headers=headers, json=payload)

        if response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError:
                return f"{ERROR_PREFIX} Failed to decode successful JSON response (Status 200)."
        else:
            error_body = response.text[:500]
            if response.status_code == 404: return f"{ERROR_PREFIX} Resource not found (404). Product ID {product_id} invalid?"
            elif response.status_code == 401: return f"{ERROR_PREFIX} Unauthorized (401)."
            elif response.status_code == 400: return f"{ERROR_PREFIX} Bad Request (400). Invalid parameters?"
            elif response.status_code >= 500: return f"{ERROR_PREFIX} Server Error ({response.status_code})."
            else: return f"{ERROR_PREFIX} Unexpected HTTP {response.status_code}. Body: {error_body}"

    except httpx.TimeoutException:
        return f"{ERROR_PREFIX} Request timed out."
    except httpx.RequestError as req_err:
        return f"{ERROR_PREFIX} Network or connection error. Details: {req_err}"
    except json.JSONDecodeError:
        status_code = response.status_code if response else 'Unknown'
        return f"{ERROR_PREFIX} Failed to decode error response as JSON. Status: {status_code}"
    except Exception as e:
        return f"{ERROR_PREFIX} An unexpected error occurred. Details: {e}"

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
    if not API_BASE_URL: return f"{ERROR_PREFIX} Configuration Error - Missing API Base URL."
    if not API_AUTH_TOKEN: return f"{ERROR_PREFIX} Configuration Error - Missing API authentication token."

    final_country_code = country_code or DEFAULT_COUNTRY_CODE
    final_currency_code = currency_code or DEFAULT_CURRENCY_CODE

    api_url = f"{API_BASE_URL}/api/{API_VERSION}/Pricing/{product_id}/pricing"
    headers = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": f"Bearer {API_AUTH_TOKEN}"}

    try:
        payload = {
            "width": float(width), "height": float(height),
            "countryCode": str(final_country_code), "quantity": int(quantity),
            "currencyCode": str(final_currency_code), "accessoryOptions": accessory_options or [],
        }
    except ValueError as e:
        return f"{ERROR_PREFIX} Invalid parameter type. Error: {e}"

    response = None
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(api_url, headers=headers, json=payload)

        if response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError:
                return f"{ERROR_PREFIX} Failed to decode successful JSON response (Status 200)."
        else:
            # Handle specific HTTP errors
            error_body = response.text[:500]
            if response.status_code == 404: return f"{ERROR_PREFIX} Resource not found (404). Product ID {product_id} invalid?"
            elif response.status_code == 401: return f"{ERROR_PREFIX} Unauthorized (401). Check API token."
            elif response.status_code == 400: return f"{ERROR_PREFIX} Bad Request (400). Check parameters/payload."
            elif response.status_code >= 500: return f"{ERROR_PREFIX} Server Error ({response.status_code})."
            else: return f"{ERROR_PREFIX} Unexpected HTTP {response.status_code}. Body: {error_body}"

    except httpx.TimeoutException:
        # Specific handoff message from original code, adapting slightly
        return f"{ERROR_PREFIX} The request to the pricing API timed out."
    except httpx.RequestError as req_err:
        return f"{ERROR_PREFIX} Network or connection error. Details: {req_err}"
    except json.JSONDecodeError: # Should only happen if error response isn't JSON
        status_code = response.status_code if response else 'Unknown'
        return f"{ERROR_PREFIX} Failed to decode error response as JSON. Status: {status_code}"
    except Exception as e:
        print(f" Unexpected error in sy_get_specific_price: {e}"); traceback.print_exc() # Keep traceback for debugging
        return f"{ERROR_PREFIX} An unexpected error occurred. Details: {e}"


async def sy_list_countries(
) -> Dict | str:
    """(POST /api/v{version}/Pricing/countries) Returns a list of supported countries for pricing/shipping."""
    if not API_BASE_URL: return f"{ERROR_PREFIX} Configuration Error - Missing API Base URL."
    if not API_AUTH_TOKEN: return f"{ERROR_PREFIX} Configuration Error - Missing API authentication token."

    api_url = f"{API_BASE_URL}/api/{API_VERSION}/Pricing/countries"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {API_AUTH_TOKEN}"}

    response = None
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Using POST as per documentation
            response = await client.post(api_url, headers=headers)

        if response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError:
                return f"{ERROR_PREFIX} Failed to decode successful JSON response (Status 200)."
        else:
            error_body = response.text[:500]
            if response.status_code == 401: return f"{ERROR_PREFIX} Unauthorized (401)."
            elif response.status_code >= 500: return f"{ERROR_PREFIX} Server Error ({response.status_code})."
            else: return f"{ERROR_PREFIX} Unexpected HTTP {response.status_code}. Body: {error_body}"

    except httpx.TimeoutException:
        return f"{ERROR_PREFIX} Request timed out."
    except httpx.RequestError as req_err:
        return f"{ERROR_PREFIX} Network or connection error. Details: {req_err}"
    except json.JSONDecodeError:
        status_code = response.status_code if response else 'Unknown'
        return f"{ERROR_PREFIX} Failed to decode error response as JSON. Status: {status_code}"
    except Exception as e:
        return f"{ERROR_PREFIX} An unexpected error occurred. Details: {e}"

# --- Users ---

async def sy_verify_login(
) -> Dict | str:
    """(GET /api/v{version}/users/login) Verifies if the current authentication token is valid."""
    if not API_BASE_URL: return f"{ERROR_PREFIX} Configuration Error - Missing API Base URL."
    if not API_AUTH_TOKEN: return f"{ERROR_PREFIX} Configuration Error - Missing API authentication token for verification."

    api_url = f"{API_BASE_URL}/api/{API_VERSION}/users/login"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {API_AUTH_TOKEN}"}

    response = None
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(api_url, headers=headers)

        if response.status_code == 200:
            try:
                # Expecting {"name": "string", "authenticated": true}
                return response.json()
            except json.JSONDecodeError:
                return f"{ERROR_PREFIX} Failed to decode successful JSON response for login verification (Status 200)."
        else:
            error_body = response.text[:500]
            if response.status_code == 401: return f"{ERROR_PREFIX} Unauthorized (401). Token is invalid or expired."
            elif response.status_code >= 500: return f"{ERROR_PREFIX} Server Error ({response.status_code})."
            else: return f"{ERROR_PREFIX} Unexpected HTTP {response.status_code} during login verification. Body: {error_body}"

    except httpx.TimeoutException:
        return f"{ERROR_PREFIX} Request timed out during login verification."
    except httpx.RequestError as req_err:
        return f"{ERROR_PREFIX} Network or connection error during login verification. Details: {req_err}"
    except json.JSONDecodeError:
        status_code = response.status_code if response else 'Unknown'
        return f"{ERROR_PREFIX} Failed to decode error response as JSON during login verification. Status: {status_code}"
    except Exception as e:
        return f"{ERROR_PREFIX} An unexpected error occurred during login verification. Details: {e}"


async def sy_perform_login(
    username: str,
    password: str,
) -> Dict | str:
    """(POST /api/v{version}/users/login) Performs user login to obtain an authentication token."""
    if not API_BASE_URL: return f"{ERROR_PREFIX} Configuration Error - Missing API Base URL."
    # No auth token needed for login request itself

    api_url = f"{API_BASE_URL}/api/{API_VERSION}/users/login"
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
        return f"{ERROR_PREFIX} An unexpected error occurred during login. Details: {e}"
