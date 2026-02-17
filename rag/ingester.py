# RAG Ingester
# Document loading, chunking, and ingestion into ChromaDB

import logging
import re
from pathlib import Path
from pypdf import PdfReader

logger = logging.getLogger(__name__)


def load_text_file(path: str) -> str:
    """
    Load a plain text file.

    Args:
        path: File path

    Returns:
        File contents as string
    """
    logger.info(f"Loading text file: {path}")
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()


def load_pdf(path: str) -> str:
    """
    Load a PDF file and extract text.

    Args:
        path: PDF file path

    Returns:
        Extracted text as string
    """
    logger.info(f"Loading PDF: {path}")
    text = []
    try:
        reader = PdfReader(path)
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text.append(f"[Page {page_num + 1}]\n{page_text}")
    except Exception as e:
        logger.error(f"Error extracting PDF {path}: {e}")
    return "\n\n".join(text)


def load_markdown(path: str) -> str:
    """
    Load a markdown file.

    Args:
        path: File path

    Returns:
        File contents as string
    """
    logger.info(f"Loading markdown: {path}")
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 64) -> list[str]:
    """
    Chunk text into overlapping segments.

    Args:
        text: Input text
        chunk_size: Approximate chunk size in words
        overlap: Number of overlapping words between chunks

    Returns:
        List of text chunks
    """
    words = text.split()
    chunks = []

    if len(words) <= chunk_size:
        return [text]

    i = 0
    while i < len(words):
        chunk_words = words[i:i + chunk_size]
        chunks.append(" ".join(chunk_words))
        i += chunk_size - overlap

    return chunks


def ingest_file(path: str, collection, source_label: str, chunk_size: int = 512, overlap: int = 64):
    """
    Ingest a file: load, chunk, and upsert to collection.

    Args:
        path: File path to ingest
        collection: ChromaDB collection to upsert into
        source_label: Label for metadata (e.g., filename)
        chunk_size: Chunk size in words
        overlap: Overlap in words

    Returns:
        Number of chunks ingested
    """
    path = Path(path)

    # Load file based on extension
    if path.suffix.lower() == '.pdf':
        text = load_pdf(str(path))
    elif path.suffix.lower() in ['.md', '.markdown']:
        text = load_markdown(str(path))
    else:
        text = load_text_file(str(path))

    if not text:
        logger.warning(f"No text extracted from {path}")
        return 0

    # Chunk text
    chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
    logger.info(f"Created {len(chunks)} chunks from {path}")

    # Prepare chunks for ingestion
    chunk_dicts = []
    for idx, chunk in enumerate(chunks):
        chunk_dicts.append({
            "id": f"{path.stem}_{idx}",
            "text": chunk,
            "metadata": {
                "source": source_label,
                "chunk_index": idx,
                "filename": path.name,
            }
        })

    # Import here to avoid circular dependency
    from . import vector_store
    num_upserted = vector_store.upsert_chunks(collection, chunk_dicts)
    logger.info(f"Ingested {path.name}: {num_upserted} chunks")

    return num_upserted
