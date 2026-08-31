"""GPT-OSS-20B client and response validation. No fallback model."""

import logging
from functools import lru_cache

from openai import OpenAI

from . import config
from .prompts import (HEALTHCARE_INDICATORS, RESPONSE_PREFIXES,
                      build_healthcare_prompt)

logger = logging.getLogger(__name__)

UNAVAILABLE_MESSAGE = (
    "🚨 I'm currently experiencing technical difficulties with my AI system. "
    "Please try again in a moment, or contact our clinic directly at "
    f"{config.CLINIC_PHONE} for immediate assistance."
)


@lru_cache
def get_client() -> OpenAI:
    """Initialize the OpenAI-compatible client against the Hugging Face router."""
    return OpenAI(base_url=config.BASE_URL, api_key=config.require_token())


def _extract_content(response) -> str:
    """Pull the message text out of a completion, checking each layer."""
    if not response:
        raise Exception("Empty response from API")
    if not response.choices or len(response.choices) == 0:
        raise Exception("No choices in response")

    choice = response.choices[0]
    if not choice:
        raise Exception("Empty choice in response")
    if not choice.message:
        raise Exception("No message in choice")

    content = choice.message.content
    if not content:
        raise Exception("Empty content in message")
    return content


def _clean_content(content: str) -> str:
    """Strip the echoed prompt prefix and reject replies that are too short."""
    content = content.strip()
    if not content or len(content) < 10:
        raise Exception("Response too short or empty")

    for prefix in RESPONSE_PREFIXES:
        if prefix in content:
            content = content.split(prefix)[-1].strip()
            break

    # Ensure response is professional and healthcare-appropriate
    if not any(word in content.lower() for word in HEALTHCARE_INDICATORS):
        # If no healthcare indicators, check if it's at least a reasonable response
        if len(content) < 20 or not any(char.isalpha() for char in content):
            raise Exception("Response not healthcare-appropriate")

    return content


def get_gpt_oss_response(message: str) -> str:
    """Get response from GPT-OSS-20B with maximum robustness"""
    try:
        response = get_client().chat.completions.create(
            model=config.MODEL,
            messages=[{"role": "user", "content": build_healthcare_prompt(message)}],
            max_tokens=config.MAX_TOKENS,
            temperature=config.TEMPERATURE,
            timeout=config.REQUEST_TIMEOUT,
        )
        content = _clean_content(_extract_content(response))
        logger.info(f"GPT-OSS-20B response: {content[:50]}...")
        return content

    except Exception as e:
        logger.error(f"GPT-OSS-20B failed: {e}")
        raise Exception(f"GPT-OSS-20B is not available: {str(e)}")


def get_ai_response(message: str) -> str:
    """Main AI response function - GPT-OSS-20B or nothing"""
    try:
        return get_gpt_oss_response(message)
    except Exception as e:
        logger.error(f"AI response failed: {e}")
        # NO FALLBACK - Return error message
        return UNAVAILABLE_MESSAGE
