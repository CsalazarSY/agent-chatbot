"""Defines tools (functions) for interacting with the StickerYou API."""

# src/tools/sticker_api/sy_api.py
import json
import traceback
from typing import Optional, List, Dict, Union
import re
import httpx
import config
from pydantic import ValidationError
from src.services.logger_config import log_message

# Import specific DTOs using absolute paths from src
from src.tools.sticker_api.dtos.responses import (
    LoginResponse,
    LoginStatusResponse,
    CountriesResponse,
    Country,
    SpecificPriceResponse,
    PriceTiersResponse,
    ProductListResponse,
    ProductDetail,
    OrderDetailResponse,
    OrderListResponse,
    SuccessResponse,
    DesignResponse,
    DesignPreviewResponse,
    OrderItemStatus,
    EnhancedProductListResponse,
    SYOrderStatusResponse,
)
from src.markdown_info.quick_replies.quick_reply_markdown import (
    QUICK_REPLIES_START_TAG,
    QUICK_REPLIES_END_TAG,
)
from src.markdown_info.quick_replies.live_product_references import (
    LPA_PRODUCT_QUICK_REPLIES_LABELS,
)

# Standardized Error Prefix
API_ERROR_PREFIX = "SY_TOOL_FAILED:"

# Create a lookup map for efficiency
_product_label_map = {
    item["productId"]: item["quick_reply_label"]
    for item in LPA_PRODUCT_QUICK_REPLIES_LABELS
}
_product_name_map = {
    item["productId"]: item["name"] for item in LPA_PRODUCT_QUICK_REPLIES_LABELS
}


