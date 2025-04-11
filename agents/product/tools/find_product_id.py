# product/tools/find_product_id.py
from typing import Optional, List, Set
from test_data import product_data

# --- Tool Function Definition ---
def find_product_id(product_name_or_desc: str) -> Optional[int]:
    """
    Finds the product ID by searching relevant fields in the imported product data list.

    Args:
        product_name_or_desc: The user's description of the product.

    Returns:
        The product ID (as an int) if found, otherwise None.
    """
    # Access the globally imported product_data
    data = product_data
    print(f"\n--- Running Tool: find_product_id ---")
    search_term = product_name_or_desc.lower().strip()
    print(f"    Attempting to find product ID for: '{search_term}'")

    if not data:
        print("     Error: Product data list is empty.")
        return None

    # Fields to search within
    search_fields = [
        "customer_friendly_name",
        "google_analytics_name",
        "product",
        "category_material_adhesion_finish",
        "print_shop_name",
        "editor_material_name"
    ]

    # --- Matching logic --- #
    # 1. Try exact match on friendly name or Google Analytics name first
    for item in data:
        friendly_name = item.get("customer_friendly_name")
        ga_name = item.get("google_analytics_name")
        if friendly_name and search_term == friendly_name.lower():
             try:
                 pid = int(item["web_product_id"])
                 print(f"       Found exact match on 'customer_friendly_name': '{search_term}' -> ID {pid}")
                 print(f"--- Tool find_product_id finished (Success) ---\n")
                 return pid
             except (ValueError, KeyError):
                 print(f"       Warning: Found match but 'web_product_id' is invalid for {friendly_name}")
                 continue  # Try next item
        if ga_name and search_term == ga_name.lower():
             try:
                 pid = int(item["web_product_id"])
                 print(f"       Found exact match on 'google_analytics_name': '{search_term}' -> ID {pid}")
                 print(f"--- Tool find_product_id finished (Success) ---\n")
                 return pid
             except (ValueError, KeyError):
                 print(f"       Warning: Found match but invalid ID for {ga_name}")
                 continue # Try next item

    # 2. If no exact match, try partial match across specified fields
    possible_matches: List[tuple[int, int]] = [] # (score, pid)
    search_words: Set[str] = set(s for s in search_term.split() if len(s) > 2) # Ignore short words
    print(f"    Attempting partial match using words: {search_words}")

    for item in data:
        text_to_search = ""
        for field in search_fields:
            field_value = item.get(field)
            if isinstance(field_value, str):
                text_to_search += field_value.lower() + " "

        # Simple scoring: count how many search words are in the combined text
        words_in_product_text: Set[str] = set(text_to_search.split())
        common_words: Set[str] = search_words.intersection(words_in_product_text)
        match_score = len(common_words)

        # Boost score for matches in more important fields
        if item.get("customer_friendly_name") and search_term in item["customer_friendly_name"].lower():
            match_score += 2
        if item.get("google_analytics_name") and search_term in item["google_analytics_name"].lower():
            match_score += 2

        if match_score > 0:
            try:
                 pid = int(item["web_product_id"])
                 possible_matches.append((match_score, pid))
                 print(f"       Potential partial match (score {match_score}) for '{search_term}' in product ID {pid}")
            except (ValueError, KeyError):
                print(f"        Warning: Potential match but invalid ID for item")
                continue

    # If we found potential matches, return the one with the highest score
    if possible_matches:
        possible_matches.sort(key=lambda x: x[0], reverse=True) # Sort by score
        best_score, best_pid = possible_matches[0]
        print(f"Found best partial match (score {best_score}) for '{search_term}' -> ID {best_pid}")
        print(f"--- Tool find_product_id finished (Success - Partial Match) ---\n")
        return best_pid

    # 3. No matches found
    print(f"Could not determine product ID for: '{search_term}' from product data.")
    print(f"--- Tool find_product_id finished (Not Found) ---\n")
    return None