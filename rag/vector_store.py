# RAG Vector Store
# ChromaDB operations for persistent vector storage

import logging
import chromadb

logger = logging.getLogger(__name__)


def init_store(path: str) -> chromadb.PersistentClient:
    """
    Initialize a persistent ChromaDB client.

    Args:
        path: Local filesystem path for the database

    Returns:
        ChromaDB PersistentClient instance
    """
    logger.info(f"Initializing ChromaDB at {path}")
    client = chromadb.PersistentClient(path=path)
    return client


def get_or_create_collection(client: chromadb.Client, name: str):
    """
    Get or create a collection by name.

    Args:
        client: ChromaDB Client
        name: Collection name

    Returns:
        ChromaDB Collection
    """
    logger.info(f"Getting or creating collection: {name}")
    collection = client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"}
    )
    return collection


def upsert_chunks(collection, chunks: list[dict]) -> int:
    """
    Upsert (insert or update) document chunks into a collection.

    Args:
        collection: ChromaDB Collection
        chunks: List of dicts with keys: id, text, metadata

    Returns:
        Number of chunks upserted
    """
    if not chunks:
        return 0

    ids = [chunk["id"] for chunk in chunks]
    documents = [chunk["text"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )
    logger.info(f"Upserted {len(chunks)} chunks to {collection.name}")
    return len(chunks)


def query_collection(collection, query_embedding: list[float], top_k: int = 5) -> list[dict]:
    """
    Query a collection by embedding vector.

    Args:
        collection: ChromaDB Collection
        query_embedding: Embedding vector (list of floats)
        top_k: Number of results to return

    Returns:
        List of result dicts with keys: id, text, metadata, distance
    """
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    # Flatten results into a list of dicts
    output = []
    if results["ids"] and len(results["ids"]) > 0:
        for i, doc_id in enumerate(results["ids"][0]):
            output.append({
                "id": doc_id,
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
            })

    return output
