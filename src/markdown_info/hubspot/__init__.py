"""
HubSpot Markdown Information Module

This module contains markdown-formatted information and reference materials
specifically for HubSpot CRM integration and agent system messages.

Contents:
- product_properties.py: HubSpot product properties reference for the custom quote form
"""

from .product_properties import HUBSPOT_PRODUCT_PROPERTIES_MARKDOWN
from .mapping_examples import HUBSPOT_TRANSLATION_EXAMPLES_MARKDOWN

__all__ = [
    "HUBSPOT_PRODUCT_PROPERTIES_MARKDOWN",
    "HUBSPOT_TRANSLATION_EXAMPLES_MARKDOWN",
]
