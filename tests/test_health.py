"""API contract tests for the initial scaffold."""

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
    assert response.json()["verdict"] == "no_obvious_red_flags"
    assert response.json()["risk_score"] == 0.0


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


def test_screenshot_endpoint_scaffold() -> None:
    response = client.post(
        "/api/v1/analyze/screenshot",
        files={"file": ("message.png", b"placeholder", "image/png")},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "not_implemented"
    assert response.json()["message"] == "OCR is not implemented yet."
