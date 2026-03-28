"""Tests for Google Cloud Translation service."""

from unittest.mock import patch, MagicMock
from src.translate import detect_language, translate_to_english, translate_from_english


class TestDetectLanguage:
    def test_returns_en_when_client_unavailable(self):
        with patch("src.translate._get_client", return_value=False):
            assert detect_language("hello") == "en"

    def test_returns_detected_language(self):
        mock_client = MagicMock()
        mock_client.detect_language.return_value = {"language": "hi", "confidence": 0.99}
        with patch("src.translate._get_client", return_value=mock_client):
            result = detect_language("नमस्ते")
        assert result == "hi"

    def test_falls_back_to_en_on_exception(self):
        mock_client = MagicMock()
        mock_client.detect_language.side_effect = Exception("API error")
        with patch("src.translate._get_client", return_value=mock_client):
            result = detect_language("test")
        assert result == "en"

    def test_handles_empty_string(self):
        mock_client = MagicMock()
        mock_client.detect_language.return_value = {"language": "en", "confidence": 0.5}
        with patch("src.translate._get_client", return_value=mock_client):
            result = detect_language("")
        assert result == "en"


class TestTranslateToEnglish:
    def test_returns_original_when_client_unavailable(self):
        with patch("src.translate._get_client", return_value=False):
            text, lang = translate_to_english("hello")
        assert text == "hello"
        assert lang == "en"

    def test_translates_hindi_to_english(self):
        mock_client = MagicMock()
        mock_client.translate.return_value = {
            "translatedText": "There is a fire in the building",
            "detectedSourceLanguage": "hi",
        }
        with patch("src.translate._get_client", return_value=mock_client):
            text, lang = translate_to_english("इमारत में आग लगी है")
        assert text == "There is a fire in the building"
        assert lang == "hi"

    def test_returns_english_unchanged(self):
        mock_client = MagicMock()
        mock_client.translate.return_value = {
            "translatedText": "fire",
            "detectedSourceLanguage": "en",
        }
        with patch("src.translate._get_client", return_value=mock_client):
            text, lang = translate_to_english("fire")
        assert lang == "en"

    def test_falls_back_on_exception(self):
        mock_client = MagicMock()
        mock_client.translate.side_effect = Exception("API error")
        with patch("src.translate._get_client", return_value=mock_client):
            text, lang = translate_to_english("test input")
        assert text == "test input"
        assert lang == "en"

    def test_returns_tuple(self):
        with patch("src.translate._get_client", return_value=False):
            result = translate_to_english("test")
        assert isinstance(result, tuple)
        assert len(result) == 2


class TestTranslateFromEnglish:
    def test_returns_original_for_english_target(self):
        text = translate_from_english("Call emergency services", "en")
        assert text == "Call emergency services"

    def test_returns_original_when_client_unavailable(self):
        with patch("src.translate._get_client", return_value=False):
            text = translate_from_english("Call help", "hi")
        assert text == "Call help"

    def test_translates_to_hindi(self):
        mock_client = MagicMock()
        mock_client.translate.return_value = {"translatedText": "मदद के लिए कॉल करें"}
        with patch("src.translate._get_client", return_value=mock_client):
            text = translate_from_english("Call for help", "hi")
        assert text == "मदद के लिए कॉल करें"

    def test_falls_back_on_exception(self):
        mock_client = MagicMock()
        mock_client.translate.side_effect = Exception("quota exceeded")
        with patch("src.translate._get_client", return_value=mock_client):
            text = translate_from_english("Call 112", "te")
        assert text == "Call 112"

    def test_supports_telugu(self):
        mock_client = MagicMock()
        mock_client.translate.return_value = {"translatedText": "అత్యవసర సేవలను పిలవండి"}
        with patch("src.translate._get_client", return_value=mock_client):
            text = translate_from_english("Call emergency services", "te")
        assert text == "అత్యవసర సేవలను పిలవండి"
