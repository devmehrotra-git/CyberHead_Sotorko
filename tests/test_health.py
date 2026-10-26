"""API contract tests for the Sotorko prototype."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_valid_analyze_request() -> None:
    response = client.post(
        "/api/v1/analyze",
        json={
            "input_type": "text",
            "content": "Please review this message.",
            "language": "en",
            "incident_status": "unknown",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "predicted"
    assert body["verdict"] in {"no_obvious_red_flags", "likely_scam"}
    assert isinstance(body["risk_score"], (int, float))
    assert 0.0 <= body["risk_score"] <= 1.0
    assert "English baseline model prediction" in body["explanation"]


def test_invalid_input_type() -> None:
    response = client.post(
        "/api/v1/analyze",
        json={
            "input_type": "image",
            "content": "content",
            "language": "en",
            "incident_status": "unknown",
        },
    )

    assert response.status_code == 422


def test_empty_content() -> None:
    response = client.post(
        "/api/v1/analyze",
        json={
            "input_type": "text",
            "content": "",
            "language": "en",
            "incident_status": "unknown",
        },
    )

    assert response.status_code == 422


def test_invalid_language() -> None:
    response = client.post(
        "/api/v1/analyze",
        json={
            "input_type": "text",
            "content": "content",
            "language": "fr",
            "incident_status": "unknown",
        },
    )

    assert response.status_code == 422


def test_unsupported_bengali_request_is_explicit() -> None:
    response = client.post(
        "/api/v1/analyze",
        json={
            "input_type": "text",
            "content": "আপনার অ্যাকাউন্ট যাচাই করুন",
            "language": "bn",
            "incident_status": "unknown",
        },
    )

    assert response.status_code == 200
    assert response.json()["verdict"] == "unsupported"
    assert "reliable" in response.json()["explanation"]


def test_url_request_is_explicitly_unsupported() -> None:
    response = client.post(
        "/api/v1/analyze",
        json={
            "input_type": "url",
            "content": "https://example.com",
            "language": "en",
            "incident_status": "unknown",
        },
    )

    assert response.status_code == 200
    assert response.json()["verdict"] == "unsupported"
    assert "URL analysis" in response.json()["explanation"]


def test_screenshot_endpoint_reports_real_ocr_state() -> None:
    response = client.post(
        "/api/v1/analyze/screenshot",
        files={"file": ("message.png", b"placeholder", "image/png")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] in {"unavailable", "invalid", "failed", "empty", "success"}
    assert "filename" in body
    assert "extracted_text" in body
