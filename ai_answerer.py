# Piazza-Chimp AI Answerer
# Claude API integration with error handling

import time
import logging
import anthropic
from anthropic import RateLimitError, APIConnectionError, APIError

import config

logger = logging.getLogger(__name__)


def get_client(api_key: str) -> anthropic.Anthropic:
    """Create and return an Anthropic client with retries configured."""
    return anthropic.Anthropic(
        api_key=api_key,
        max_retries=3,
        timeout=30.0,
    )


def generate_answer(
    subject: str,
    content: str,
    course_name: str,
    api_key: str,
    context: str = "",
) -> str | None:
    """
    Generate an answer using Claude API.

    Args:
        subject: Post subject/title
        content: Plain text post content
        course_name: Name of the course (for system prompt)
        api_key: Anthropic API key
        context: Optional RAG context (course materials and past Q&As)

    Returns:
        Generated answer text, or None if an error occurred
    """
    client = get_client(api_key)

    system_prompt = f"""You are a helpful teaching assistant for {course_name}.
Answer student questions clearly and concisely.
- Be encouraging and supportive
- If unsure, say so honestly rather than guessing
- Do not address grades, personal matters, or exam answers
- Keep responses under 350 words
- Use plain text (no HTML tags)"""

    # Inject context if available
    if context:
        system_prompt += f"""

[RELEVANT CONTEXT]
{context}
[/RELEVANT CONTEXT]

Use the above context if relevant to answering the question. If the context doesn't help, use general knowledge."""

    user_prompt = f"Subject: {subject}\n\nQuestion: {content}"

    try:
        logger.info(f"Generating answer for: {subject[:50]}...")
        message = client.messages.create(
            model=config.MODEL,
            max_tokens=config.ANTHROPIC_MAX_TOKENS,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ],
        )
        answer = message.content[0].text
        logger.info("Successfully generated answer")
        return answer

    except RateLimitError as e:
        logger.warning(f"Rate limited by Claude API: {e}")
        logger.info("Sleeping for 60 seconds before retry...")
        time.sleep(60)
        return None

    except APIConnectionError as e:
        logger.error(f"Connection error with Claude API: {e}")
        return None

    except APIError as e:
        logger.error(f"Claude API error: {e}")
        return None

    except Exception as e:
        logger.error(f"Unexpected error generating answer: {e}")
        return None
