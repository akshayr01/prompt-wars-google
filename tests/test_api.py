"""Tests for API endpoints — 14 tests."""

import pytest


class TestHealthEndpoint:
    """Tests for GET /health."""

    def test_health_returns_200(self, client):
        """Health endpoint should return 200 OK."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_has_status_ok(self, client):
        """Health response should have status 'ok'."""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "ok"

    def test_health_lists_google_services(self, client):
        """Health response should list Google services used."""
        response = client.get("/health")
        data = response.json()
        assert "google_services" in data
        assert len(data["google_services"]) >= 2
        assert "Gemini 1.5 Flash" in data["google_services"]


class TestAnalyzeEndpoint:
    """Tests for POST /analyze."""

    def test_analyze_valid_input_returns_200(self, client, sample_medical):
        """Valid emergency input should return 200."""
        response = client.post("/analyze", json={"input": sample_medical})
        assert response.status_code == 200

    def test_analyze_response_has_situation(self, client, sample_medical):
        """Response should contain situation field."""
        response = client.post("/analyze", json={"input": sample_medical})
        data = response.json()
        assert "situation" in data
        assert len(data["situation"]) > 0

    def test_analyze_response_has_category(self, client, sample_medical):
        """Response should contain a valid category."""
        response = client.post("/analyze", json={"input": sample_medical})
        data = response.json()
        assert data["category"] in ["medical", "accident", "disaster", "fire", "crime", "civic", "other"]

    def test_analyze_response_has_actions_list(self, client, sample_medical):
        """Response should contain a non-empty actions list."""
        response = client.post("/analyze", json={"input": sample_medical})
        data = response.json()
        assert isinstance(data["actions"], list)
        assert len(data["actions"]) > 0

    def test_analyze_response_has_contacts_list(self, client, sample_medical):
        """Response should contain a contacts list."""
        response = client.post("/analyze", json={"input": sample_medical})
        data = response.json()
        assert isinstance(data["contacts"], list)
        assert len(data["contacts"]) > 0

    def test_analyze_empty_string_returns_422(self, client):
        """Empty string input should return validation error."""
        response = client.post("/analyze", json={"input": ""})
        assert response.status_code == 422

    def test_analyze_whitespace_only_returns_422(self, client):
        """Whitespace-only input should return validation error."""
        response = client.post("/analyze", json={"input": "   \n\t  "})
        assert response.status_code == 422

    def test_analyze_missing_input_field_returns_422(self, client):
        """Missing input field should return 422."""
        response = client.post("/analyze", json={})
        assert response.status_code == 422

    def test_analyze_null_input_returns_422(self, client):
        """Null input should return 422."""
        response = client.post("/analyze", json={"input": None})
        assert response.status_code == 422

    def test_analyze_input_too_long_returns_422(self, client):
        """Input exceeding 5000 chars should return validation error."""
        long_input = "a" * 5001
        response = client.post("/analyze", json={"input": long_input})
        assert response.status_code == 422

    def test_analyze_unicode_input_returns_200(self, client, sample_hindi):
        """Unicode/Hindi input should be accepted and return 200."""
        response = client.post("/analyze", json={"input": sample_hindi})
        assert response.status_code == 200
