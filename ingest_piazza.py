#!/usr/bin/env python3
# Ingest Piazza Q&A history into ChromaDB
# Usage: python ingest_piazza.py

import logging
import sys
import os
import time
from dotenv import load_dotenv

import config
import piazza_client
from rag import vector_store

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def extract_qa_pair(post: dict) -> str | None:
    """
    Extract Q&A pair from a post if it has an accepted answer.

    Args:
        post: Full post object from Piazza API

    Returns:
        Formatted Q&A string, or None if no answer found
    """
    # Get question from first history entry
    history = post.get("history", [])
    if not history:
        return None

    first_version = history[0]
    subject = first_version.get("subject", "")
    html_content = first_version.get("content", "")
    question_content = piazza_client.strip_html(html_content)

    if not question_content:
        return None

    # Look for accepted answer (s_answer)
    children = post.get("children", [])
    answer_text = None

    for child in children:
        if child.get("type") == "s_answer":
            html_answer = child.get("content", "")
            answer_text = piazza_client.strip_html(html_answer)
            break

    if not answer_text:
        return None

    # Format as Q&A pair
    qa_pair = f"Q: {subject}\n{question_content}\n\nA: {answer_text}"
    return qa_pair


def main():
    logger.info("=" * 60)
    logger.info("Ingesting Piazza Q&A History")
    logger.info("=" * 60)

    # Get credentials
    email = os.getenv("PIAZZA_EMAIL")
    password = os.getenv("PIAZZA_PASSWORD")
    network_id = os.getenv("PIAZZA_NETWORK")

    if not all([email, password, network_id]):
        logger.error("Missing Piazza credentials in .env")
        sys.exit(1)

    # Login to Piazza
    try:
        network = piazza_client.login(email=email, password=password, network_id=network_id)
    except Exception as e:
        logger.error(f"Failed to login to Piazza: {e}")
        sys.exit(1)

    # Initialize ChromaDB
    client = vector_store.init_store(config.CHROMA_DB_PATH)
    collection = vector_store.get_or_create_collection(
        client, config.COLLECTION_PIAZZA
    )

    # Fetch posts - try to get all posts
    logger.info("Fetching all posts from Piazza...")
    try:
        # Try with a large limit first (Piazza API may have max limit)
        feed = network.get_feed(limit=10000)
        feed_items = feed.get("feed", [])
        logger.info(f"Found {len(feed_items)} posts in feed")
    except Exception as e:
        logger.error(f"Error fetching feed: {e}")
        sys.exit(1)

    # Extract Q&A pairs
    chunks = []
    qa_count = 0
    skipped_count = 0

    for item in feed_items:
        post_id = item.get("id")
        post_nr = item.get("nr", "?")

        try:
            time.sleep(config.PIAZZA_CALL_SLEEP)
            full_post = piazza_client.get_full_post(network, post_id)

            if not full_post:
                logger.debug(f"Could not fetch post {post_id}")
                skipped_count += 1
                continue

            # Skip if not a question
            if full_post.get("type") != "question":
                skipped_count += 1
                continue

            # Try to extract Q&A pair
            qa_pair = extract_qa_pair(full_post)
            if not qa_pair:
                skipped_count += 1
                continue

            # Add to chunks
            tags = full_post.get("tags", [])
            chunks.append({
                "id": post_id,
                "text": qa_pair,
                "metadata": {
                    "post_nr": int(post_nr) if isinstance(post_nr, (int, str)) and str(post_nr).isdigit() else 0,
                    "tags": ",".join(tags),
                }
            })
            qa_count += 1

            if qa_count % 10 == 0:
                logger.info(f"Extracted {qa_count} Q&A pairs so far...")

        except Exception as e:
            logger.error(f"Error processing post {post_id}: {e}")
            skipped_count += 1

    # Upsert to ChromaDB
    if chunks:
        logger.info(f"Upserting {len(chunks)} Q&A pairs to ChromaDB...")
        vector_store.upsert_chunks(collection, chunks)
        logger.info(f"Successfully ingested {qa_count} Q&A pairs")
    else:
        logger.info("No Q&A pairs found to ingest")

    logger.info(f"Summary: {qa_count} Q&A pairs ingested, {skipped_count} posts skipped")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
