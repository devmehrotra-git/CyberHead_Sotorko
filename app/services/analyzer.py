"""Cached inference service for the limited Sotorko prototype model."""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib

from app.schemas.analysis import (
    AnalysisRequest,
    AnalysisResponse,
    AnalysisStatus,
    InputLanguage,
    ReportingGuidance,
    ScamCategory,
    Verdict,
)
from app.services.english_safety import detect as detect_english_safety

logger = logging.getLogger(__name__)
DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[2] / "data" / "derived" / "ml_baseline" / "tfidf_logistic_regression.joblib"
MODEL_PATH = Path(os.getenv("SOTORKO_MODEL_PATH", str(DEFAULT_MODEL_PATH)))
SUPPORTED_LANGUAGE = InputLanguage.EN


def _model_path() -> Path:
    """Resolve the configured artifact without depending on the process cwd."""
    configured = Path(MODEL_PATH).expanduser()
    if configured.is_file():
        return configured
    if not configured.is_absolute():
        rooted = Path(__file__).resolve().parents[2] / configured
        if rooted.is_file():
            return rooted
    raise FileNotFoundError(f"Sotorko model artifact not found: {configured}")


@lru_cache(maxsize=1)
def load_model_bundle() -> dict[str, Any]:
    """Load the existing trained bundle once per process."""
    bundle = joblib.load(_model_path())
    if not isinstance(bundle, dict) or "features" not in bundle or "model" not in bundle:
        raise ValueError("model bundle is missing required components")
    model = bundle["model"]
    classes = {str(value) for value in getattr(model, "classes_", [])}
    if classes != {"genuine", "scam"} or not callable(getattr(model, "predict", None)):
        raise ValueError("model bundle does not expose the expected genuine/scam classifier")
    if not callable(getattr(model, "predict_proba", None)):
        raise ValueError("model bundle does not expose calibrated class probabilities")
    return bundle


def _response(
    *,
    request: AnalysisRequest,
    status: AnalysisStatus,
    verdict: Verdict,
    risk_score: float | None,
    detected_language: InputLanguage,
    explanation: str,
    analysis_mode: str = "limited",
    evidence: list[str] | None = None,
    safety_guidance: str = "",
    scam_category: ScamCategory | None = None,
    red_flags: list[Any] | None = None,
    recommended_actions: list[Any] | None = None,
) -> AnalysisResponse:
    output_language = request.language if request.language != InputLanguage.AUTO else detected_language
    return AnalysisResponse(
        status=status,
        verdict=verdict,
        risk_score=risk_score,
        detected_language=detected_language,
        output_language=output_language,
        scam_category=scam_category if scam_category is not None else (ScamCategory.NONE if status == AnalysisStatus.PREDICTED else None),
        red_flags=red_flags or [],
        explanation=explanation,
        recommended_actions=recommended_actions or [],
        reporting=ReportingGuidance(
            available=False,
            message="Reporting guidance is not implemented yet.",
        ),
        analysis_mode=analysis_mode,
        evidence=evidence or [],
        safety_guidance=safety_guidance,
    )


def _limited(
    request: AnalysisRequest,
    explanation: str,
    status: AnalysisStatus = AnalysisStatus.UNSUPPORTED,
) -> AnalysisResponse:
    detected = request.language if request.language != InputLanguage.AUTO else InputLanguage.AUTO
    return _response(
        request=request,
        status=status,
        verdict=Verdict.UNSUPPORTED,
        risk_score=None,
        detected_language=detected,
        explanation=explanation,
    )


def analysis_not_implemented(request: AnalysisRequest) -> AnalysisResponse:
    """Return the honest API scaffold state until analysis is exposed."""
    return _limited(
        request,
        "The analysis engine is not implemented yet. No classification was performed.",
    )


def analyze_text(request: AnalysisRequest) -> AnalysisResponse:
    """Analyze supported English text with the saved baseline bundle only."""
    if request.input_type.value != "text":
        return _limited(
            request,
            "URL analysis is not supported by the current text-message model. No URL classification was performed.",
        )
    if request.language != SUPPORTED_LANGUAGE:
        return _limited(
            request,
            "The current model is validated only for English text. No reliable classification was performed for this language.",
        )

    try:
        bundle = load_model_bundle()
        transformed = bundle["features"].transform([request.content])
        model = bundle["model"]
        predicted = str(model.predict(transformed)[0])
        classes = list(model.classes_)
        probabilities = model.predict_proba(transformed)[0]
        scam_probability = float(probabilities[classes.index("scam")])
    except FileNotFoundError as exc:
        logger.warning("Sotorko model artifact unavailable: %s", exc)
        load_model_bundle.cache_clear()
        return _limited(
            request,
            "The English analysis model is unavailable. No reliable classification was performed.",
            AnalysisStatus.UNAVAILABLE,
        )
    except (ValueError, KeyError, TypeError) as exc:
        logger.warning("Sotorko model artifact is incompatible: %s", exc)
        load_model_bundle.cache_clear()
        return _limited(
            request,
            "The English analysis model is incompatible with this service. No reliable classification was performed.",
            AnalysisStatus.UNAVAILABLE,
        )
    except Exception as exc:
        logger.exception("Sotorko model inference unavailable: %s", exc)
        load_model_bundle.cache_clear()
        return _limited(
            request,
            "The English analysis model failed while processing this message. No reliable classification was performed.",
            AnalysisStatus.FAILED,
        )

    if predicted == "scam":
        verdict = Verdict.LIKELY_SCAM
        explanation = (
            "English baseline model prediction: likely scam. This probability is the model's estimated scam-class "
            "score, not a guarantee. Verify the sender independently and do not share secrets."
        )
    elif predicted == "genuine":
        verdict = Verdict.NO_OBVIOUS_RED_FLAGS
        explanation = "English baseline model prediction: no obvious red flags. This is not proof that the message is safe; verify the sender independently."
    else:
        return _limited(request, "The model returned an unsupported class. No reliable classification was performed.", AnalysisStatus.FAILED)

    safety_finding = detect_english_safety(request.content)
    if safety_finding:
        return _response(
            request=request,
            status=AnalysisStatus.PREDICTED,
            verdict=Verdict.SUSPICIOUS,
            risk_score=None,
            detected_language=SUPPORTED_LANGUAGE,
            explanation="Experimental English rule-based safety check: warning signals were found. This is not a guarantee or a trained override.",
            analysis_mode="english_experimental_rules",
            evidence=list(safety_finding.evidence),
            safety_guidance="Do not share OTPs, PINs, passwords, or money. Verify the sender through an independent official channel.",
            scam_category=safety_finding.category,
            red_flags=list(safety_finding.flags),
        )

    return _response(
        request=request,
        status=AnalysisStatus.PREDICTED,
        verdict=verdict,
        risk_score=scam_probability,
        detected_language=SUPPORTED_LANGUAGE,
        explanation=explanation,
        analysis_mode="english_ml",
        safety_guidance="Verify the sender independently; this model result is not a guarantee of safety or fraud.",
    )
