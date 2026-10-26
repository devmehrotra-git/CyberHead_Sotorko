"""Deterministic regression tests for the current API analysis contracts."""

from __future__ import annotations

import io
from types import SimpleNamespace

import pytest
from fastapi import UploadFile

from app.api.v1.analyze import analyze_content, analyze_screenshot
from app.main import app
from app.schemas.analysis import AnalysisRequest, AnalysisStatus, InputLanguage, OCRStatus
from app.services import analyzer, ocr


class FakeFeatures:
    def transform(self, texts: list[str]) -> list[str]:
        return texts


class FakeModel:
    classes_ = ["genuine", "scam"]

    def __init__(self, predicted: str, probabilities: list[float]) -> None:
        self.predicted = predicted
        self.probabilities = probabilities

    def predict(self, transformed: list[str]) -> list[str]:
        return [self.predicted]

    def predict_proba(self, transformed: list[str]) -> list[list[float]]:
        return [self.probabilities]


def request(language: InputLanguage = InputLanguage.EN) -> AnalysisRequest:
    return AnalysisRequest(
        input_type="text",
        content="A deterministic contract-test message.",
        language=language,
        incident_status="unknown",
    )


class FakeImage:
    size = (320, 180)

    def verify(self) -> None:
        return None

    def load(self) -> None:
        return None

    def convert(self, mode: str) -> "FakeImage":
        return self

    def resize(self, size: tuple[int, int]) -> "FakeImage":
        self.size = size
        return self


class FakeImageModule:
    @staticmethod
    def open(stream: object) -> FakeImage:
        return FakeImage()


class FakeImageOps:
    @staticmethod
    def exif_transpose(image: FakeImage) -> FakeImage:
        return image

    @staticmethod
    def autocontrast(image: FakeImage) -> FakeImage:
        return image


class SuccessfulTesseract:
    Output = SimpleNamespace(DICT="dict")

    @staticmethod
    def get_languages(config: str = "") -> list[str]:
        return ["ben", "eng"]

    @staticmethod
    def image_to_data(
        image: FakeImage,
        *,
        lang: str,
        output_type: str,
        timeout: int,
    ) -> dict[str, list[str]]:
        assert lang == "ben"
        return {"text": ["আপনার", "অ্যাকাউন্ট"], "conf": ["92", "88"]}


def upload(filename: str = "message.png", content_type: str = "image/png", payload: bytes = b"image") -> UploadFile:
    return UploadFile(file=io.BytesIO(payload), filename=filename, headers={"content-type": content_type})


def test_analyze_route_uses_the_real_english_analyzer() -> None:
    response = analyze_content(request())

    assert response.status == AnalysisStatus.PREDICTED
    assert response.verdict.value in {"no_obvious_red_flags", "likely_scam"}
    assert response.risk_score is not None
    assert 0.0 <= response.risk_score <= 1.0
    assert response.red_flags == []
    assert "English baseline model prediction" in response.explanation


def test_analyze_route_does_not_return_a_placeholder() -> None:
    response = analyze_content(request())

    assert response.status != AnalysisStatus.UNSUPPORTED
    assert response.verdict.value != "unsupported"
    assert response.risk_score is not None


def test_unsupported_languages_never_load_or_fabricate_model(monkeypatch: pytest.MonkeyPatch) -> None:
    def model_must_not_load() -> dict[str, object]:
        raise AssertionError("unsupported language attempted model loading")

    monkeypatch.setattr(analyzer, "load_model_bundle", model_must_not_load)

    for language in (InputLanguage.BN, InputLanguage.BANGLISH, InputLanguage.HI):
        response = analyze_content(request(language))

        assert response.status == AnalysisStatus.UNSUPPORTED
        assert response.verdict.value == "unsupported"
        assert response.risk_score is None
        assert response.red_flags == []
        assert response.scam_category is None

    response = analyze_content(
        AnalysisRequest(input_type="text", content="xylophone qzv 123", language=InputLanguage.AUTO, incident_status="unknown")
    )
    assert response.status == AnalysisStatus.UNSUPPORTED
    assert response.verdict.value == "unsupported"
    assert response.risk_score is None


