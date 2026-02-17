# RAG Embedder
# Thin wrapper around sentence-transformers for text embeddings

import logging
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# Load model once at import time
_model = None


def _get_model():
    """Lazy-load the embedding model."""
    global _model
    if _model is None:
        logger.info("Loading embedding model: all-MiniLM-L6-v2")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def embed(texts: list[str]) -> list[list[float]]:
    """
    Embed a list of texts.

    Args:
        texts: List of text strings to embed

    Returns:
        List of embedding vectors (each is a list of floats)
    """
    model = _get_model()
    embeddings = model.encode(texts, convert_to_tensor=False)
    return [emb.tolist() if hasattr(emb, 'tolist') else list(emb) for emb in embeddings]


def embed_one(text: str) -> list[float]:
    """
    Embed a single text.

    Args:
        text: Text string to embed

    Returns:
        Embedding vector (list of floats)
    """
    model = _get_model()
    embedding = model.encode(text, convert_to_tensor=False)
    result = embedding.tolist() if hasattr(embedding, 'tolist') else list(embedding)
    return result
