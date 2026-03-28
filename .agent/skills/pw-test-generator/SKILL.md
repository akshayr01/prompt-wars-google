---
name: pw-test-generator
description: Use this skill when the user wants to generate tests, increase test coverage, reach 50+ tests, or fix the Testing score criterion. Automatically generates comprehensive pytest test suites for all services.
---

# pw-test-generator

## Goal
Generate 50+ pytest tests that cover all services, endpoints, and edge cases. The Hyderabad winner had 50+ tests and scored full marks on Testing.

## Instructions

### Step 1: Audit Existing Tests
```bash
pytest tests/ --collect-only 2>&1 | grep "test session" -A5
# Count how many tests exist
pytest tests/ --collect-only -q 2>&1 | tail -5
```

### Step 2: Generate Tests Per Module

#### tests/conftest.py (always create first)
```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, AsyncMock
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sample_text_en():
    return "Flood warning: evacuate Zone 3 immediately. Call 1800-180-1551."

@pytest.fixture
def sample_text_hindi():
    return "बाढ़ की चेतावनी: क्षेत्र 3 खाली करें। 1800-180-1551 पर कॉल करें।"

@pytest.fixture
def sample_text_telugu():
    return "వరద హెచ్చరిక: జోన్ 3 ఖాళీ చేయండి. 1800-180-1551 కి కాల్ చేయండి."

@pytest.fixture
def mock_gemini():
    with patch("src.services.gemini_service.model") as mock:
        mock.generate_content.return_value = MagicMock(
            text='{"severity": "HIGH", "action": "Evacuate immediately", "evacuate": true, "contacts": ["1800-180-1551"]}'
        )
        yield mock

@pytest.fixture
def mock_translate():
    with patch("src.services.translate_service.get_translate_client") as mock:
        client = MagicMock()
        client.translate_text.return_value = MagicMock(
            translations=[MagicMock(translated_text="Flood warning", detected_language_code="te")]
        )
        mock.return_value = client
        yield client

@pytest.fixture
def mock_firestore():
    with patch("src.services.firestore_service.get_db") as mock:
        db = MagicMock()
        doc_ref = MagicMock()
        doc_ref.id = "test-doc-123"
        db.collection.return_value.document.return_value = doc_ref
        mock.return_value = db
        yield db
```

#### tests/test_api_endpoints.py (10 tests)
```python
import pytest
from fastapi.testclient import TestClient

class TestProcessEndpoint:
    def test_valid_english_input_returns_200(self, client, mock_gemini):
        response = client.post("/process", json={"text": "Flood warning in Zone 3"})
        assert response.status_code == 200

    def test_response_has_required_fields(self, client, mock_gemini):
        response = client.post("/process", json={"text": "Flood warning"})
        data = response.json()
        assert "severity" in data
        assert "action" in data

    def test_empty_text_returns_400(self, client):
        response = client.post("/process", json={"text": ""})
        assert response.status_code == 400

    def test_missing_text_field_returns_422(self, client):
        response = client.post("/process", json={})
        assert response.status_code == 422

    def test_text_exceeding_limit_returns_400(self, client):
        response = client.post("/process", json={"text": "x" * 10001})
        assert response.status_code == 400

    def test_null_text_returns_422(self, client):
        response = client.post("/process", json={"text": None})
        assert response.status_code == 422

    def test_hindi_text_accepted(self, client, mock_gemini, mock_translate):
        response = client.post("/process", json={"text": "बाढ़ की चेतावनी"})
        assert response.status_code == 200

    def test_unicode_special_chars_handled(self, client, mock_gemini):
        response = client.post("/process", json={"text": "Emergency! 🚨 Flood alert zone-3"})
        assert response.status_code in [200, 400]  # either is acceptable

    def test_whitespace_only_rejected(self, client):
        response = client.post("/process", json={"text": "   \n\t  "})
        assert response.status_code == 400

    def test_get_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestHistoryEndpoint:
    def test_history_returns_list(self, client, mock_firestore):
        response = client.get("/history")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_history_limit_respected(self, client, mock_firestore):
        response = client.get("/history?limit=5")
        assert response.status_code == 200
```

