# RAG Retriever
# Main query interface for retrieving relevant context

import logging
from . import embedder, vector_store

logger = logging.getLogger(__name__)


class Retriever:
    """
    Retriever for querying course materials and Piazza history.
    """

    def __init__(self, chroma_path: str, embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize the retriever.

        Args:
            chroma_path: Path to ChromaDB database
            embedding_model: Name of embedding model (currently unused, for future flexibility)
        """
        self.client = vector_store.init_store(chroma_path)
        self.materials_collection = vector_store.get_or_create_collection(
            self.client, "course_materials"
        )
        self.piazza_collection = vector_store.get_or_create_collection(
            self.client, "piazza_history"
        )
        logger.info("Retriever initialized")

    def query(self, question: str, top_k: int = 5) -> str:
        """
        Query both collections and return formatted context block.

        Args:
            question: The query question
            top_k: Number of top results to return from each collection

        Returns:
            Formatted context string (may be empty if no results)
        """
        # Embed the question
        query_embedding = embedder.embed_one(question)

        # Query both collections
        materials_results = vector_store.query_collection(
            self.materials_collection, query_embedding, top_k=top_k
        )
        piazza_results = vector_store.query_collection(
            self.piazza_collection, query_embedding, top_k=top_k
        )

        # Build formatted context block
        context_lines = []

        # Add materials
        if materials_results:
            for result in materials_results:
                source = result["metadata"].get("source", "Unknown")
                text = result["text"]
                context_lines.append(f"[From course materials - {source}]")
                context_lines.append(text)
                context_lines.append("")

        # Add Piazza Q&As
        if piazza_results:
            for result in piazza_results:
                post_nr = result["metadata"].get("post_nr", "?")
                text = result["text"]
                context_lines.append(f"[From past Q&A - @{post_nr}]")
                context_lines.append(text)
                context_lines.append("")

        context_block = "\n".join(context_lines).strip()

        if context_block:
            logger.info(f"Retrieved {len(materials_results)} material chunks and {len(piazza_results)} Q&A pairs")
        else:
            logger.info("No relevant context found in RAG collections")

        return context_block
