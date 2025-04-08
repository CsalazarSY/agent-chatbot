# test_data.py
from typing import TypedDict, List, Optional, Literal

class ProductData(TypedDict):
    business_unit: str
    product: str
    category_material_adhesion_finish: str
    customer_friendly_name: Optional[str]
    orderable_through_product_first: Literal["Yes", "No"]
    format: str
    web_product_id: str
    google_analytics_name: str
    orderable_through_editor: Optional[Literal["Yes", "No"]]
    print_shop_name: str
    editor_material_name: str


product_data: List[ProductData] = [
    {
        "business_unit": "Rolls",
        "product": "Sticker",
        "category_material_adhesion_finish": "Rolls - White BOPP - Permanent - Glossy (Laminated)",
        "customer_friendly_name": None,
        "orderable_through_product_first": "Yes",
        "format": "Rolls",
        "web_product_id": "30",
        "google_analytics_name": "Durable Roll Label",
        "orderable_through_editor": "Yes",
        "print_shop_name": "Durable BOPP (glossy, permanent)",
        "editor_material_name": "Durable BOPP (glossy, permanent)"
    },
    {
        "business_unit": "Sheet Stickers and Labels",
        "product": "Sticker",
        "category_material_adhesion_finish": "Kiss-Cut - White Vinyl - Removable - Glossy",
        "customer_friendly_name": "White Vinyl Removable Glossy Kiss-Cut Sticker",
        "orderable_through_product_first": "Yes",
        "format": "Kiss Cut",
        "web_product_id": "11",
        "google_analytics_name": "Removable Vinyl Sticker Hand-Outs",
        "orderable_through_editor": "Yes",
        "print_shop_name": "Removable White Vinyl (Glossy)",
        "editor_material_name": "Removable White Vinyl (Glossy)"
    },
    {
        "business_unit": "Sheet Stickers and Labels",
        "product": "Sticker",
        "category_material_adhesion_finish": "Die-Cut - Clear Vinyl - Removable - Glossy",
        "customer_friendly_name": "Laminated Clear Vinyl Removable Sticker",
        "orderable_through_product_first": "Yes",
        "format": "Die Cut",
        "web_product_id": "55",
        "google_analytics_name": "Clear Die-Cut Stickers",
        "orderable_through_editor": None,
        "print_shop_name": "Clear Die-Cut Stickers",
        "editor_material_name": "Clear Die-Cut Stickers"
    }
]