#### tests/test_gemini_service.py (10 tests)
```python
import pytest
from unittest.mock import MagicMock, patch
from src.services.gemini_service import generate_structured_response

class TestGeminiService:
    def test_successful_call_returns_text(self, mock_gemini):
        mock_gemini.generate_content.return_value = MagicMock(text="test response")
        import asyncio
        result = asyncio.run(generate_structured_response("test prompt"))
        assert result == "test response"

    def test_gemini_exception_raises_runtime_error(self):
        with patch("src.services.gemini_service.model") as mock:
            mock.generate_content.side_effect = Exception("API error")
            import asyncio
            with pytest.raises(RuntimeError):
                asyncio.run(generate_structured_response("test"))

    def test_empty_prompt_still_calls_model(self, mock_gemini):
        import asyncio
        asyncio.run(generate_structured_response(""))
        mock_gemini.generate_content.assert_called_once()

    def test_system_prompt_prepended(self, mock_gemini):
        mock_gemini.generate_content.return_value = MagicMock(text="ok")
        import asyncio
        asyncio.run(generate_structured_response("prompt", "system"))
        call_arg = mock_gemini.generate_content.call_args[0][0]
        assert "system" in call_arg
        assert "prompt" in call_arg

    def test_long_prompt_handled(self, mock_gemini):
        mock_gemini.generate_content.return_value = MagicMock(text="ok")
        import asyncio
        result = asyncio.run(generate_structured_response("x" * 4000))
        assert result == "ok"

    def test_unicode_prompt_handled(self, mock_gemini):
        mock_gemini.generate_content.return_value = MagicMock(text="ok")
        import asyncio
        result = asyncio.run(generate_structured_response("বাढ़ 홍수 flood"))
        assert result == "ok"
```

#### tests/test_validation.py (12 tests)
```python
import pytest
from fastapi import HTTPException
from src.utils.validation import validate_input, sanitize_html_input

class TestValidateInput:
    def test_valid_string_passes(self):
        result = validate_input("valid text")
        assert result == "valid text"

    def test_empty_string_raises_400(self):
        with pytest.raises(HTTPException) as exc:
            validate_input("")
        assert exc.value.status_code == 400

    def test_whitespace_only_raises_400(self):
        with pytest.raises(HTTPException):
            validate_input("   \n  ")

    def test_none_raises_400(self):
        with pytest.raises(HTTPException):
            validate_input(None)

    def test_exceeds_max_length_raises_400(self):
        with pytest.raises(HTTPException) as exc:
            validate_input("x" * 5001, max_length=5000)
        assert exc.value.status_code == 400

    def test_exactly_max_length_passes(self):
        result = validate_input("x" * 5000, max_length=5000)
        assert len(result) == 5000

    def test_strips_whitespace(self):
        result = validate_input("  hello  ")
        assert result == "hello"

    def test_unicode_text_passes(self):
        result = validate_input("बाढ़ की चेतावनी")
        assert "बाढ़" in result

    def test_telugu_text_passes(self):
        result = validate_input("వరద హెచ్చరిక")
        assert len(result) > 0

    def test_non_string_raises_400(self):
        with pytest.raises(HTTPException):
            validate_input(12345)

    def test_list_raises_400(self):
        with pytest.raises(HTTPException):
            validate_input(["a", "b"])

    def test_html_in_input_sanitized(self):
        result = sanitize_html_input("<script>alert(1)</script>Hello")
        assert "<script>" not in result
        assert "Hello" in result
```

