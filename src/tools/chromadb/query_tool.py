# src/tools/chromadb/query_tool.py

import json
from typing import List, Dict, Any

from src.services.chromadb.client_manager import get_chroma_collection
from src.services.logger_config import log_message

# --- Tool Function ---
async def query_knowledge_base(query_text: str) -> str:
    """
    Queries the ChromaDB knowledge base with a given text string and returns
    the top 3 most relevant document chunks as a JSON formatted string.
    This tool is used by the StickerYou_Agent to find information to answer user questions.
    """
    
    try:
        # 1. Get the pre-initialized collection
        collection = get_chroma_collection()

        # 2. Prepare and execute the query with the required prefix
        prefixed_query = f"search_query: {query_text}"
        query_results = collection.query(
            query_texts=[prefixed_query],
            n_results=3,
            include=["documents", "metadatas", "distances"],
        )

        # 3. Format the results into a JSON string
        if not query_results or not query_results.get("ids") or not query_results["ids"][0]:
            log_message("No results found in ChromaDB for the query.", level=3)
            return json.dumps([])

        results_list = []
        documents = query_results["documents"][0]
        metadatas = query_results["metadatas"][0]
        distances = query_results["distances"][0]

        for i, doc in enumerate(documents):
            results_list.append({
                "result_number": i + 1,
                "content": doc,
                "source": metadatas[i].get("source", "N/A"),
                "relevance_score": 1 - distances[i]
            })
        
        final_json_string = json.dumps(results_list, indent=2)
        log_message(f"Returning {len(documents)} results as JSON to agent.", level=3)
        return final_json_string

    except Exception as e:
        log_message(f"An error occurred during ChromaDB query: {e}", log_type="error")
        import traceback
        traceback.print_exc()
        return json.dumps([{"error": f"An exception occurred while querying the knowledge base: {e}"}])