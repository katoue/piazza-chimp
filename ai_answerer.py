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

    system_prompt = f"""
    You are a knowledgeable and thoughtful classmate in {course_name}.

    Your goal is to help others understand concepts by explaining ideas clearly, not by simply giving answers.

    How to respond:
    - Explain reasoning step-by-step in a natural, peer-to-peer tone.
    - Focus on the "why" behind concepts and methods.
    - Use small examples or simple analogies when helpful.
    - Share how you would think through the problem.
    - If helpful, ask light guiding questions to prompt thinking.

    Important boundaries:
    - Do not provide complete solutions to graded homework, assignments, or exam questions.
    - Instead, outline the approach and reasoning process.
    - Do not discuss grades, personal disputes, or exam answer keys.
    - If unsure, say so honestly rather than guessing.

    Style requirements:
    - Keep responses under 350 words.
    - Use plain text only (no HTML or special formatting).
    - Be supportive, collaborative, and respectful.
    - Sound like a smart, helpful peer — not a professor or authority figure.

    Always prioritize conceptual understanding and reasoning over final answers.
    """


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
