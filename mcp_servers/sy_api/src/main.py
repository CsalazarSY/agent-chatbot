# mcp_servers/sy_api/src/main.py
import os
import asyncio
import httpx
import json
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Optional, List, Dict

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP, Context

# Import utilities
from utils import sy_api_config

# Load environment variables (redundant if utils loads, but safe)
load_dotenv()

API_ERROR_PREFIX="SY_TOOL_FAILED:"

# --- SY API Config Context --- #
@dataclass
class SYApiContext:
    """Context holding the SY API configuration."""
    config: dict

@asynccontextmanager
async def sy_api_lifespan(server: FastMCP) -> AsyncIterator[SYApiContext]:
    """Manages the SY API config context."""
    cfg = sy_api_config # Use the config loaded by utils.py
    if not cfg.get("base_url") or not cfg.get("auth_token"):
        pass # Let the tool handle the missing config
    try:
        yield SYApiContext(config=cfg)
    finally:
        # print("SY API Lifespan: Shutdown complete.")
        pass

# --- Initialize FastMCP Server --- #
mcp = FastMCP(
    "mcp-sy-api",
    description="MCP server for interacting with the StickerYou (SY) API, including pricing, orders, designs and product listing",
    lifespan=sy_api_lifespan,
    host=os.getenv("HOST", "0.0.0.0"), # For SSE
    port=int(os.getenv("PORT", "8052")) # Default port 8052 for SY API server
)

# --- Tools Organized by Category --- #

# --- Designs ---

@mcp.tool()
async def sy_create_design(
    ctx: Context,
    product_id: int,
    width: float,
    height: float,
    image_base64: str,
) -> Dict | str:
    """(POST /api/{version}/Designs/new) Sends a new design to StickerYou."""
    sy_api_context: SYApiContext = ctx.request_context.lifespan_context
    config = sy_api_context.config
    base_url = config.get("base_url")
    api_version = config.get("api_version", "v1")
    auth_token = config.get("auth_token")

    if not base_url: return "{API_ERROR_PREFIX} Configuration Error - Missing API Base URL."
    if not auth_token: return "{API_ERROR_PREFIX}  Configuration Error - Missing API authentication token."

    api_url = f"{base_url}/api/{api_version}/Designs/new"
    headers = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": f"Bearer {auth_token}"}
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
                return f"{API_ERROR_PREFIX}  Failed to decode successful JSON response (Status 200)."
        else:
            error_body = response.text[:500]
            if response.status_code == 401: return f"{API_ERROR_PREFIX}  Unauthorized (401)."
            elif response.status_code == 400: return f"{API_ERROR_PREFIX}  Bad Request (400). Check design parameters/image format."
            elif response.status_code >= 500: return f"{API_ERROR_PREFIX}  Server Error ({response.status_code})."
            else: return f"{API_ERROR_PREFIX}  Unexpected HTTP {response.status_code}. Body: {error_body}"

    except httpx.TimeoutException:
        return "{API_ERROR_PREFIX}  Request timed out (create design)."
    except httpx.RequestError as req_err:
        return f"{API_ERROR_PREFIX}  Network or connection error. Details: {req_err}"
    except json.JSONDecodeError:
        status_code = response.status_code if response else 'Unknown'
        return f"{API_ERROR_PREFIX}  Failed to decode error response as JSON. Status: {status_code}"
    except Exception as e:
        return f"{API_ERROR_PREFIX}  An unexpected error occurred. Details: {e}"


@mcp.tool()
async def sy_get_design_preview(
    ctx: Context,
    design_id: str,
) -> Dict | str:
    """(GET /api/{version}/Designs/{designId}/preview)
        Returns a design preview using its Design ID.
    """
    sy_api_context: SYApiContext = ctx.request_context.lifespan_context
    config = sy_api_context.config
    base_url = config.get("base_url")
    api_version = config.get("api_version", "v1")
    auth_token = config.get("auth_token")

    if not base_url: return "{API_ERROR_PREFIX}  Configuration Error - Missing API Base URL."
    if not auth_token: return "{API_ERROR_PREFIX}  Configuration Error - Missing API authentication token."

    api_url = f"{base_url}/api/{api_version}/Designs/{design_id}/preview"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {auth_token}"}

    response = None
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(api_url, headers=headers)

        if response.status_code == 200:
            try:
                return response.json() # Return whatever the API gives, even if it looks like an order
            except json.JSONDecodeError:
                return f"{API_ERROR_PREFIX}  Failed to decode successful JSON response (Status 200)."
        else:
            error_body = response.text[:500]
            if response.status_code == 404: return f"{API_ERROR_PREFIX}  Design not found (404)."
            elif response.status_code == 401: return f"{API_ERROR_PREFIX}  Unauthorized (401)."
            elif response.status_code >= 500: return f"{API_ERROR_PREFIX}  Server Error ({response.status_code})."
            else: return f"{API_ERROR_PREFIX}  Unexpected HTTP {response.status_code}. Body: {error_body}"

    except httpx.TimeoutException:
        return "{API_ERROR_PREFIX}  Request timed out."
    except httpx.RequestError as req_err:
        return f"{API_ERROR_PREFIX}  Network or connection error. Details: {req_err}"
    except json.JSONDecodeError:
        status_code = response.status_code if response else 'Unknown'
        return f"{API_ERROR_PREFIX}  Failed to decode error response as JSON. Status: {status_code}"
    except Exception as e:
        return f"{API_ERROR_PREFIX}  An unexpected error occurred. Details: {e}"


