"""Google Cloud Translation service for Sahayak AI.

Auto-detects language, translates input to English for the pipeline,
then translates response back to the user's original language.
"""

import os
import logging

logger = logging.getLogger(__name__)

_translate_client = None


def _get_client():
    """Lazy-init the Google Cloud Translate v2 client."""
    global _translate_client
    if _translate_client is None:
        try:
            from google.cloud import translate_v2 as translate
            _translate_client = translate.Client()
            logger.info("Google Cloud Translation client initialized")
        except Exception as e:
            logger.warning(f"Cloud Translation unavailable, falling back to passthrough: {e}")
            _translate_client = False  # Mark as unavailable
    return _translate_client


def detect_language(text: str) -> str:
    """Detect the language of the given text.

    Args:
        text: The text to detect the language of.

    Returns:
        ISO 639-1 language code (e.g. 'hi', 'te', 'en').
    """
    client = _get_client()
    if not client:
        return "en"
    try:
        result = client.detect_language(text)
        lang = result.get("language", "en")
        logger.info("Language detected", extra={"language": lang, "confidence": result.get("confidence")})
        return lang
    except Exception as e:
        logger.error(f"Language detection failed: {e}")
        return "en"


def translate_to_english(text: str) -> tuple[str, str]:
    """Translate text to English. Returns (translated_text, source_language).

    Args:
        text: The text to translate.

    Returns:
        Tuple of (translated text, detected source language code).
    """
    client = _get_client()
    if not client:
        return text, "en"
    try:
        result = client.translate(text, target_language="en")
        source_lang = result.get("detectedSourceLanguage", "en")
        translated = result.get("translatedText", text)
        logger.info("Translated to English", extra={"source_language": source_lang})
        return translated, source_lang
    except Exception as e:
        logger.error(f"Translation to English failed: {e}")
        return text, "en"


def translate_from_english(text: str, target_lang: str) -> str:
    """Translate text from English to the target language.

    Args:
        text: The English text to translate.
        target_lang: ISO 639-1 code for target language (e.g. 'hi').

    Returns:
        Translated text, or original on failure.
    """
    if target_lang == "en":
        return text
    client = _get_client()
    if not client:
        return text
    try:
        result = client.translate(text, source_language="en", target_language=target_lang)
        translated = result.get("translatedText", text)
        logger.info("Translated from English", extra={"target_language": target_lang})
        return translated
    except Exception as e:
        logger.error(f"Translation from English failed: {e}")
        return text
