"""Input validation utilities for Sahayak AI."""

import re
import logging

logger = logging.getLogger(__name__)


def sanitize_input(text: str) -> str:
    """Sanitize user input by stripping dangerous content.

    Args:
        text: Raw user input string.

    Returns:
        Sanitized string safe for processing.
    """
    if not isinstance(text, str):
        raise ValueError("Input must be a string")
    # Strip leading/trailing whitespace
    text = text.strip()
    # Remove null bytes
    text = text.replace("\x00", "")
    # Basic HTML tag stripping for safety
    text = re.sub(r"<[^>]+>", "", text)
    return text


def validate_length(text: str, max_length: int = 5000) -> str:
    """Validate that input text doesn't exceed maximum length.

    Args:
        text: Input text to validate.
        max_length: Maximum allowed character count.

    Returns:
        The validated text.

    Raises:
        ValueError: If text exceeds max_length.
    """
    if len(text) > max_length:
        raise ValueError(f"Input exceeds {max_length} characters")
    return text
