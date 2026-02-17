# Piazza-Chimp Piazza API Wrappers
# Read/write operations with filtering logic

import time
import logging
from html.parser import HTMLParser
from piazza_api import Piazza
from piazza_api.network import UnreadFilter

logger = logging.getLogger(__name__)


class HTMLStripper(HTMLParser):
    """Strip HTML tags from text."""
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []

    def handle_data(self, data):
        self.text.append(data)

    def get_text(self):
        return ''.join(self.text)


def login(email: str, password: str, network_id: str):
    """Login to Piazza and return the Network object."""
    logger.info("Logging in to Piazza...")
    p = Piazza()
    p.user_login(email=email, password=password)
    network = p.network(network_id)
    logger.info("Successfully logged in to Piazza")
    return network


def get_unread_posts(network) -> list:
    """Get list of unread posts from the feed (lightweight API call)."""
    logger.info("Fetching unread posts...")
    try:
        feed = network.get_filtered_feed(UnreadFilter())
        unread_items = feed.get("feed", [])
        logger.info(f"Found {len(unread_items)} unread posts")
        return unread_items
    except Exception as e:
        logger.error(f"Error fetching unread posts: {e}")
        return []


def get_full_post(network, post_id: str) -> dict:
    """Get the full post object including all children."""
    logger.info(f"Fetching full post {post_id}...")
    try:
        post = network.get_post(post_id)
        return post
    except Exception as e:
        logger.error(f"Error fetching full post {post_id}: {e}")
        return {}


def should_answer(full_post: dict, already_answered_check=None) -> bool:
    """
    Determine if the bot should answer this post.

    Filtering rules:
    1. Post type must be "question" (skip notes)
    2. No instructor answer already exists
    3. No "instructor-note" tag
    4. Not already answered by bot (optional check)
    """
    if not full_post:
        return False

    # Rule 1: must be a question
    if full_post.get("type") != "question":
        logger.debug(f"Post {full_post.get('id')} is not a question, skipping")
        return False

    # Rule 2: no instructor answer should exist
    children = full_post.get("children", [])
    for child in children:
        if child.get("type") == "i_answer":
            logger.debug(f"Post {full_post.get('id')} already has instructor answer, skipping")
            return False

    # Rule 3: no instructor-note tag
    tags = full_post.get("tags", [])
    if "instructor-note" in tags:
        logger.debug(f"Post {full_post.get('id')} has instructor-note tag, skipping")
        return False

    # Rule 4: optional DB check
    if already_answered_check is not None:
        post_id = full_post.get("id")
        if already_answered_check(post_id):
            logger.debug(f"Post {post_id} already answered by bot, skipping")
            return False

    return True


def post_answer(network, full_post: dict, answer_text: str) -> bool:
    """
    Post an answer to the post.

    Strategy:
    - Try create_instructor_answer first
    - On permission error, fall back to create_followup with a note
    - Return True if successful, False otherwise
    """
    post_id = full_post.get("id")
    post_nr = full_post.get("nr")

    try:
        # Try to post as instructor answer first
        logger.info(f"Attempting to post instructor answer to post #{post_nr}...")
        network.create_instructor_answer(full_post, answer_text, revision=0)
        logger.info(f"Successfully posted instructor answer to post #{post_nr}")
        return True
    except Exception as e:
        # If permission denied or other error, fall back to followup
        if "permission" in str(e).lower() or "instructor" in str(e).lower():
            logger.info(f"Instructor answer failed (permission), falling back to followup for post #{post_nr}...")
            try:
                followup_text = f"(AI Bot - Generated Answer)\n\n{answer_text}"
                network.create_followup(full_post, followup_text)
                logger.info(f"Successfully posted followup to post #{post_nr}")
                return True
            except Exception as fallback_e:
                logger.error(f"Fallback followup also failed for post #{post_nr}: {fallback_e}")
                return False
        else:
            logger.error(f"Error posting answer to post #{post_nr}: {e}")
            return False


def strip_html(html_str: str) -> str:
    """Strip HTML tags from a string."""
    if not html_str:
        return ""
    stripper = HTMLStripper()
    try:
        stripper.feed(html_str)
        return stripper.get_text().strip()
    except Exception as e:
        logger.warning(f"Error stripping HTML: {e}")
        return html_str
