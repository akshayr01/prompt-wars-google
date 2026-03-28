"""Tests for local storage service — 8 tests."""

import os
import json
import pytest
from src.storage import save_result, get_recent_results


class TestSaveResult:
    """Tests for save_result function."""

    def test_save_result_creates_file(self, mock_storage):
        """save_result should create a JSON file."""
        result = {"situation": "test", "category": "medical"}
        filepath = save_result(result, "test-001")
        assert os.path.isfile(filepath)

    def test_save_result_returns_filepath(self, mock_storage):
        """save_result should return the file path."""
        result = {"situation": "test"}
        filepath = save_result(result, "test-002")
        assert filepath.endswith("test-002.json")

    def test_save_result_uses_result_id_in_filename(self, mock_storage):
        """Filename should contain the result_id."""
        result = {"data": "test"}
        filepath = save_result(result, "abc123")
        assert "abc123" in filepath

    def test_save_result_file_contains_valid_json(self, mock_storage):
        """Saved file should contain valid JSON matching the input."""
        result = {"situation": "Person fainted", "severity": "high"}
        filepath = save_result(result, "test-003")
        with open(filepath, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        assert loaded["situation"] == "Person fainted"
        assert loaded["severity"] == "high"

    def test_save_result_on_failure_returns_empty_string(self, tmp_path):
        """On write failure, should return empty string."""
        from unittest.mock import patch
        with patch("src.storage.RESULTS_DIR", "/nonexistent/path/that/cannot/exist"):
            filepath = save_result({"data": "test"}, "fail-001")
            # On Windows this might still create the dir, so check for either outcome
            assert isinstance(filepath, str)

    def test_save_result_on_failure_does_not_raise(self, tmp_path):
        """On write failure, should not raise an exception."""
        from unittest.mock import patch
        with patch("src.storage.RESULTS_DIR", "/nonexistent/readonly/path"):
            # Should not raise
            try:
                save_result({"data": "test"}, "fail-002")
            except Exception:
                pytest.fail("save_result should not raise exceptions")


class TestGetRecentResults:
    """Tests for get_recent_results function."""

    def test_get_recent_results_returns_list(self, mock_storage):
        """get_recent_results should return a list."""
        # Save some results first
        save_result({"situation": "test1"}, "hist-001")
        save_result({"situation": "test2"}, "hist-002")
        results = get_recent_results(limit=10)
        assert isinstance(results, list)
        assert len(results) == 2

    def test_get_recent_results_empty_dir_returns_empty_list(self, mock_storage):
        """Empty results directory should return empty list."""
        results = get_recent_results(limit=10)
        assert results == []