# --- Orders ---

@mcp.tool()
async def sy_list_orders_by_status_get(
    ctx: Context,
    status_id: int,
) -> List[Dict] | str:
    """
    (GET /{version}/Orders/status/list/{status})
    List orders by status ID using the GET method.

    Args:
        status_id (int): The status ID to filter orders by. Valid values:
                         1 (Cancelled), 2 (Error), 10 (New), 20 (Accepted),
                         30 (InProgress), 40 (OnHold), 50 (Printed), 100 (Shipped).
        config (Config): Configuration object containing API details.
    
     Returns:
        dict | str: A dictionary containing the list of orders on success, or an error string.
   """
    sy_api_context: SYApiContext = ctx.request_context.lifespan_context
    config = sy_api_context.config
    base_url = config.get("base_url")
    api_version = config.get("api_version", "v1")
    auth_token = config.get("auth_token")

    if not base_url: return "{API_ERROR_PREFIX}  Configuration Error - Missing API Base URL."
    if not auth_token: return "{API_ERROR_PREFIX}  Configuration Error - Missing API authentication token."

    api_url = f"{base_url}/{api_version}/Orders/status/list/{status_id}"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {auth_token}"}

    response = None
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(api_url, headers=headers)

        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list): return data
                else: return f"{API_ERROR_PREFIX}  Unexpected response type: {type(data)}. Expected list."
            except json.JSONDecodeError:
                return f"{API_ERROR_PREFIX}  Failed to decode successful JSON response (Status 200)."
        else:
            error_body = response.text[:500]
            if response.status_code == 401: return f"{API_ERROR_PREFIX}  Unauthorized (401)."
            elif response.status_code == 400: return f"{API_ERROR_PREFIX}  Bad Request (400). Invalid status ID."
            elif response.status_code == 404: return f"{API_ERROR_PREFIX}  Invalid Status ID {status_id} provided? (404)."
            elif response.status_code >= 500: return f"{API_ERROR_PREFIX}  Server Error ({response.status_code})."
            else: return f"{API_ERROR_PREFIX}  Unexpected HTTP {response.status_code}. Body: {error_body}"

    except httpx.TimeoutException:
        return "{API_ERROR_PREFIX}  Request timed out."
    except httpx.RequestError as req_err:
        return f"{API_ERROR_PREFIX}  Network or connection error. Details: {req_err}"
    except json.JSONDecodeError:
        status_code = response.status_code if response else 'Unknown'
        return f"{API_ERROR_PREFIX}  Failed to decode error response as JSON. Status: {status_code}"
    except Exception as e:
        return f"{API_ERROR_PREFIX}  An unexpected error occurred. Details: {e}"


