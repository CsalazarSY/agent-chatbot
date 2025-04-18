# mcp_servers/sy_api/src/main.py
import os
import asyncio
import traceback
import httpx
import json
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Optional, Any

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP, Context

# Import utilities
from utils import sy_api_config

# Load environment variables (redundant if utils loads, but safe)
load_dotenv()

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
        # print("SY API Lifespan Warning: Base URL or Auth Token missing. Tools will likely fail.") 
        pass # Let the tool handle the missing config
    try:
        yield SYApiContext(config=cfg)
    finally:
        # print("SY API Lifespan: Shutdown complete.") 
        pass

# --- Initialize FastMCP Server --- #
mcp = FastMCP(
    "mcp-sy-api",
    description="MCP server for interacting with the SY Pricing API.",
    lifespan=sy_api_lifespan,
    host=os.getenv("HOST", "0.0.0.0"), # For SSE
    port=int(os.getenv("PORT", "8052")) # Default port 8052 for SY API server
)

# --- Tool Definition --- #
@mcp.tool(name="get_price")
async def sy_get_price(
    ctx: Context,
    product_id: int,
    width: float,
    height: float,
    quantity: int,
    country_code: Optional[str] = None,
    currency_code: Optional[str] = None
) -> str:
    """Calls the external SY pricing API to get a price quote.

    Args:
        ctx: The MCP server context containing the SY API config.
        product_id: The unique ID of the product (e.g., 38 or 51).
        width: The width of the product.
        height: The height of the product.
        quantity: The number of items requested.
        country_code: Optional. The ISO country code for pricing/shipping. Uses default if None.
        currency_code: Optional. The ISO currency code for the price. Uses default if None.

    Returns:
        A string containing the formatted price information or a handoff message.
        (Handoff message indicates failure or inability to get a specific price).
    """
    # print(f"\n--- MCP Tool: get_price --- Called") 
    sy_api_context: SYApiContext = ctx.request_context.lifespan_context
    config = sy_api_context.config

    # Get config values, using defaults from config if args are None
    base_url = config.get("base_url")
    api_version = config.get("api_version", "v1")
    auth_token = config.get("auth_token")
    final_country_code = country_code or config.get("default_country_code")
    final_currency_code = currency_code or config.get("default_currency_code")

    # --- Config Validation --- #
    if not base_url:
        return "HANDOFF: Configuration Error - Missing API Base URL."
    if not auth_token:
        return "HANDOFF: Configuration Error - Missing API authentication token."

    # --- Structure variables for the call (adapted from original tool) --- #
    api_url = f"{base_url}/api/{api_version}/Pricing/{product_id}/pricing"

    # Ensure types are correct before sending payload
    try:
        payload = {
            "width": float(width),
            "height": float(height),
            "countryCode": str(final_country_code),
            "quantity": int(quantity),
            "currencyCode": str(final_currency_code),
        }
    except ValueError as e:
        # print(f"    Error converting parameters for API call: {e}") 
        return f"HANDOFF: Invalid parameter type (width/height/quantity must be numbers). Error: {e}"

    headers = {
        "Content-Type": "application/json", "Accept": "application/json",
        "Authorization": f"Bearer {auth_token}"
    }

    # print(f"    <- Calling Pricing API ->") 
    # print(f"        URL: {api_url}") 
    # print(f"        Payload: {json.dumps(payload, indent=2)}") 

    try:
        # Use httpx for async request
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(api_url, headers=headers, json=payload)
            response.raise_for_status() # Raise exception for 4xx/5xx responses
            response_data = response.json()

        # print(f"\n    <- API Response Received (Status: {response.status_code}) ->\n    {json.dumps(response_data, indent=2)}") 

        # Parse response structure
        if response_data and "productPricing" in response_data:
            pricing_info = response_data["productPricing"]
            if pricing_info is None or pricing_info.get("price") is None:
                # print("    API response OK, but missing 'price'.") 
                return "HANDOFF: I checked our pricing list, but couldn't find the specific price details for that configuration. Let me connect you with a team member."

            # Extract the response information
            price = pricing_info.get("price")
            currency = pricing_info.get("currency", final_currency_code)
            unit_measure = pricing_info.get("unitMeasure", "items")
            price_per_unit = pricing_info.get("pricePerSticker")
            response_quantity = pricing_info.get("quantity", quantity)

            # Format success response string
            response_str = f"Okay, the price for {response_quantity} {unit_measure} ({width}x{height}) is {price:.2f} {currency}."
            if price_per_unit is not None:
                response_str += f" That is {price_per_unit:.4f} {currency} per {unit_measure.rstrip('s')}."

            # Add shipping info if available
            if pricing_info.get("shippingMethods") and isinstance(pricing_info["shippingMethods"], list):
                 response_str += "\n\n Available shipping options:"
                 for method in pricing_info["shippingMethods"]:
                      method_name = method.get('name', '?')
                      method_price = method.get('price')
                      method_delivery = method.get('deliveryEstimate')
                      price_str = f"{method_price:.2f} {currency}" if method_price is not None else "N/A"
                      delivery_str = f"{method_delivery} days" if method_delivery is not None else "N/A"
                      response_str += f"\n - {method_name}: {price_str} (Est. delivery: {delivery_str})"
            else:
                response_str += "\n (Shipping options info not available.)"

            # print(f"--- Tool get_price finished (Success) ---\n") 
            return response_str
        else:
            # print("    API success, but 'productPricing' key missing in response.") 
            # print(f"--- Tool get_price finished (Error - Bad Format) ---\n") 
            return "HANDOFF: Unexpected response format from pricing system. Transferring..."

    # Handle specific exceptions (copied from original tool)
    except httpx.HTTPStatusError as http_err:
        status_code = http_err.response.status_code
        # print(f"    HTTP error: {http_err} - Status: {status_code}") 
        handoff_message = f"HANDOFF: We encountered a technical issue (Error {status_code}) trying to fetch the price. Please wait while I transfer you to a team member."
        if status_code == 404: handoff_message = f"HANDOFF: It seems I couldn't find that product (ID: {product_id}) or specific configuration in our system. I'll transfer you to someone who can check."
        elif status_code == 401: handoff_message = f"HANDOFF: There's an issue with our pricing system authorization. Please wait while I transfer you to a team member."
        elif status_code == 400: handoff_message = f"HANDOFF: There might have been an issue with the details provided (like size or quantity). To be sure, I'll connect you with a human agent."
        # print(f"--- Tool get_price finished (Error - HTTP {status_code}) ---\n") 
        return handoff_message

    except httpx.TimeoutException as timeout_err:
        # print(f"    Timeout error: {timeout_err}") 
        # print(f"--- Tool get_price finished (Error - Timeout) ---\n") 
        return "HANDOFF: The request to the pricing API timed out. I'll connect you with a human agent."

    except httpx.RequestError as req_err:
        # print(f"    Request error: {req_err}") 
        # print(f"--- Tool get_price finished (Error - Request) ---\n") 
        return "HANDOFF: Problem communicating with the pricing API. I'll connect you with a human agent."

    except json.JSONDecodeError:
        # print(f"    JSON decode error.") 
        # print(f"--- Tool get_price finished (Error - JSON Decode) ---\n") 
        return "HANDOFF: I was not able to find the price details for that configuration. I'll transfer you to someone who can check."

    except Exception as e:
        # print(f"    Unexpected error in get_price: {e}"); # traceback.print_exc() # Avoid printing traceback to stdio
        # print(f"--- Tool get_price finished (Error - Unexpected) ---\n") 
        return "HANDOFF: Unexpected error processing price quote. I'll transfer you to someone who can check."

# --- Main Execution Block --- #
async def main():
    transport = os.getenv("TRANSPORT", "stdio").lower()
    # print(f"Starting SY API MCP Server with {transport} transport...") 
    if transport == 'sse':
        await mcp.run_sse_async()
    elif transport == 'stdio':
        await mcp.run_stdio_async()
    else:
        # print(f"Error: Invalid TRANSPORT specified: {transport}. Use 'stdio' or 'sse'.") 
        pass # Or raise an error

if __name__ == "__main__":
    # Ensure event loop policy is set for Windows if needed
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main()) 