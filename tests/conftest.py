"""Shared test fixtures for Sahayak AI test suite."""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


# Default Gemini mock response — covers all pipeline nodes
MOCK_UNDERSTAND = {"clean_text": "Person fainted at metro station", "situation": "Person has fainted at MG Road metro station", "intent": "medical_emergency"}
MOCK_CLASSIFY = {"category": "medical", "severity": "high", "priority": "immediate"}
MOCK_PLAN = {"actions": ["Call 108 ambulance", "Keep person lying flat", "Check breathing"], "contacts": [{"name": "Ambulance", "number": "108"}, {"name": "Police", "number": "100"}]}
MOCK_ACT = {"refined_actions": ["Call 108 ambulance immediately", "Keep the person lying flat on their back", "Check if the person is breathing"]}
MOCK_VALIDATE = {"confidence": "high", "gaps": []}


def gemini_side_effect(prompt: str) -> dict:
    """Return appropriate mock based on prompt content."""
    prompt_lower = prompt.lower()
    if "clean and interpret" in prompt_lower:
        return MOCK_UNDERSTAND
    elif "classify" in prompt_lower:
        return MOCK_CLASSIFY
    elif "generate response" in prompt_lower:
        return MOCK_PLAN
    elif "refine and order" in prompt_lower:
        return MOCK_ACT
    elif "check this emergency" in prompt_lower or "gaps" in prompt_lower:
        return MOCK_VALIDATE
    return MOCK_UNDERSTAND


@pytest.fixture
def mock_gemini():
    """Patch call_gemini_json to return appropriate mock data."""
    with patch("src.gemini.call_gemini_json", side_effect=gemini_side_effect) as mock:
        yield mock


@pytest.fixture
def mock_gemini_raw():
    """Patch call_gemini to return raw string."""
    with patch("src.gemini.call_gemini", return_value='{"test": "data"}') as mock:
        yield mock


@pytest.fixture
def mock_storage(tmp_path):
    """Patch storage RESULTS_DIR to use temporary directory."""
    with patch("src.storage.RESULTS_DIR", str(tmp_path)) as mock:
        yield tmp_path


@pytest.fixture
def client(mock_gemini, mock_storage):
    """Test client with all external services mocked."""
    from main import app
    return TestClient(app)


@pytest.fixture
def client_no_mock():
    """Test client without mocks — for validation-only tests."""
    from main import app
    return TestClient(app)


@pytest.fixture
def sample_medical():
    """Sample medical emergency input."""
    return "Person fainted at MG Road metro station"


@pytest.fixture
def sample_hindi():
    """Sample Hindi emergency input."""
    return "मेट्रो में व्यक्ति बेहोश हो गया"


@pytest.fixture
def sample_disaster():
    """Sample disaster emergency input."""
    return "Water entering homes in Koramangala, people stuck on rooftops"