@mcp.tool()
async def sy_list_orders_by_status_post(
    ctx: Context,
    status_id: int,
    take: int = 100,
    skip: int = 0,
) -> List[Dict] | str:
    """(POST /{version}/Orders/status/list) Lists orders matching a specific status using a request body (POST)."""
    sy_api_context: SYApiContext = ctx.request_context.lifespan_context
    config = sy_api_context.config
    base_url = config.get("base_url")
    api_version = config.get("api_version", "v1")
    auth_token = config.get("auth_token")

    if not base_url: return "{API_ERROR_PREFIX}  Configuration Error - Missing API Base URL."
    if not auth_token: return "{API_ERROR_PREFIX}  Configuration Error - Missing API authentication token."

    api_url = f"{base_url}/{api_version}/Orders/status/list"
    headers = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": f"Bearer {auth_token}"}
    payload = {"take": take, "skip": skip, "status": status_id}

    response = None
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(api_url, headers=headers, json=payload)

        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list): return data
                else: return f"{API_ERROR_PREFIX}  Unexpected response type: {type(data)}. Expected list."
            except json.JSONDecodeError:
                return f"{API_ERROR_PREFIX}  Failed to decode successful JSON response (Status 200)."
        else:
            error_body = response.text[:500]
            if response.status_code == 401: return f"{API_ERROR_PREFIX}  Unauthorized (401)."
            elif response.status_code == 400: return f"{API_ERROR_PREFIX}  Bad Request (400). Invalid status ID or pagination params."
            elif response.status_code >= 500: return f"{API_ERROR_PREFIX}  Server Error ({response.status_code})."
            else: return f"{API_ERROR_PREFIX}  Unexpected HTTP {response.status_code}. Body: {error_body}"

    except httpx.TimeoutException:
        return "{API_ERROR_PREFIX}  Request timed out."
    except httpx.RequestError as req_err:
        return f"{API_ERROR_PREFIX}  Network or connection error. Details: {req_err}"
    except json.JSONDecodeError:
        status_code = response.status_code if response else 'Unknown'
        return f"{API_ERROR_PREFIX}  Failed to decode error response as JSON. Status: {status_code}"
    except Exception as e:
        return f"{API_ERROR_PREFIX}  An unexpected error occurred. Details: {e}"


@mcp.tool()
async def sy_create_order(
    ctx: Context,
    order_data: Dict,
) -> Dict | str:
    """(POST /{version}/Orders/new) Sends a new order"""
    sy_api_context: SYApiContext = ctx.request_context.lifespan_context
    config = sy_api_context.config
    base_url = config.get("base_url")
    api_version = config.get("api_version", "v1")
    auth_token = config.get("auth_token")

    if not base_url: return "{API_ERROR_PREFIX}  Configuration Error - Missing API Base URL."
    if not auth_token: return "{API_ERROR_PREFIX}  Configuration Error - Missing API authentication token."

    api_url = f"{base_url}/{api_version}/Orders/new"
    headers = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": f"Bearer {auth_token}"}

    response = None
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(api_url, headers=headers, json=order_data)

        if response.status_code == 200:
            try:
                # Expecting {"success": true, "message": "string"}
                return response.json()
            except json.JSONDecodeError:
                return f"{API_ERROR_PREFIX}  Failed to decode successful JSON response (Status 200)."
        else:
            error_body = response.text[:500]
            if response.status_code == 401: return f"{API_ERROR_PREFIX}  Unauthorized (401)."
            elif response.status_code == 400: return f"{API_ERROR_PREFIX}  Bad Request (400). Check order data format, product IDs, or artwork URLs."
            elif response.status_code >= 500: return f"{API_ERROR_PREFIX}  Server Error ({response.status_code})."
            else: return f"{API_ERROR_PREFIX}  Unexpected HTTP {response.status_code}. Body: {error_body}"

    except httpx.TimeoutException:
        return "{API_ERROR_PREFIX}  Request timed out."
    except httpx.RequestError as req_err:
        return f"{API_ERROR_PREFIX}  Network or connection error. Details: {req_err}"
    except json.JSONDecodeError:
        status_code = response.status_code if response else 'Unknown'
        return f"{API_ERROR_PREFIX}  Failed to decode error response as JSON. Status: {status_code}"
    except Exception as e:
        return f"{API_ERROR_PREFIX}  An unexpected error occurred. Details: {e}"