def test_model_unavailable_is_explicit_and_non_predictive(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(analyzer, "MODEL_PATH", analyzer.Path("E:/Sotorko-model-does-not-exist.joblib"))
    analyzer.load_model_bundle.cache_clear()

    response = analyzer.analyze_text(request())

    assert response.status == AnalysisStatus.UNAVAILABLE
    assert response.verdict.value == "unsupported"
    assert response.risk_score is None
    assert response.red_flags == []
    assert "unavailable" in response.explanation.lower()


def test_successful_bengali_ocr_does_not_imply_bengali_classification(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ocr, "_load_dependencies", lambda: (FakeImageModule, FakeImageOps, SuccessfulTesseract))

    ocr_response = analyze_screenshot(upload(), InputLanguage.BN)
    classification_response = analyze_content(
        AnalysisRequest(
            input_type="text",
            content=ocr_response.extracted_text,
            language=ocr_response.detected_language,
            incident_status="unknown",
        )
    )

    assert ocr_response.status == OCRStatus.SUCCESS
    assert ocr_response.detected_language == InputLanguage.BN
    assert classification_response.status == AnalysisStatus.UNSUPPORTED
    assert classification_response.verdict.value == "unsupported"
    assert classification_response.risk_score is None


def test_bengali_route_exposes_experimental_signal_without_score() -> None:
    response = analyze_content(
        AnalysisRequest(
            input_type="text",
            content="অভিনন্দন! লটারিতে পুরস্কার জিতেছেন। পুরস্কার পেতে ৫০০ টাকা ফি দিন।",
            language=InputLanguage.BN,
            incident_status="unknown",
        )
    )

    assert response.analysis_mode == "bengali_experimental_rules"
    assert response.status == AnalysisStatus.PREDICTED
    assert response.verdict.value == "suspicious"
    assert response.risk_score is None
    assert response.evidence


def test_auto_language_routes_meaningful_bengali_script_to_experimental_detector() -> None:
    response = analyze_content(
        AnalysisRequest(
            input_type="text",
            content="আপনার OTP দিন, না হলে অ্যাকাউন্ট বন্ধ হবে।",
            language=InputLanguage.AUTO,
            incident_status="unknown",
        )
    )

    assert response.detected_language == InputLanguage.BN
    assert response.analysis_mode == "bengali_experimental_rules"
    assert response.verdict.value == "suspicious"
    assert response.risk_score is None


def test_auto_english_uses_existing_ml_path() -> None:
    response = analyze_content(request(InputLanguage.AUTO))

    assert response.detected_language == InputLanguage.EN
    assert response.analysis_mode == "english_ml"
    assert response.status == AnalysisStatus.PREDICTED
    assert response.risk_score is not None


def test_auto_banglish_and_hindi_remain_unsupported() -> None:
    for content in ("Apnar OTP din, account bondho hobe", "आपका खाता बंद होगा, OTP दें"):
        response = analyze_content(
            AnalysisRequest(input_type="text", content=content, language=InputLanguage.AUTO, incident_status="unknown")
        )

        assert response.status == AnalysisStatus.UNSUPPORTED
        assert response.verdict.value == "unsupported"
        assert response.risk_score is None


def test_auto_url_never_routes_to_bengali_detector() -> None:
    response = analyze_content(
        AnalysisRequest(input_type="url", content="https://example.com/বাংলা", language=InputLanguage.AUTO, incident_status="unknown")
    )

    assert response.status == AnalysisStatus.UNSUPPORTED
    assert response.verdict.value == "unsupported"
    assert response.risk_score is None


def test_invalid_screenshot_upload_uses_existing_validation_contract(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ocr, "_load_dependencies", lambda: (FakeImageModule, FakeImageOps, SuccessfulTesseract))

    response = analyze_screenshot(upload(content_type="text/plain"), InputLanguage.AUTO)

    assert response.status == OCRStatus.INVALID
    assert response.extracted_text == ""
    assert "PNG" in response.message


def test_ocr_failure_returns_no_classification_signal(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ocr, "_load_dependencies", lambda: (FakeImageModule, FakeImageOps, SuccessfulTesseract))
    monkeypatch.setattr(ocr, "_run_tesseract", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("OCR failed")))

    response = analyze_screenshot(upload(), InputLanguage.AUTO)

    assert response.status == OCRStatus.UNAVAILABLE
    assert response.extracted_text == ""
    assert not hasattr(response, "verdict")


def test_api_paths_and_response_fields_remain_versioned() -> None:
    # FastAPI versions may represent included routers differently in app.routes.
    # OpenAPI is the stable public contract for the versioned endpoints.
    paths = set(app.openapi()["paths"])
    assert {"/api/v1/health", "/api/v1/analyze", "/api/v1/analyze/screenshot"}.issubset(paths)