# --- Helper Function for API Requests with Retry ---
async def _make_sy_api_request(
    method: str,
    api_url: str,
    headers_base: Optional[Dict] = None,
    json_payload: Optional[Dict] = None,
    timeout: float = 30.0,
    max_retries: int = 1,  # Only retry once on 401
) -> Dict | List | str:
    """
    Internal helper to make SY API requests, handling dynamic token auth and 401 retry.
    """
    if not config.API_BASE_URL:
        return f"{API_ERROR_PREFIX} Configuration Error - Missing API Base URL."

    current_token = config.get_sy_api_token()
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        **(headers_base or {}),  # Merge base headers if provided
    }
    # Add Authorization header ONLY if token exists
    if current_token:
        headers["Authorization"] = f"Bearer {current_token}"

    async with httpx.AsyncClient(timeout=timeout) as client:
        response: Optional[httpx.Response] = None
        for attempt in range(max_retries + 1):
            try:
                response = await client.request(
                    method,
                    api_url,
                    headers=headers,
                    json=json_payload,
                    follow_redirects=True,
                )

                # Handle successful responses (2xx)
                if 200 <= response.status_code < 300:
                    # Attempt to parse JSON, handle empty 200/204
                    try:
                        # Handle 204 No Content or empty body explicitly
                        if response.status_code == 204 or not response.content:
                            # Return a standard success dict if no body expected
                            # This aligns with SuccessResponse Pydantic model
                            if (
                                response.request.method == "POST"
                            ):  # Typical for creates/updates
                                return {
                                    "success": True,
                                    "message": "Operation successful (No Content)",
                                }
                            # Return raw response for GET/DELETE etc. that might expect no body
                            return response

                        else:
                            json_response = response.json()
                            # Validate expected type (Dict or List)
                            if isinstance(json_response, (dict, list)):
                                return json_response
                            # Return error if unexpected JSON type
                            return f"{API_ERROR_PREFIX} Unexpected JSON type: {type(json_response).__name__}. Expected Dict or List."

                    except json.JSONDecodeError:
                        # This case should be rare if content check above works
                        # but good to have as fallback.
                        return f"{API_ERROR_PREFIX} Success status ({response.status_code}) but failed to decode non-empty response as JSON."

                # Handle 401 Unauthorized - attempt refresh ONLY ONCE
                elif response.status_code == 401 and attempt < max_retries:
                    # Import the refresh function locally ** ONLY WHEN NEEDED **
                    from src.services.sy_refresh_token import refresh_sy_token

                    refresh_successful = await refresh_sy_token()
                    if refresh_successful:
                        headers["Authorization"] = f"Bearer {config.get_sy_api_token()}"
                        log_message("Retrying request with new token.", level=3, log_type="warning")
                        continue  # Retry the request with the new token
                    else:
                        log_message("Token refresh failed. Aborting request.", level=3, log_type="error")
                        # Return a structured error message
                        return {
                            "error": "Authentication failed",
                            "message": "Token refresh failed.",
                        }

                # Handle other client/server errors (4xx, 5xx)
                else:
                    error_detail = f"Status: {response.status_code}"
                    try:
                        # Try to get more detail from response body
                        error_body = response.json()
                        error_detail += f", Body: {json.dumps(error_body)[:200]}"
                    except json.JSONDecodeError:
                        error_detail += f", Body: {response.text[:200]}"
                    # Provide specific error messages
                    if response.status_code == 400:
                        return f"{API_ERROR_PREFIX} Bad Request (400): {error_detail}"
                    elif response.status_code == 404:
                        return f"{API_ERROR_PREFIX} Not Found (404): {error_detail}"
                    elif response.status_code == 403:
                        return f"{API_ERROR_PREFIX} Forbidden (403): {error_detail}"
                    elif 500 <= response.status_code < 600:
                        return f"{API_ERROR_PREFIX} Server Error ({response.status_code}): {error_detail}"
                    else:
                        return f"{API_ERROR_PREFIX} Request failed: {error_detail}"

            # Handle client-side exceptions (timeout, connection errors)
            except httpx.TimeoutException:
                return f"{API_ERROR_PREFIX} Request timed out."
            except httpx.RequestError as req_err:
                # Provide more specific network error info if possible
                return f"{API_ERROR_PREFIX} Network/Connection Error: {req_err}"
            except json.JSONDecodeError:  # Should be less likely to hit here now
                status_code_str = str(response.status_code) if response else "Unknown"
                raw_text = response.text[:200] if response else "[No Response]"
                return f"{API_ERROR_PREFIX} Failed to decode response as JSON. Status: {status_code_str}. Body starts: {raw_text}"
            except Exception as e:
                log_message(traceback.format_exc(), log_type="error")
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
    payload = {
        "productId": product_id,
        "width": width,
        "height": height,
        "imageBase64": image_base64,
    }
    result = await _make_sy_api_request(
        "POST", api_url, json_payload=payload, timeout=60.0
    )

    if isinstance(result, dict):
        return result
    elif isinstance(result, str) and result.startswith(API_ERROR_PREFIX):
        return result
    elif isinstance(result, httpx.Response):  # Handle non-JSON 200 OK
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
    api_url = (
        f"{config.API_BASE_URL}/api/{config.API_VERSION}/Designs/{design_id}/preview"
    )
    result = await _make_sy_api_request("GET", api_url)

    if isinstance(result, dict):
        return result
    elif isinstance(result, str) and result.startswith(API_ERROR_PREFIX):
        return result
    elif isinstance(result, httpx.Response):  # Handle non-JSON 200 OK
        return f"{API_ERROR_PREFIX} Unexpected response format (non-JSON 200 OK) for design preview."
    else:
        return (
            f"{API_ERROR_PREFIX} Unexpected successful response type: "
            f"{type(result)}. Expected Dict."
        )


# --- Helper function for country quick replies ---
def format_countries_as_qr(countries: List[Country]) -> str:
    """Formats a list of Country objects into a JSON string for Quick Replies."""
    qr_options = [
        {"label": country["name"], "value": country["name"]} for country in countries
    ]
    # Note: <country_selection> is a placeholder type. The Planner should use this.
    return f"{{QUICK_REPLIES_START_TAG}}<country_selection>:{json.dumps(qr_options)}{{QUICK_REPLIES_END_TAG}}"


def format_products_as_qr(products: List[ProductDetail]) -> str:
    """
    Formats a list of ProductDetail objects into a JSON string of objects
    for Quick Replies, using the manually defined labels.
    """
    qr_options = []
    for p in products:
        label = _product_label_map.get(p.id)
        if label:
            # The value should be the same as the label for user clarity
            qr_options.append({"label": label, "value": label})

    # Add a fallback option
    qr_options.append(
        {"label": "None of these / Need more help", "value": "None of these"}
    )

    qr_json_array = json.dumps(qr_options)
    return (
        f"{QUICK_REPLIES_START_TAG}<product_clarification>:"
        f"{qr_json_array}{QUICK_REPLIES_END_TAG}"
    )