@mcp.tool()
async def sy_create_order_from_designs(
    ctx: Context,
    order_data: Dict,
) -> Dict | str:
    """(POST /{version}/Orders/designs/new) Sends a new order with designs"""
    sy_api_context: SYApiContext = ctx.request_context.lifespan_context
    config = sy_api_context.config
    base_url = config.get("base_url")
    api_version = config.get("api_version", "v1")
    auth_token = config.get("auth_token")

    if not base_url: return "{API_ERROR_PREFIX}  Configuration Error - Missing API Base URL."
    if not auth_token: return "{API_ERROR_PREFIX}  Configuration Error - Missing API authentication token."

    api_url = f"{base_url}/{api_version}/Orders/designs/new"
    headers = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": f"Bearer {auth_token}"}

    response = None
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(api_url, headers=headers, json=order_data)

        if response.status_code == 200:
            try:
                 # Expecting {"success": true, "message": "string"}
                return response.json()
            except json.JSONDecodeError:
                return f"{API_ERROR_PREFIX}  Failed to decode successful JSON response (Status 200)."
        else:
            error_body = response.text[:500]
            if response.status_code == 401: return f"{API_ERROR_PREFIX}  Unauthorized (401)."
            elif response.status_code == 400: return f"{API_ERROR_PREFIX}  Bad Request (400). Check order data format or design IDs."
            elif response.status_code >= 500: return f"{API_ERROR_PREFIX}  Server Error ({response.status_code})."
            else: return f"{API_ERROR_PREFIX}  Unexpected HTTP {response.status_code}. Body: {error_body}"

    except httpx.TimeoutException:
        return "{API_ERROR_PREFIX}  Request timed out."
    except httpx.RequestError as req_err:
        return f"{API_ERROR_PREFIX}  Network or connection error. Details: {req_err}"
    except json.JSONDecodeError:
        status_code = response.status_code if response else 'Unknown'
        return f"{API_ERROR_PREFIX}  Failed to decode error response as JSON. Status: {status_code}"
    except Exception as e:
        return f"{API_ERROR_PREFIX}  An unexpected error occurred. Details: {e}"


@mcp.tool()
async def sy_get_order_details(
    ctx: Context,
    order_id: str,
) -> Dict | str:
    """(GET /{version}/Orders/{id}) Returns order details by its identifier."""
    sy_api_context: SYApiContext = ctx.request_context.lifespan_context
    config = sy_api_context.config
    base_url = config.get("base_url")
    api_version = config.get("api_version", "v1")
    auth_token = config.get("auth_token")

    if not base_url: return "{API_ERROR_PREFIX}  Configuration Error - Missing API Base URL."
    if not auth_token: return "{API_ERROR_PREFIX}  Configuration Error - Missing API authentication token."

    api_url = f"{base_url}/{api_version}/Orders/{order_id}"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {auth_token}"}

    response = None
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(api_url, headers=headers)

        if response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError:
                return f"{API_ERROR_PREFIX}  Failed to decode successful JSON response (Status 200)."
        else:
            error_body = response.text[:500]
            if response.status_code == 404: return f"{API_ERROR_PREFIX}  Order not found (404)."
            elif response.status_code == 401: return f"{API_ERROR_PREFIX}  Unauthorized (401)."
            elif response.status_code >= 500: return f"{API_ERROR_PREFIX}  Server Error ({response.status_code})."
            else: return f"{API_ERROR_PREFIX}  Unexpected HTTP {response.status_code}. Body: {error_body}"

    except httpx.TimeoutException:
        return "{API_ERROR_PREFIX}  Request timed out."
    except httpx.RequestError as req_err:
        return f"{API_ERROR_PREFIX}  Network or connection error. Details: {req_err}"
    except json.JSONDecodeError:
        status_code = response.status_code if response else 'Unknown'
        return f"{API_ERROR_PREFIX}  Failed to decode error response as JSON. Status: {status_code}"
    except Exception as e:
        return f"{API_ERROR_PREFIX}  An unexpected error occurred. Details: {e}"


@mcp.tool()
async def sy_cancel_order(
    ctx: Context,
    order_id: str,
) -> Dict | str:
    """(PUT /{version}/Orders/{id}/cancel) Cancels an order using its identifier."""
    sy_api_context: SYApiContext = ctx.request_context.lifespan_context
    config = sy_api_context.config
    base_url = config.get("base_url")
    api_version = config.get("api_version", "v1")
    auth_token = config.get("auth_token")

    if not base_url: return "{API_ERROR_PREFIX}  Configuration Error - Missing API Base URL."
    if not auth_token: return "{API_ERROR_PREFIX}  Configuration Error - Missing API authentication token."

    api_url = f"{base_url}/{api_version}/Orders/{order_id}/cancel"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {auth_token}"} # Content-Type might not be needed for PUT with no body

    response = None
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.put(api_url, headers=headers)

        if response.status_code == 200:
            try:
                # Assuming PUT returns the updated order details
                return response.json()
            except json.JSONDecodeError:
                return f"{API_ERROR_PREFIX}  Failed to decode successful JSON response (Status 200)."
        else:
            error_body = response.text[:500]
            if response.status_code == 404: return f"{API_ERROR_PREFIX}  Order not found (404)."
            elif response.status_code == 401: return f"{API_ERROR_PREFIX}  Unauthorized (401)."
            elif response.status_code == 400: return f"{API_ERROR_PREFIX}  Bad Request (400). Order may already be cancelled or unable to be cancelled."
            elif response.status_code >= 500: return f"{API_ERROR_PREFIX}  Server Error ({response.status_code})."
            else: return f"{API_ERROR_PREFIX}  Unexpected HTTP {response.status_code}. Body: {error_body}"

    except httpx.TimeoutException:
        return "{API_ERROR_PREFIX}  Request timed out."
    except httpx.RequestError as req_err:
        return f"{API_ERROR_PREFIX}  Network or connection error. Details: {req_err}"
    except json.JSONDecodeError:
        status_code = response.status_code if response else 'Unknown'
        return f"{API_ERROR_PREFIX}  Failed to decode error response as JSON. Status: {status_code}"
    except Exception as e:
        return f"{API_ERROR_PREFIX}  An unexpected error occurred. Details: {e}"


