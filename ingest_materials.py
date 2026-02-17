#!/usr/bin/env python3
# Ingest course materials into ChromaDB
# Usage: python ingest_materials.py --dir ./course_files [--ext pdf,md,txt]

import argparse
import logging
import sys
from pathlib import Path

import config
from rag import vector_store, ingester

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Ingest course materials into ChromaDB"
    )
    parser.add_argument(
        "--dir",
        type=str,
        required=True,
        help="Directory containing course files"
    )
    parser.add_argument(
        "--ext",
        type=str,
        default="pdf,md,txt",
        help="Comma-separated file extensions to process (default: pdf,md,txt)"
    )

    args = parser.parse_args()

    # Parse extensions
    extensions = [f".{ext.strip().lower()}" for ext in args.ext.split(",")]
    logger.info(f"Processing file extensions: {extensions}")

    # Verify directory exists
    materials_dir = Path(args.dir)
    if not materials_dir.exists():
        logger.error(f"Directory not found: {materials_dir}")
        sys.exit(1)

    if not materials_dir.is_dir():
        logger.error(f"Not a directory: {materials_dir}")
        sys.exit(1)

    # Initialize ChromaDB
    client = vector_store.init_store(config.CHROMA_DB_PATH)
    collection = vector_store.get_or_create_collection(
        client, config.COLLECTION_MATERIALS
    )

    # Scan and ingest files
    files_to_ingest = []
    for ext in extensions:
        files_to_ingest.extend(materials_dir.glob(f"*{ext}"))

    if not files_to_ingest:
        logger.warning(f"No files found with extensions {extensions} in {materials_dir}")
        sys.exit(0)

    logger.info(f"Found {len(files_to_ingest)} file(s) to ingest")

    total_chunks = 0
    for file_path in sorted(files_to_ingest):
        try:
            chunks_added = ingester.ingest_file(
                str(file_path),
                collection,
                source_label=file_path.name,
                chunk_size=config.RAG_CHUNK_SIZE,
                overlap=config.RAG_CHUNK_OVERLAP,
            )
            total_chunks += chunks_added
        except Exception as e:
            logger.error(f"Error ingesting {file_path}: {e}")

    logger.info(f"Ingestion complete. Total chunks added: {total_chunks}")


if __name__ == "__main__":
    main()
