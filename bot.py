#!/usr/bin/env python3
# Piazza-Chimp Main Bot
# Polling loop that monitors Piazza and posts AI-generated answers

import time
import logging
import sys
import os
from dotenv import load_dotenv

import config
import db
import piazza_client
import ai_answerer

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_bot():
    """Main bot loop."""
    logger.info("=" * 60)
    logger.info("Piazza-Chimp Bot Starting")
    logger.info("=" * 60)

    # Initialize database
    conn = db.init_db(config.DB_PATH)
    logger.info(f"Database initialized: {config.DB_PATH}")

    # Login to Piazza
    try:
        network = piazza_client.login(
            email=os.getenv("PIAZZA_EMAIL"),
            password=os.getenv("PIAZZA_PASSWORD"),
            network_id=os.getenv("PIAZZA_NETWORK")
        )
    except Exception as e:
        logger.error(f"Failed to login to Piazza: {e}")
        sys.exit(1)

    logger.info(f"Bot ready. Polling every {config.POLL_INTERVAL_SEC} seconds.")
    logger.info("=" * 60)

    cycle_count = 0

    try:
        while True:
            cycle_count += 1
            logger.info(f"\n--- Poll Cycle #{cycle_count} ---")

            # Get unread posts
            unread = piazza_client.get_unread_posts(network)

            if not unread:
                logger.info("No unread posts found")
            else:
                logger.info(f"Processing {len(unread)} unread post(s)")

            for item in unread:
                post_id = item.get("id")
                post_nr = item.get("nr", "?")

                # Check if already answered
                if db.already_answered(conn, post_id):
                    logger.info(f"Post #{post_nr} ({post_id}) already answered, skipping")
                    continue

                time.sleep(config.PIAZZA_CALL_SLEEP)

                # Fetch full post
                full_post = piazza_client.get_full_post(network, post_id)
                if not full_post:
                    logger.warning(f"Could not fetch full post {post_id}")
                    continue

                # Check if we should answer
                if not piazza_client.should_answer(full_post):
                    logger.info(f"Post #{post_nr} does not meet criteria for answering, marking as skipped")
                    db.mark_answered(conn, post_id, full_post.get("nr", 0))
                    continue

                # Extract question content
                history = full_post.get("history", [])
                if not history:
                    logger.warning(f"Post #{post_nr} has no history, skipping")
                    db.mark_answered(conn, post_id, full_post.get("nr", 0))
                    continue

                first_version = history[0]
                subject = first_version.get("subject", "(no subject)")
                html_content = first_version.get("content", "")
                content = piazza_client.strip_html(html_content)

                if not content:
                    logger.warning(f"Post #{post_nr} has no content, skipping")
                    db.mark_answered(conn, post_id, full_post.get("nr", 0))
                    continue

                logger.info(f"Generating answer for post #{post_nr}: {subject[:50]}")

                # Generate answer
                answer = ai_answerer.generate_answer(
                    subject=subject,
                    content=content,
                    course_name=os.getenv("COURSE_NAME"),
                    api_key=os.getenv("ANTHROPIC_API_KEY"),
                )

                if answer is None:
                    logger.warning(f"Failed to generate answer for post #{post_nr}, will retry next cycle")
                    continue

                # Append disclaimer
                answer_with_disclaimer = answer + config.AI_DISCLAIMER

                # Post the answer
                time.sleep(config.PIAZZA_CALL_SLEEP)
                if piazza_client.post_answer(network, full_post, answer_with_disclaimer):
                    db.mark_answered(conn, post_id, full_post.get("nr", 0))
                    logger.info(f"Successfully posted answer to post #{post_nr}")
                else:
                    logger.warning(f"Failed to post answer to post #{post_nr}")

            logger.info(f"Poll cycle complete. Sleeping for {config.POLL_INTERVAL_SEC} seconds...")
            time.sleep(config.POLL_INTERVAL_SEC)

    except KeyboardInterrupt:
        logger.info("\nBot interrupted by user")
        conn.close()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
        conn.close()
        sys.exit(1)


if __name__ == "__main__":
    run_bot()
