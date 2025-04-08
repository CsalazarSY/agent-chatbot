# price.api.py
import httpx
import json
import traceback

# Import necessary configuration constants from config.py
from config import (
    API_BASE_URL, API_VERSION, API_AUTH_TOKEN,
    DEFAULT_COUNTRY_CODE, DEFAULT_CURRENCY_CODE
)

# --- Tool Function Definition ---
async def get_price(
    product_id: int,
    width: float,
    height: float,
    quantity: int,
    country_code: str = DEFAULT_COUNTRY_CODE,
    currency_code: str = DEFAULT_CURRENCY_CODE
) -> str:
    """
    Calls the external pricing API asynchronously to get a price quote.

    Args:
        product_id: The unique ID of the product (e.g., 38 or 51).
        width: The width of the product.
        height: The height of the product.
        quantity: The number of items requested.
        country_code: The ISO country code for pricing/shipping.
        currency_code: The ISO currency code for the price.

    Returns:
        A string containing the formatted price information or a handoff message.
        (Handoff message indicates failure or inability to get a specific price).
    """
    print(f"\n--- Running Tool: get_price ---")

    # --- Structure variables for the cal --- #
    api_url = f"{API_BASE_URL}/api/{API_VERSION}/Pricing/{product_id}/pricing"

    # Ensure types are correct before sending payload
    try:
        payload = {
            "width": float(width),
            "height": float(height),
            "countryCode": str(country_code),
            "quantity": int(quantity),
            "currencyCode": str(currency_code),
        }
    except ValueError as e:
        print(f"Error converting parameters for API call: {e}")
        # Return handoff message directly for parameter errors
        return f"HANDOFF: Invalid parameter type (width/height/quantity must be numbers). Error: {e}"

    headers = {
        "Content-Type": "application/json", "Accept": "application/json",
        "Authorization": f"Bearer {API_AUTH_TOKEN}"
    }

    if not API_AUTH_TOKEN:
        print("Error: API_AUTH_TOKEN is empty.")
        return "HANDOFF: Configuration Error - Missing API authentication token."

    print(f" <- Calling Pricing API...")
    print(f"    URL: {api_url}")
    print(f"    Headers: {{... 'Authorization': 'Bearer [REDACTED]' ...}}")
    print(f"    Payload: {json.dumps(payload, indent=2)}")

    try:
        # Use httpx for async request
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(api_url, headers=headers, json=payload)
            # Raise exception for 4xx/5xx responses
            response.raise_for_status()
            response_data = response.json()

        print(f" <- API Response Received (Status: {response.status_code}): {json.dumps(response_data, indent=2)}")

        # Parse response structure
        if response_data and "productPricing" in response_data:
            pricing_info = response_data["productPricing"]
            if pricing_info is None or pricing_info.get("price") is None:
                 print(" API response OK, but missing 'price'.")
                 # Return handoff if price isn't found in a valid response
                 return "HANDOFF: I checked our pricing list, but couldn't find the specific price details for that configuration. Let me connect you with a team member."

            # Extract the response information
            price = pricing_info.get("price")
            currency = pricing_info.get("currency", currency_code)
            unit_measure = pricing_info.get("unitMeasure", "items")
            price_per_unit = pricing_info.get("pricePerSticker")
            response_quantity = pricing_info.get("quantity", quantity)

            # Format success response string
            response_str = f"Okay, the price for {response_quantity} {unit_measure} ({width}x{height}) is {price:.2f} {currency}."
            if price_per_unit is not None:
                response_str += f" That is {price_per_unit:.4f} {currency} per {unit_measure.rstrip('s')}."

            # Add shipping info if available and desired
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

            print(f"--- Tool get_price finished (Success) ---\n")
            # No need for TERMINATE here, agent completion handles it. Return just the result.
            return response_str
        else:
            print(" API success, but 'productPricing' key missing in response.")
            print(f"--- Tool get_price finished (Error - Bad Format) ---\n")
            # Return handoff for unexpected format
            return "HANDOFF: Unexpected response format from pricing system. Transferring..."

    # Handle specific exceptions
    except httpx.HTTPStatusError as http_err:
        status_code = http_err.response.status_code
        # response_text = http_err.response.text

        print(f" HTTP error: {http_err} - Status: {status_code}")
        handoff_message = f"HANDOFF: We encountered a technical issue (Error {status_code}) trying to fetch the price. Please wait while I transfer you to a team member."

        if status_code == 404: handoff_message = f"HANDOFF: It seems I couldn't find that product (ID: {product_id}) or specific configuration in our system. I'll transfer you to someone who can check."
        elif status_code == 401: handoff_message = f"HANDOFF: There's an issue with our pricing system. Please wait while I transfer you to a team member to resolve this."
        elif status_code == 400: handoff_message = f"HANDOFF: There might have been an issue with the details provided (like size or quantity). To be sure, I'll connect you with a human agent."
        print(f"--- Tool get_price finished (Error - HTTP {status_code}) ---\n")
        return handoff_message

    except httpx.TimeoutException as timeout_err:
        print(f" Timeout error: {timeout_err}")
        print(f"--- Tool get_price finished (Error - Timeout) ---\n")
        return "HANDOFF: The request to the pricing API timed out. I'll connect you with a human agent."

    except httpx.RequestError as req_err: # Covers connection errors etc.
        print(f" Request error: {req_err}")
        print(f"--- Tool get_price finished (Error - Request) ---\n")
        return "HANDOFF: Problem communicating with the pricing API. I'll connect you with a human agent."

    except json.JSONDecodeError:
        response_text = "[Could not capture response text]"
        print(f" JSON decode error. API Response text: {response_text}...")
        print(f"--- Tool get_price finished (Error - JSON Decode) ---\n")
        return "HANDOFF: I was not able to find the price details for that configuration. I'll transfer you to someone who can check."

    except Exception as e: # Catch-all for other unexpected errors
        print(f" Unexpected error in get_price: {e}"); traceback.print_exc()
        print(f"--- Tool get_price finished (Error - Unexpected) ---\n")
        return "HANDOFF: Unexpected error processing price quote. I'll transfer you to someone who can check."