"""ChromaDB services package for agent chatbot application."""

from .custom_embedding_function import ModernBertEmbeddingFunction
from .client_manager import (
    initialize_chroma_client,
    get_chroma_collection,
    close_chroma_client,
)

__all__ = [
    "ModernBertEmbeddingFunction",
    "initialize_chroma_client",
    "get_chroma_collection", 
    "close_chroma_client",
]