@mcp.tool()
async def sy_get_order_item_statuses(
    ctx: Context,
    order_id: str,
) -> List[Dict] | str:
    """(GET /{version}/Orders/{id}/items/status) Gets the status for all items within a specific order."""
    sy_api_context: SYApiContext = ctx.request_context.lifespan_context
    config = sy_api_context.config
    base_url = config.get("base_url")
    api_version = config.get("api_version", "v1")
    auth_token = config.get("auth_token")

    if not base_url: return "{API_ERROR_PREFIX}  Configuration Error - Missing API Base URL."
    if not auth_token: return "{API_ERROR_PREFIX}  Configuration Error - Missing API authentication token."

    api_url = f"{base_url}/{api_version}/Orders/{order_id}/items/status"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {auth_token}"}

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
                    return f"{API_ERROR_PREFIX}  Unexpected response type: {type(data)}. Expected a list."
            except json.JSONDecodeError:
                return f"{API_ERROR_PREFIX}  Failed to decode successful JSON response (Status 200)."
        else:
            error_body = response.text[:500]
            if response.status_code == 404: return f"{API_ERROR_PREFIX}  Order not found (404)."
            elif response.status_code == 401: return f"{API_ERROR_PREFIX}  Unauthorized (401)."
            elif response.status_code >= 500: return f"{API_ERROR_PREFIX}  Server Error ({response.status_code})."
            else: return f"{API_ERROR_PREFIX}  Unexpected HTTP {response.status_code}. Body: {error_body}"

    except httpx.TimeoutException:
        return "{API_ERROR_PREFIX}  Request timed out."
    except httpx.RequestError as req_err:
        return f"{API_ERROR_PREFIX}  Network or connection error. Details: {req_err}"
    except json.JSONDecodeError:
        status_code = response.status_code if response else 'Unknown'
        return f"{API_ERROR_PREFIX}  Failed to decode error response as JSON. Status: {status_code}"
    except Exception as e:
        return f"{API_ERROR_PREFIX}  An unexpected error occurred. Details: {e}"


@mcp.tool()
async def sy_get_order_tracking(
    ctx: Context,
    order_id: str,
) -> Dict | str:
    """(GET /{version}/Orders/{id}/trackingcode) Retrieves the tracking code for a specific order."""
    sy_api_context: SYApiContext = ctx.request_context.lifespan_context
    config = sy_api_context.config
    base_url = config.get("base_url")
    api_version = config.get("api_version", "v1")
    auth_token = config.get("auth_token")

    if not base_url: return "{API_ERROR_PREFIX}  Configuration Error - Missing API Base URL."
    if not auth_token: return "{API_ERROR_PREFIX}  Configuration Error - Missing API authentication token."

    api_url = f"{base_url}/{api_version}/Orders/{order_id}/trackingcode"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {auth_token}"}

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
            if response.status_code == 404: return f"{API_ERROR_PREFIX}  Order not found (404)."
            elif response.status_code == 401: return f"{API_ERROR_PREFIX}  Unauthorized (401)."
            elif response.status_code >= 500: return f"{API_ERROR_PREFIX}  Server Error ({response.status_code})."
            else: return f"{API_ERROR_PREFIX}  Unexpected HTTP {response.status_code}. Body: {error_body}"

    except httpx.TimeoutException:
        return "{API_ERROR_PREFIX}  Request timed out."
    except httpx.RequestError as req_err:
        return f"{API_ERROR_PREFIX}  Network or connection error. Details: {req_err}"
    except json.JSONDecodeError:
        status_code = response.status_code if response else 'Unknown'
        return f"{API_ERROR_PREFIX}  Failed to decode error response as JSON. Status: {status_code}"
    except Exception as e:
        return f"{API_ERROR_PREFIX}  An unexpected error occurred. Details: {e}"


# --- Pricing ---