async def get_live_countries(
    name: Optional[str] = None,
    code: Optional[str] = None,
    returnAsQuickReply: bool = False,
) -> CountriesResponse | str:
    """
    Retrieves a list of supported countries. Can filter by name/code or return the
    full list formatted as a Quick Reply string for fast UI rendering.
    """
    response = await sy_list_countries()
    if isinstance(response, str):
        return f"{API_ERROR_PREFIX} Could not retrieve country list. Upstream error: {response}"

    all_countries = response.countries

    # Fast path for generating UI quick replies
    if returnAsQuickReply:
        return format_countries_as_qr(all_countries)

    # Standard filtering logic
    filtered_countries = all_countries
    if code:
        filtered_countries = [
            c for c in filtered_countries if c.code.lower() == code.lower()
        ]
    if name:
        # Further filter the already filtered list
        filtered_countries = [
            c for c in filtered_countries if c.name.lower() == name.lower()
        ]

    return CountriesResponse(countries=filtered_countries)


async def get_live_products(
    name: Optional[str] = None,
    format: Optional[str] = None,
    material: Optional[str] = None,
) -> EnhancedProductListResponse | str:
    """
    Retrieves a filtered and scored list of products based on search criteria.
    Returns a rich object containing the total number of matches, a list of the top 20
    most relevant products, and a pre-formatted quick reply string if the results
    are ambiguous.
    """
    # Step 1: Get the full product list from the actual API
    all_products_api_data = await sy_list_products()
    if isinstance(all_products_api_data, str):
        return f"{{API_ERROR_PREFIX}} Could not retrieve product list for filtering. Upstream error: {{all_products_api_data}}"

    if not isinstance(all_products_api_data, list):
        return (
            f"{{API_ERROR_PREFIX}} sy_list_products did not return a list as expected."
        )

    # Step 2: Prepare search terms
    search_terms = set()
    if name and name != "*":
        search_terms.update(
            term.lower() for term in re.split(r"[\\s,-]+", name) if term
        )
    if format and format != "*":
        search_terms.update(
            term.lower() for term in re.split(r"[\\s,-]+", format) if term
        )
    if material and material != "*":
        search_terms.update(
            term.lower() for term in re.split(r"[\\s,-]+", material) if term
        )

    # Step 3: Score and sort products if search terms are provided
    product_candidates = []
    total_matches = 0
    if search_terms:
        product_scores = []
        for product_dict in all_products_api_data:
            if not isinstance(product_dict, dict):
                continue  # Skip non-dict items
            score = 0
            product_text = f"{product_dict.get('name', '').lower()} {product_dict.get('material', '').lower()} {product_dict.get('format', '').lower()}"
            for term in search_terms:
                if term in product_text:
                    score += 1
            if score > 0:
                product_scores.append({"score": score, "product": product_dict})

        total_matches = len(product_scores)
        if not product_scores:
            return EnhancedProductListResponse(
                total_matches=0, products=[], quick_reply_string=None
            )

        sorted_products_with_score = sorted(
            product_scores, key=lambda x: x["score"], reverse=True
        )
        product_candidates = [
            item["product"] for item in sorted_products_with_score[:20]
        ]
    else:
        product_candidates = all_products_api_data
        total_matches = len(product_candidates)

    # Step 4: Enrich the candidates and convert to Pydantic models for easier handling
    enriched_product_models = []
    for product_dict in product_candidates:
        if not isinstance(product_dict, dict):
            continue

        product_id = product_dict.get("id")
        label = _product_label_map.get(
            product_id, product_dict.get("name", "Unknown Product")
        )
        product_name_from_map = _product_name_map.get(
            product_id, product_dict.get("name")
        )

        enriched_product = product_dict.copy()
        enriched_product["name"] = product_name_from_map
        enriched_product["quick_reply_label"] = label
        enriched_product_models.append(ProductDetail(**enriched_product))

    # Step 5: Determine definitive match and generate quick replies if needed
    definitive_product = None
    if name and name != "*":
        search_name_lower = name.lower()
        for p in enriched_product_models:
            if p.name.lower() == search_name_lower or (
                p.quick_reply_label and p.quick_reply_label.lower() == search_name_lower
            ):
                definitive_product = p
                break

    quick_reply_string = None
    products_to_return = []

    if definitive_product:
        products_to_return = [definitive_product]
    else:
        products_to_return = enriched_product_models
        # Generate QR string only if there's ambiguity (multiple products, no definitive match)
        if len(products_to_return) > 1:
            quick_reply_string = format_products_as_qr(products_to_return)

    # Step 6: Return the rich response object
    return EnhancedProductListResponse(
        total_matches=total_matches,
        products=products_to_return,
        quick_reply_string=quick_reply_string,
    )


