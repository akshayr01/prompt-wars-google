"""Tests for input validation — 12 tests."""

import pytest
from pydantic import ValidationError
from src.schemas import AnalyzeRequest


class TestAnalyzeRequestValidation:
    """Tests for AnalyzeRequest Pydantic model validation."""

    def test_valid_input_passes(self):
        """Valid input should pass validation."""
        req = AnalyzeRequest(input="Person fainted at metro station")
        assert req.input == "Person fainted at metro station"

    def test_empty_string_raises_validation_error(self):
        """Empty string should raise ValidationError (min_length=1)."""
        with pytest.raises(ValidationError):
            AnalyzeRequest(input="")

    def test_whitespace_only_raises_validation_error(self):
        """Whitespace-only input should raise ValidationError."""
        with pytest.raises(ValidationError):
            AnalyzeRequest(input="   \n\t  ")

    def test_none_raises_validation_error(self):
        """None input should raise ValidationError."""
        with pytest.raises(ValidationError):
            AnalyzeRequest(input=None)

    def test_5000_chars_passes(self):
        """Exactly 5000 characters should pass validation."""
        req = AnalyzeRequest(input="a" * 5000)
        assert len(req.input) == 5000

    def test_5001_chars_raises_validation_error(self):
        """5001 characters should raise ValidationError (max_length=5000)."""
        with pytest.raises(ValidationError):
            AnalyzeRequest(input="a" * 5001)

    def test_unicode_input_passes(self):
        """Unicode text should pass validation."""
        req = AnalyzeRequest(input="Emergency: 日本語テスト")
        assert "日本語" in req.input

    def test_hindi_input_passes(self):
        """Hindi text should pass validation."""
        req = AnalyzeRequest(input="मेट्रो में व्यक्ति बेहोश हो गया")
        assert "मेट्रो" in req.input

    def test_telugu_input_passes(self):
        """Telugu text should pass validation."""
        req = AnalyzeRequest(input="మెట్రోలో వ్యక్తి స్పృహ కోల్పోయాడు")
        assert "మెట్రో" in req.input

    def test_leading_whitespace_stripped(self):
        """Leading whitespace should be stripped."""
        req = AnalyzeRequest(input="   Person fainted")
        assert req.input == "Person fainted"

    def test_trailing_whitespace_stripped(self):
        """Trailing whitespace should be stripped."""
        req = AnalyzeRequest(input="Person fainted   ")
        assert req.input == "Person fainted"

    def test_non_string_raises_validation_error(self):
        """Non-string input (int) should raise ValidationError."""
        with pytest.raises(ValidationError):
            AnalyzeRequest(input=12345)