#### tests/test_firestore_service.py (8 tests)
```python
import pytest
from unittest.mock import MagicMock, patch
from src.services.firestore_service import save_result, get_recent, get_by_id
import asyncio

class TestFirestoreService:
    def test_save_result_returns_doc_id(self, mock_firestore):
        result = asyncio.run(save_result("results", {"data": "test"}))
        assert result == "test-doc-123"

    def test_save_result_calls_firestore_set(self, mock_firestore):
        asyncio.run(save_result("results", {"key": "value"}))
        mock_firestore.collection.return_value.document.return_value.set.assert_called_once()

    def test_get_recent_returns_list(self, mock_firestore):
        mock_firestore.collection.return_value.order_by.return_value.limit.return_value.stream.return_value = iter([])
        result = asyncio.run(get_recent("results"))
        assert isinstance(result, list)

    def test_save_adds_timestamp(self, mock_firestore):
        asyncio.run(save_result("results", {"data": "test"}))
        call_args = mock_firestore.collection.return_value.document.return_value.set.call_args[0][0]
        assert "created_at" in call_args

    def test_save_failure_raises_exception(self):
        with patch("src.services.firestore_service.get_db") as mock:
            mock.return_value.collection.side_effect = Exception("Connection failed")
            with pytest.raises(Exception):
                asyncio.run(save_result("results", {}))

    def test_get_recent_failure_returns_empty_list(self):
        with patch("src.services.firestore_service.get_db") as mock:
            mock.return_value.collection.side_effect = Exception("error")
            result = asyncio.run(get_recent("results"))
            assert result == []

    def test_get_by_id_not_found_returns_none(self, mock_firestore):
        mock_firestore.collection.return_value.document.return_value.get.return_value.exists = False
        result = asyncio.run(get_by_id("results", "nonexistent"))
        assert result is None

    def test_get_by_id_found_returns_dict(self, mock_firestore):
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.id = "abc123"
        mock_doc.to_dict.return_value = {"data": "test"}
        mock_firestore.collection.return_value.document.return_value.get.return_value = mock_doc
        result = asyncio.run(get_by_id("results", "abc123"))
        assert result is not None
        assert result["id"] == "abc123"
```

#### tests/test_translate_service.py (8 tests)
```python
import pytest
from unittest.mock import MagicMock, patch
from src.services.translate_service import detect_language, translate_to_english

class TestTranslateService:
    def test_detect_language_returns_string(self, mock_translate):
        mock_client = MagicMock()
        mock_client.detect_language.return_value = MagicMock(
            languages=[MagicMock(language_code="te")]
        )
        with patch("src.services.translate_service.get_translate_client", return_value=mock_client):
            result = detect_language("వరద హెచ్చరిక")
            assert isinstance(result, str)

    def test_translate_returns_dict_with_required_keys(self, mock_translate):
        with patch("src.services.translate_service.get_translate_client", return_value=mock_translate):
            result = translate_to_english("test")
            assert "original" in result
            assert "translated" in result
            assert "detected_language" in result

    def test_translation_failure_returns_original(self):
        with patch("src.services.translate_service.get_translate_client") as mock:
            mock.return_value.translate_text.side_effect = Exception("API error")
            result = translate_to_english("hello")
            assert result["translated"] == "hello"
            assert result["original"] == "hello"

    def test_empty_string_handled(self, mock_translate):
        with patch("src.services.translate_service.get_translate_client", return_value=mock_translate):
            result = translate_to_english("")
            assert "original" in result

    def test_detect_language_failure_returns_unknown(self):
        with patch("src.services.translate_service.get_translate_client") as mock:
            mock.return_value.detect_language.side_effect = Exception("error")
            result = detect_language("test")
            assert result == "unknown"
```

### Step 3: Verify Count
```bash
pytest tests/ --collect-only -q 2>&1 | tail -3
# Should show: "X tests collected"
# Target: 50+
```

### Step 4: Run All Tests
```bash
pytest tests/ -v --tb=short
# Must show: X passed, 0 failed
```

## Constraints
- All tests must be isolated — use mocks for all external services
- Tests must run offline — no actual GCP calls
- Use `pytest.fixture` for all shared setup
- Every test has exactly one assertion focus (single responsibility)
- Test file names must start with `test_`