# --- Orders ---
async def sy_get_internal_order_status(order_id: str) -> Union[SYOrderStatusResponse, Dict]:
    """
    (GET /api/{version}/SyOrders/orderstatus/{orderID})
    Description: Retrieves the internal status of an order from the StickerYou API.
    This is a component of the unified order status tool.

    Parameters:
        order_id (str): The order ID to check.

    Returns:
        Union[SYOrderStatusResponse, Dict]: A Pydantic model on success, or a dictionary with a 'status' of 'failed' on error.
    """
    
    # Check configuration
    if not all([config.API_BASE_URL, config.SY_API_ORDER_TOKEN]):
        return {
            "status": "failed",
            "message": f"{API_ERROR_PREFIX} Configuration Error - Missing API_BASE_URL or SY_API_ORDER_TOKEN."
        }

    api_url = f"{config.API_BASE_URL}/api/{config.API_VERSION}/SyOrders/orderstatus/{order_id}"
    
    headers = {
        "Sy-Token": config.SY_API_ORDER_TOKEN,
        "Accept": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(api_url, headers=headers)

            if response.status_code == 200:
                try:
                    response_json = response.json()
                    
                    # On success, return the validated Pydantic model
                    status_response = SYOrderStatusResponse.model_validate(response_json)
                    return status_response
                except ValidationError as e:
                    return {
                        "status": "failed",
                        "message": f"{API_ERROR_PREFIX} Invalid response format from internal order API."
                    }
                except Exception as json_error:
                    return {
                        "status": "failed",
                        "message": f"{API_ERROR_PREFIX} Failed to parse JSON response from internal order API."
                    }
            else:
                error_detail = f"Status: {response.status_code}"
                try:
                    error_body = response.json()
                    error_detail += f", Body: {json.dumps(error_body)[:200]}"
                except json.JSONDecodeError:
                    error_detail += f", Body: {response.text[:200]}"

                if response.status_code == 404:
                    message = f"{API_ERROR_PREFIX} Order not found via internal API (404)."
                else:
                    message = f"{API_ERROR_PREFIX} Internal order API request failed: {error_detail}"
                
                return {"status": "failed", "message": message}

    except httpx.TimeoutException:
        return {"status": "failed", "message": f"{API_ERROR_PREFIX} Internal order API request timed out."}
    except httpx.RequestError as req_err:
        return {"status": "failed", "message": f"{API_ERROR_PREFIX} Network error on internal order API call: {req_err}"}
    except Exception as e:
        log_message(f"Unexpected error in sy_get_internal_order_status: {e}", log_type="error")
        return {"status": "failed", "message": f"{API_ERROR_PREFIX} Unexpected error checking internal order status: {e}"}

# --- Pricing ---
async def sy_list_products() -> ProductListResponse | str:
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
        return result  # Direct list matches Pydantic model
    elif isinstance(result, dict) and "root" in result:
        # Handle case if it incorrectly comes back as a dict { "root": [...] }
        if isinstance(result["root"], list):
            return result["root"]
        else:
            return f"{API_ERROR_PREFIX} Unexpected structure in product list response dict."

    elif isinstance(result, str) and result.startswith(API_ERROR_PREFIX):
        return result
    elif isinstance(result, httpx.Response):  # Handle non-JSON 200 OK
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
    sizeUnit: str = "inches",
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
        width (float): The desired width.
        height (float): The desired height.
        sizeUnit (str): The unit for width and height ('inches' or 'cm'). Defaults to 'inches'.
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
    api_url = (
        f"{config.API_BASE_URL}/api/{config.API_VERSION}/Pricing/{product_id}/pricings"
    )

    # Convert dimensions to inches if necessary
    width_inches = float(width)
    height_inches = float(height)
    if sizeUnit.lower() in ["cm", "centimeter", "centimeters"]:
        width_inches /= 2.54
        height_inches /= 2.54

    payload = {
        "width": width_inches,
        "height": height_inches,
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
    elif isinstance(result, httpx.Response):  # Handle non-JSON 200 OK
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
    quantity: int,
    sizeUnit: str = "inches",
    country_code: Optional[str] = None,
    currency_code: Optional[str] = None,
    accessory_options: Optional[List[Dict]] = None,
) -> SpecificPriceResponse | str:
    """
    (POST /api/{version}/Pricing/{productId}/pricing)
    Description: Calculates and returns the exact price for a specific quantity of a product,
                 based on its dimensions and selected options. Also returns shipping methods.
    Allowed Scopes: [User, Dev, Internal]

    Parameters:
        product_id (int): The unique identifier of the product.
        width (float): The desired width.
        height (float): The desired height.
        quantity (int): The specific quantity required for pricing. Required.
        sizeUnit (str): The unit for width and height ('inches' or 'cm'). Defaults to 'inches'.
        country_code (Optional[str]): Two-letter ISO country code for shipping/pricing context (defaults to config).
        currency_code (Optional[str]): ISO currency code (e.g., 'USD', 'CAD') (defaults to config).
        accessory_options (Optional[List[Dict]]): List of selected accessories, each a dict like {"accessoryId": int, "quantity": int}.

    Request body example (type: SpecificPriceRequest):
        {
            "width": 2.0, # Assumed to be in inches by the API
            "height": 2.0, # Assumed to be in inches by the API
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
    api_url = (
        f"{config.API_BASE_URL}/api/{config.API_VERSION}/Pricing/{product_id}/pricing"
    )

    # Convert dimensions to inches if necessary
    width_inches = float(width)
    height_inches = float(height)
    if sizeUnit.lower() in ["cm", "centimeter", "centimeters"]:
        width_inches /= 2.54
        height_inches /= 2.54

    payload = {
        "width": width_inches,
        "height": height_inches,
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
    elif isinstance(result, httpx.Response):  # Handle non-JSON 200 OK
        return f"{API_ERROR_PREFIX} Unexpected response format (non-JSON 200 OK) for get specific price."
    else:
        return (
            f"{API_ERROR_PREFIX} Unexpected successful response type: "
            f"{type(result)}. Expected Dict."
        )


async def sy_list_countries() -> CountriesResponse | str:
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
    elif isinstance(result, httpx.Response):  # Handle non-JSON 200 OK
        return f"{API_ERROR_PREFIX} Unexpected response format (non-JSON 200 OK) for list countries."
    else:
        return (
            f"{API_ERROR_PREFIX} Unexpected successful response type: "
            f"{type(result)}. Expected Dict or List."
        )


# --- Users ---


async def sy_verify_login() -> LoginStatusResponse | str:
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
            "details": result,
        }
    elif isinstance(result, str) and result.startswith(API_ERROR_PREFIX):
        # Specific handling for 401 on verify
        if "Unauthorized (401)" in result:
            return {
                "status": "failed",
                "message": "Token is invalid (Unauthorized 401).",
            }
        # Return other detailed errors from helper as a string
        return result
    elif isinstance(result, httpx.Response):  # Handle non-JSON 200 OK
        # Treat non-JSON 200 OK as potentially valid but lacking expected data
        if result.status_code == 200:
            return {
                "status": "success",
                "message": "Token appears valid (received 200 OK, but no JSON data).",
                "details": None,  # Or result.text if needed
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
                return f"{API_ERROR_PREFIX} Unexpected HTTP {status_code} during login.{error_detail}"

    except httpx.TimeoutException:
        return f"{API_ERROR_PREFIX} Request timed out during login."
    except httpx.RequestError as req_err:
        return f"{API_ERROR_PREFIX} Network or connection error during login. Details: {req_err}"
    except (
        Exception
    ) as e:  # Catch other potential errors like JSONDecodeError if response parsing fails outside status check
        log_message(traceback.format_exc(), log_type="error")
        return f"{API_ERROR_PREFIX} An unexpected error occurred during login. Details: {e}"