@mcp.tool()
async def sy_list_products(
    ctx: Context,
) -> Dict | str:
    """(GET /api/{version}/Pricing/list) Returns a list of available products and their configurable options."""
    sy_api_context: SYApiContext = ctx.request_context.lifespan_context
    config = sy_api_context.config
    base_url = config.get("base_url")
    api_version = config.get("api_version", "v1")
    auth_token = config.get("auth_token")

    if not base_url: return "{API_ERROR_PREFIX}  Configuration Error - Missing API Base URL."
    if not auth_token: return "{API_ERROR_PREFIX}  Configuration Error - Missing API authentication token."

    api_url = f"{base_url}/api/{api_version}/Pricing/list"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {auth_token}"}

    response = None
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(api_url, headers=headers)

        if response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError:
                return f"{API_ERROR_PREFIX}  Failed to decode successful JSON response (Status 200)."
        else:
            error_body = response.text[:500]
            if response.status_code == 401: return f"{API_ERROR_PREFIX}  Unauthorized (401)."
            elif response.status_code >= 500: return f"{API_ERROR_PREFIX}  Server Error ({response.status_code})."
            else: return f"{API_ERROR_PREFIX}  Unexpected HTTP {response.status_code}. Body: {error_body}"

    except httpx.TimeoutException:
        return "{API_ERROR_PREFIX}  Request timed out."
    except httpx.RequestError as req_err:
        return f"{API_ERROR_PREFIX}  Network or connection error. Details: {req_err}"
    except json.JSONDecodeError:
        status_code = response.status_code if response else 'Unknown'
        return f"{API_ERROR_PREFIX}  Failed to decode error response as JSON. Status: {status_code}"
    except Exception as e:
        return f"{API_ERROR_PREFIX}  An unexpected error occurred. Details: {e}"


@mcp.tool()
async def sy_get_price_tiers(
    ctx: Context,
    product_id: int,
    width: float,
    height: float,
    country_code: Optional[str] = None,
    currency_code: Optional[str] = None,
    accessory_options: Optional[List[Dict]] = None,
    quantity: Optional[int] = None,
) -> Dict | str:
    """(POST /api/{version}/Pricing/{productId}/pricings) Returns a list of prices for different quantity tiers for a specific product."""
    sy_api_context: SYApiContext = ctx.request_context.lifespan_context
    config = sy_api_context.config
    base_url = config.get("base_url")
    api_version = config.get("api_version", "v1")
    auth_token = config.get("auth_token")
    final_country_code = country_code or config.get("default_country_code")
    final_currency_code = currency_code or config.get("default_currency_code")

    if not base_url: return "{API_ERROR_PREFIX}  Configuration Error - Missing API Base URL."
    if not auth_token: return "{API_ERROR_PREFIX}  Configuration Error - Missing API authentication token."

    api_url = f"{base_url}/api/{api_version}/Pricing/{product_id}/pricings"
    headers = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": f"Bearer {auth_token}"}

    try:
        payload = {
            "width": float(width), 
            "height": float(height),
            "countryCode": str(final_country_code), 
            "currencyCode": str(final_currency_code),
            "accessoryOptions": accessory_options or [],
        }
        if quantity is not None: payload["quantity"] = int(quantity)
    except ValueError as e:
        return f"{API_ERROR_PREFIX}  Invalid parameter type. Error: {e}"

    response = None
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(api_url, headers=headers, json=payload)

        if response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError:
                return f"{API_ERROR_PREFIX}  Failed to decode successful JSON response (Status 200)."
        else:
            error_body = response.text[:500]
            if response.status_code == 404: return f"{API_ERROR_PREFIX}  Resource not found (404)."
            elif response.status_code == 401: return f"{API_ERROR_PREFIX}  Unauthorized (401)."
            elif response.status_code == 400: return f"{API_ERROR_PREFIX}  Bad Request (400)."
            elif response.status_code >= 500: return f"{API_ERROR_PREFIX}  Server Error ({response.status_code})."
            else: return f"{API_ERROR_PREFIX}  Unexpected HTTP {response.status_code}. Body: {error_body}"

    except httpx.TimeoutException:
        return "{API_ERROR_PREFIX}  Request timed out."
    except httpx.RequestError as req_err:
        return f"{API_ERROR_PREFIX}  Network or connection error. Details: {req_err}"
    except json.JSONDecodeError:
        status_code = response.status_code if response else 'Unknown'
        return f"{API_ERROR_PREFIX}  Failed to decode error response as JSON. Status: {status_code}"
    except Exception as e:
        return f"{API_ERROR_PREFIX}  An unexpected error occurred. Details: {e}"


