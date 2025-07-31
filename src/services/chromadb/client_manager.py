# src/services/chromadb/client_manager.py

import chromadb
from typing import Optional

import config
from src.services.logger_config import log_message
from .custom_embedding_function import ModernBertEmbeddingFunction

# --- Global variables to hold the shared instances ---
chroma_client: Optional[chromadb.PersistentClient] = None
embedding_function: Optional[ModernBertEmbeddingFunction] = None

def initialize_chroma_client():
    """
    Initializes the shared ChromaDB client and embedding function.
    This should be called once at application startup.
    """
    global chroma_client, embedding_function
    
    if chroma_client is not None:
        log_message("ChromaDB client is already initialized.", level=2)
        return

    if not config.CHROMA_DB_PATH_CONFIG or not config.CHROMA_COLLECTION_NAME_CONFIG:
        raise ValueError("CHROMA_DB_PATH_CONFIG and CHROMA_COLLECTION_NAME_CONFIG must be set.")

    log_message(f"Initializing ChromaDB client at path: {config.CHROMA_DB_PATH_CONFIG}", level=2, prefix=">")
    try:
        # Initialize the client once using the correct config variable
        chroma_client = chromadb.PersistentClient(path=config.CHROMA_DB_PATH_CONFIG)
        
        # Initialize the embedding function once (this loads the model)
        embedding_function = ModernBertEmbeddingFunction()

        # Ping the collection to ensure it's accessible on startup
        collection = chroma_client.get_collection(
            name=config.CHROMA_COLLECTION_NAME_CONFIG,
            embedding_function=embedding_function
        )
        log_message(f"✅ ChromaDB client initialized. Collection '{collection.name}' has {collection.count()} items.", level=2)

    except Exception as e:
        log_message(f"CRITICAL: Failed to initialize ChromaDB client: {e}", log_type="error", level=1, prefix="!!!")
        chroma_client = None
        embedding_function = None
        raise

def get_chroma_collection() -> chromadb.Collection:
    """
    Returns the initialized ChromaDB collection instance.
    Raises a ConnectionError if the client is not initialized.
    """
    if chroma_client is None or embedding_function is None:
        raise ConnectionError("ChromaDB client has not been initialized. Call initialize_chroma_client() first.")
    
    # The validation in initialize_chroma_client ensures config.CHROMA_COLLECTION_NAME_CONFIG is set
    return chroma_client.get_collection(
        name=config.CHROMA_COLLECTION_NAME_CONFIG,
        embedding_function=embedding_function
    )

def close_chroma_client():
    """
    Cleans up the ChromaDB client resources.
    """
    global chroma_client, embedding_function
    if chroma_client:
        log_message("Closing ChromaDB client.", level=2, prefix="---")
        chroma_client = None
        embedding_function = None