# /src/services/chromadb/custom_embedding_function.py

import chromadb
from sentence_transformers import SentenceTransformer
from src.services.logger_config import log_message

class ModernBertEmbeddingFunction(chromadb.EmbeddingFunction):
    """
    Custom embedding function that matches the one used during ingestion.
    It uses the 'nomic-ai/modernbert-embed-base' model and adds the
    required 'search_query:' prefix to input texts for querying.
    """
    def __init__(self, model_name: str = "nomic-ai/modernbert-embed-base"):
        log_message(f"Initializing custom ModernBertEmbeddingFunction with model: {model_name}", level=2)
        try:
            self.model = SentenceTransformer(model_name)
            log_message("Custom embedding model loaded successfully.", level=3)
        except Exception as e:
            log_message(f"!!! FAILED to load SentenceTransformer model '{model_name}': {e}", log_type="error")
            raise

    def __call__(self, input_texts: chromadb.Documents) -> chromadb.Embeddings:
        # Add the required prefix for querying.
        prefixed_texts = [f"search_query: {text}" for text in input_texts]
        
        embeddings = self.model.encode(prefixed_texts, normalize_embeddings=True)
        
        return embeddings.tolist()