"""Tests for Gemini service — 10 tests."""

import pytest
import json
from unittest.mock import patch, MagicMock


class TestCallGemini:
    """Tests for call_gemini function."""

    def test_call_gemini_returns_string(self):
        """call_gemini should return a string."""
        mock_response = MagicMock()
        mock_response.text = "test response"
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response

        with patch("src.gemini._get_model", return_value=mock_model):
            from src.gemini import call_gemini, _cache
            _cache.clear()
            result = call_gemini("test prompt")
            assert isinstance(result, str)
            assert result == "test response"

    def test_call_gemini_raises_on_api_error(self):
        """call_gemini should raise RuntimeError on API failure."""
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API error")

        with patch("src.gemini._get_model", return_value=mock_model):
            from src.gemini import call_gemini, _cache
            _cache.clear()
            with pytest.raises(RuntimeError, match="Gemini call failed"):
                call_gemini("failing prompt unique 123")

    def test_empty_prompt_does_not_crash(self):
        """Empty prompt should still work without crashing."""
        mock_response = MagicMock()
        mock_response.text = "{}"
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response

        with patch("src.gemini._get_model", return_value=mock_model):
            from src.gemini import call_gemini, _cache
            _cache.clear()
            result = call_gemini("")
            assert isinstance(result, str)

    def test_unicode_prompt_handled(self):
        """Unicode/Hindi prompt should be handled correctly."""
        mock_response = MagicMock()
        mock_response.text = '{"clean_text": "test"}'
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response

        with patch("src.gemini._get_model", return_value=mock_model):
            from src.gemini import call_gemini, _cache
            _cache.clear()
            result = call_gemini("मेट्रो में बेहोश unique_unicode_test")
            assert isinstance(result, str)

    def test_cache_same_prompt_returns_cached_result(self):
        """Same prompt should return cached result without re-calling API."""
        mock_response = MagicMock()
        mock_response.text = "cached response"
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response

        with patch("src.gemini._get_model", return_value=mock_model):
            from src.gemini import call_gemini, _cache
            _cache.clear()
            result1 = call_gemini("cache test prompt unique 456")
            result2 = call_gemini("cache test prompt unique 456")
            assert result1 == result2
            # Model should be called only once due to cache
            assert mock_model.generate_content.call_count == 1


class TestCallGeminiJson:
    """Tests for call_gemini_json function."""

    def test_call_gemini_json_returns_dict(self):
        """call_gemini_json should return a dict."""
        with patch("src.gemini.call_gemini", return_value='{"category": "medical"}'):
            from src.gemini import call_gemini_json
            result = call_gemini_json("test")
            assert isinstance(result, dict)
            assert result["category"] == "medical"

    def test_call_gemini_json_strips_markdown_fences(self):
        """Should handle markdown code fences around JSON."""
        with patch("src.gemini.call_gemini", return_value='```json\n{"severity": "high"}\n```'):
            from src.gemini import call_gemini_json
            result = call_gemini_json("test fences")
            assert result["severity"] == "high"

    def test_call_gemini_json_handles_invalid_json_returns_empty_dict(self):
        """Invalid JSON should return empty dict, not crash."""
        with patch("src.gemini.call_gemini", return_value="not valid json at all"):
            from src.gemini import call_gemini_json
            result = call_gemini_json("bad json test")
            assert result == {}

    def test_call_gemini_json_with_valid_json_string(self):
        """Valid plain JSON string should be parsed correctly."""
        with patch("src.gemini.call_gemini", return_value='{"key": "value", "count": 42}'):
            from src.gemini import call_gemini_json
            result = call_gemini_json("valid json test")
            assert result["key"] == "value"
            assert result["count"] == 42

    def test_call_gemini_json_with_extra_whitespace(self):
        """JSON with extra whitespace should still be parsed."""
        with patch("src.gemini.call_gemini", return_value='  \n  {"data": true}  \n  '):
            from src.gemini import call_gemini_json
            result = call_gemini_json("whitespace test")
            assert result["data"] is True
