"""Tests for LangGraph pipeline — 12 tests."""

import pytest
from unittest.mock import patch
from tests.conftest import gemini_side_effect


class TestRunPipeline:
    """Tests for the run_pipeline function."""

    def test_run_pipeline_returns_dict(self, mock_gemini):
        """Pipeline should return a dictionary."""
        from src.pipeline import run_pipeline
        result = run_pipeline("Person fainted")
        assert isinstance(result, dict)

    def test_pipeline_sets_clean_text(self, mock_gemini):
        """Pipeline should set clean_text field."""
        from src.pipeline import run_pipeline
        result = run_pipeline("Person fainted at metro")
        assert "clean_text" in result
        assert len(result["clean_text"]) > 0

    def test_pipeline_sets_category(self, mock_gemini):
        """Pipeline should set category field."""
        from src.pipeline import run_pipeline
        result = run_pipeline("Person fainted")
        assert result["category"] in ["medical", "accident", "disaster", "fire", "crime", "civic", "other"]

    def test_pipeline_sets_severity(self, mock_gemini):
        """Pipeline should set severity field."""
        from src.pipeline import run_pipeline
        result = run_pipeline("Person fainted")
        assert result["severity"] in ["low", "medium", "high", "critical"]

    def test_pipeline_sets_priority(self, mock_gemini):
        """Pipeline should set priority field."""
        from src.pipeline import run_pipeline
        result = run_pipeline("Person fainted")
        assert result["priority"] in ["routine", "urgent", "immediate"]

    def test_pipeline_sets_actions_list(self, mock_gemini):
        """Pipeline should set actions as a list."""
        from src.pipeline import run_pipeline
        result = run_pipeline("Person fainted")
        assert isinstance(result["actions"], list)
        assert len(result["actions"]) > 0

    def test_pipeline_sets_contacts_list(self, mock_gemini):
        """Pipeline should set contacts as a list of dicts."""
        from src.pipeline import run_pipeline
        result = run_pipeline("Person fainted")
        assert isinstance(result["contacts"], list)
        assert len(result["contacts"]) > 0
        assert "name" in result["contacts"][0]

    def test_pipeline_sets_refined_actions(self, mock_gemini):
        """Pipeline should set refined_actions."""
        from src.pipeline import run_pipeline
        result = run_pipeline("Person fainted")
        assert isinstance(result["refined_actions"], list)
        assert len(result["refined_actions"]) > 0

    def test_pipeline_sets_confidence(self, mock_gemini):
        """Pipeline should set confidence field."""
        from src.pipeline import run_pipeline
        result = run_pipeline("Person fainted")
        assert result["confidence"] in ["low", "medium", "high"]

    def test_pipeline_sets_situation(self, mock_gemini):
        """Pipeline should set situation field."""
        from src.pipeline import run_pipeline
        result = run_pipeline("Person fainted at metro")
        assert "situation" in result
        assert len(result["situation"]) > 0

    def test_pipeline_error_graceful_degradation(self):
        """Pipeline should return safe defaults when Gemini fails."""
        with patch("src.gemini.call_gemini_json", side_effect=RuntimeError("API down")):
            from src.pipeline import run_pipeline
            result = run_pipeline("test")
            # Pipeline nodes catch errors and return defaults
            assert isinstance(result, dict)
            assert result.get("category") is not None
            assert result.get("severity") is not None

    def test_pipeline_medical_scenario(self, mock_gemini):
        """Pipeline should correctly handle a medical scenario."""
        from src.pipeline import run_pipeline
        result = run_pipeline("Person fainted at MG Road metro station")
        assert result["category"] == "medical"
        assert result["severity"] == "high"