@mcp.tool(name="get_specific_price")
async def sy_get_specific_price(
    ctx: Context,
    product_id: int,
    width: float,
    height: float,
    quantity: int,
    country_code: Optional[str] = None,
    currency_code: Optional[str] = None,
    accessory_options: Optional[List[Dict]] = None
) -> Dict | str:
    """(POST /api/{version}/Pricing/{productId}/pricing) Calls the SY pricing API for a *specific* quantity of a product."""
    sy_api_context: SYApiContext = ctx.request_context.lifespan_context
    config = sy_api_context.config
    base_url = config.get("base_url")
    api_version = config.get("api_version", "v1")
    auth_token = config.get("auth_token")
    final_country_code = country_code or config.get("default_country_code")
    final_currency_code = currency_code or config.get("default_currency_code")

    if not base_url: return "{API_ERROR_PREFIX}  Configuration Error - Missing API Base URL."
    if not auth_token: return "{API_ERROR_PREFIX}  Configuration Error - Missing API authentication token."

    api_url = f"{base_url}/api/{api_version}/Pricing/{product_id}/pricing"
    headers = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": f"Bearer {auth_token}"}

    try:
        payload = {
            "width": float(width), 
            "height": float(height),
            "countryCode": str(final_country_code), 
            "quantity": int(quantity),
            "currencyCode": str(final_currency_code), 
            "accessoryOptions": accessory_options or [],
        }
    except ValueError as e:
        return f"{API_ERROR_PREFIX}  Invalid parameter type. Error: {e}"

    response = None
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(api_url, headers=headers, json=payload)

        if response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError:
                return f"{API_ERROR_PREFIX}  Failed to decode successful JSON response (Status 200)."
        else:
            # Handle specific HTTP errors
            error_body = response.text[:500]
            if response.status_code == 404: return f"{API_ERROR_PREFIX}  Resource not found (404)."
            elif response.status_code == 401: return f"{API_ERROR_PREFIX}  Unauthorized (401). Check API token."
            elif response.status_code == 400: return f"{API_ERROR_PREFIX}  Bad Request (400). Check parameters/payload."
            elif response.status_code >= 500: return f"{API_ERROR_PREFIX}  Server Error ({response.status_code})."
            else: return f"{API_ERROR_PREFIX}  Unexpected HTTP {response.status_code}. Body: {error_body}"

    except httpx.TimeoutException:
        return "{API_ERROR_PREFIX}  Request timed out."
    except httpx.RequestError as req_err:
        return f"{API_ERROR_PREFIX}  Network or connection error. Details: {req_err}"
    except json.JSONDecodeError: # Should only happen if error response isn't JSON
        status_code = response.status_code if response else 'Unknown'
        return f"{API_ERROR_PREFIX}  Failed to decode error response as JSON. Status: {status_code}"
    except Exception as e:
        return f"{API_ERROR_PREFIX}  An unexpected error occurred. Details: {e}"


@mcp.tool()
async def sy_list_countries(
    ctx: Context,
) -> Dict | str:
    """(POST /api/{version}/Pricing/countries) Returns a list of supported countries for pricing/shipping."""
    sy_api_context: SYApiContext = ctx.request_context.lifespan_context
    config = sy_api_context.config
    base_url = config.get("base_url")
    api_version = config.get("api_version", "v1")
    auth_token = config.get("auth_token")

    if not base_url: return "{API_ERROR_PREFIX}  Configuration Error - Missing API Base URL."
    if not auth_token: return "{API_ERROR_PREFIX}  Configuration Error - Missing API authentication token."

    api_url = f"{base_url}/api/{api_version}/Pricing/countries"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {auth_token}"}

    response = None
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Using POST as per documentation, though GET seems more conventional
            response = await client.post(api_url, headers=headers)

        if response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError:
                return f"{API_ERROR_PREFIX}  Failed to decode successful JSON response (Status 200)."
        else:
            error_body = response.text[:500]
            if response.status_code == 401: return f"{API_ERROR_PREFIX}  Unauthorized (401)."
            elif response.status_code >= 500: return f"{API_ERROR_PREFIX}  Server Error ({response.status_code})."
            else: return f"{API_ERROR_PREFIX}  Unexpected HTTP {response.status_code}. Body: {error_body}"

    except httpx.TimeoutException:
        return "{API_ERROR_PREFIX}  Request timed out."
    except httpx.RequestError as req_err:
        return f"{API_ERROR_PREFIX}  Network or connection error. Details: {req_err}"
    except json.JSONDecodeError:
        status_code = response.status_code if response else 'Unknown'
        return f"{API_ERROR_PREFIX}  Failed to decode error response as JSON. Status: {status_code}"
    except Exception as e:
        return f"{API_ERROR_PREFIX}  An unexpected error occurred. Details: {e}"

# --- Users ---

@mcp.tool()
async def sy_verify_login(
    ctx: Context,
) -> Dict | str:
    """(GET /users/login) Verifies if the current authentication token is valid."""
    sy_api_context: SYApiContext = ctx.request_context.lifespan_context
    config = sy_api_context.config
    base_url = config.get("base_url")
    api_version = config.get("api_version", "v1")
    auth_token = config.get("auth_token")

    if not base_url: return "{API_ERROR_PREFIX}  Configuration Error - Missing API Base URL."
    if not auth_token: return "{API_ERROR_PREFIX}  Configuration Error - Missing API authentication token for verification."

    api_url = f"{base_url}/users/login"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {auth_token}"}

    response = None
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(api_url, headers=headers)

        if response.status_code == 200:
            try:
                # Expecting {"name": "string", "authenticated": true}
                return response.json()
            except json.JSONDecodeError:
                return f"{API_ERROR_PREFIX}  Failed to decode successful JSON response for login verification (Status 200)."
        else:
            error_body = response.text[:500]
            if response.status_code == 401: return f"{API_ERROR_PREFIX}  Unauthorized (401). Token is invalid or expired."
            elif response.status_code >= 500: return f"{API_ERROR_PREFIX}  Server Error ({response.status_code})."
            else: return f"{API_ERROR_PREFIX}  Unexpected HTTP {response.status_code} during login verification. Body: {error_body}"

    except httpx.TimeoutException:
        return "{API_ERROR_PREFIX}  Request timed out during login verification."
    except httpx.RequestError as req_err:
        return f"{API_ERROR_PREFIX}  Network or connection error during login verification. Details: {req_err}"
    except json.JSONDecodeError:
        status_code = response.status_code if response else 'Unknown'
        return f"{API_ERROR_PREFIX}  Failed to decode error response as JSON during login verification. Status: {status_code}"
    except Exception as e:
        return f"{API_ERROR_PREFIX}  An unexpected error occurred during login verification. Details: {e}"


@mcp.tool()
async def sy_perform_login(
    ctx: Context,
    username: str,
    password: str,
) -> Dict | str:
    """(POST /users/login) Performs user login to obtain an authentication token."""
    sy_api_context: SYApiContext = ctx.request_context.lifespan_context
    config = sy_api_context.config
    base_url = config.get("base_url")
    # No auth token needed for login request itself

    if not base_url: return "{API_ERROR_PREFIX}  Configuration Error - Missing API Base URL."

    api_url = f"{base_url}/users/login"
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
                return f"{API_ERROR_PREFIX} Failed to decode successful JSON response from login (Status 200)."
        else:
            error_body = response.text[:500]
            # Assuming 400/401 for bad credentials, but API might vary
            if response.status_code == 400: return f"{API_ERROR_PREFIX}  Bad Request (400). Invalid credentials or request format?"
            elif response.status_code == 401: return f"{API_ERROR_PREFIX}  Unauthorized (401). Invalid username or password?"
            elif response.status_code >= 500: return f"{API_ERROR_PREFIX}  Server Error ({response.status_code})."
            else: return f"{API_ERROR_PREFIX}  Unexpected HTTP {response.status_code} during login. Body: {error_body}"

    except httpx.TimeoutException:
        return "{API_ERROR_PREFIX}  Request timed out during login."
    except httpx.RequestError as req_err:
        return f"{API_ERROR_PREFIX}  Network or connection error during login. Details: {req_err}"
    except json.JSONDecodeError:
        status_code = response.status_code if response else 'Unknown'
        return f"{API_ERROR_PREFIX}  Failed to decode error response as JSON during login. Status: {status_code}"
    except Exception as e:
        return f"{API_ERROR_PREFIX}  An unexpected error occurred during login. Details: {e}"

# --- Main Execution Block --- #
async def main():
    transport = os.getenv("TRANSPORT", "stdio").lower()
    if transport == 'sse':
        await mcp.run_sse_async()
    elif transport == 'stdio':
        await mcp.run_stdio_async()
    else:
        # Consider raising an error for invalid transport
        print(f"Error: Invalid TRANSPORT specified: {transport}. Use 'stdio' or 'sse'.")
        pass

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())