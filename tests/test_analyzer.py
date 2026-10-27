from pathlib import Path

import pytest

from app.schemas.analysis import AnalysisRequest
from app.services import analyzer, bengali


def request(*, language: str = "en", input_type: str = "text") -> AnalysisRequest:
    return AnalysisRequest(
        input_type=input_type,
        content="Congratulations, your account won a prize. Call now to claim it.",
        language=language,
        incident_status="unknown",
    )


def test_saved_bundle_has_explicit_classes_and_probability_support() -> None:
    bundle = analyzer.load_model_bundle()

    assert set(bundle["model"].classes_) == {"genuine", "scam"}
    assert callable(bundle["model"].predict_proba)
    assert bundle["features"].transform(["a message"]).shape[0] == 1


def test_english_inference_is_deterministic_and_bounded() -> None:
    analyzer.load_model_bundle.cache_clear()

    first = analyzer.analyze_text(request())
    second = analyzer.analyze_text(request())

    assert first == second
    assert first.status.value == "predicted"
    assert first.verdict.value in {"no_obvious_red_flags", "likely_scam"}
    assert 0.0 <= first.risk_score <= 1.0
    assert first.scam_category.value == "none"
    assert first.red_flags == []
    assert "English baseline model prediction" in first.explanation


def test_paired_money_request_counterfactual_is_reproducible() -> None:
    first = AnalysisRequest(input_type="text", content="This is not a scam. Send me 100000 rupees only.", language="en", incident_status="unknown")
    second = AnalysisRequest(input_type="text", content="This is a scam. Send me 100000 rupees only.", language="en", incident_status="unknown")

    first_response = analyzer.analyze_text(first)
    second_response = analyzer.analyze_text(second)

    assert first_response.verdict.value == "no_obvious_red_flags"
    assert second_response.verdict.value == "no_obvious_red_flags"
    assert first_response.risk_score == pytest.approx(0.1410908005, abs=1e-9)
    assert second_response.risk_score == pytest.approx(0.1949762340, abs=1e-9)
    assert second_response.risk_score > first_response.risk_score


def test_unvalidated_languages_are_explicitly_unsupported() -> None:
    for language in ("bn", "banglish", "hi", "auto"):
        response = analyzer.analyze_text(request(language=language))

        assert response.verdict.value == "unsupported"
        assert response.status.value == "unsupported"
        assert response.risk_score is None
        assert "reliable" in response.explanation


def test_url_input_is_not_sent_to_message_model() -> None:
    response = analyzer.analyze_text(request(input_type="url"))

    assert response.verdict.value == "unsupported"
    assert response.status.value == "unsupported"
    assert response.risk_score is None
    assert "URL analysis" in response.explanation


def test_missing_bundle_returns_limited_response(monkeypatch) -> None:
    missing = Path("E:/Sotorko-model-does-not-exist.joblib")
    monkeypatch.setattr(analyzer, "MODEL_PATH", missing)
    analyzer.load_model_bundle.cache_clear()

    response = analyzer.analyze_text(request())

    assert response.verdict.value == "unsupported"
    assert response.status.value == "unavailable"
    assert response.risk_score is None
    assert "model is unavailable" in response.explanation
    analyzer.load_model_bundle.cache_clear()


def test_bengali_otp_request_is_experimental_and_evidenced() -> None:
    response = bengali.analyze(request(language="bn"))

    assert response.status.value == "unsupported"
    assert response.verdict.value == "unsupported"
    assert response.risk_score is None


def test_bengali_otp_request_is_flagged() -> None:
    response = bengali.analyze(AnalysisRequest(input_type="text", content="আপনার OTP দিন, না হলে অ্যাকাউন্ট বন্ধ হবে।", language="bn", incident_status="unknown"))

    assert response.analysis_mode == "bengali_experimental_rules"
    assert response.verdict.value == "suspicious"
    assert response.risk_score is None
    assert "otp_request" in {flag.value for flag in response.red_flags}
    assert response.evidence
    assert "OTP দেওয়ার অনুরোধ রয়েছে।" in response.evidence
    assert "অ্যাকাউন্ট বন্ধ হওয়ার হুমকি রয়েছে।" in response.evidence


def test_bengali_urgent_link_is_flagged() -> None:
    response = bengali.analyze(AnalysisRequest(input_type="text", content="জরুরি! আপনার ব্যাংক অ্যাকাউন্ট বন্ধ হবে, এখনই লিংকে লগইন করুন: https://example.test", language="bn", incident_status="unknown"))

    assert response.verdict.value == "suspicious"
    assert "suspicious_url" in {flag.value for flag in response.red_flags}


def test_bengali_prize_fee_is_flagged() -> None:
    response = bengali.analyze(AnalysisRequest(input_type="text", content="অভিনন্দন! আপনি লটারিতে পুরস্কার জিতেছেন। পুরস্কার পেতে ৫০০ টাকা ফি দিন।", language="bn", incident_status="unknown"))

    assert response.verdict.value == "suspicious"
    assert response.scam_category.value == "banking_payment"


def test_bengali_job_registration_fee_is_flagged() -> None:
    response = bengali.analyze(AnalysisRequest(input_type="text", content="ঘরে বসে চাকরি! রেজিস্ট্রেশনের জন্য অগ্রিম ১০০০ টাকা পেমেন্ট করুন।", language="bn", incident_status="unknown"))

    assert response.verdict.value == "suspicious"
    assert response.scam_category.value == "employment_financial_opportunity"


def test_bengali_benign_and_protective_messages_are_not_called_safe() -> None:
    benign = bengali.analyze(AnalysisRequest(input_type="text", content="আজ বিকেলে বাসায় আসবেন? চা খাব।", language="bn", incident_status="unknown"))
    protective = bengali.analyze(AnalysisRequest(input_type="text", content="আপনার OTP কাউকে দেবেন না।", language="bn", incident_status="unknown"))

    assert benign.verdict.value == "unsupported"
    assert protective.verdict.value == "unsupported"
    assert benign.risk_score is None
    assert protective.risk_score is None


def test_english_safety_rule_overrides_false_negative_without_a_score() -> None:
    response = analyzer.analyze_text(AnalysisRequest(input_type="text", content="Send your your OTP now! Money deducts soon!", language="en", incident_status="unknown"))

    assert response.analysis_mode == "english_experimental_rules"
    assert response.verdict.value == "suspicious"
    assert response.risk_score is None
    assert any("authentication code" in item for item in response.evidence)
    assert any("financial/account threat" in item for item in response.evidence)


def test_otp_threat_does_not_claim_a_payment_request() -> None:
    response = analyzer.analyze_text(AnalysisRequest(input_type="text", content="Your bank account will be blocked today. Send your OTP immediately using this link.", language="en", incident_status="unknown"))

    assert response.verdict.value == "suspicious"
    assert "payment_request" not in {flag.value for flag in response.red_flags}
    assert not any("payment request" in item.lower() for item in response.evidence)


def test_explicit_money_demand_retains_payment_evidence() -> None:
    response = analyzer.analyze_text(AnalysisRequest(input_type="text", content="Your account will be blocked unless you pay 500 rupees immediately.", language="en", incident_status="unknown"))

    assert response.verdict.value == "suspicious"
    assert "payment_request" in {flag.value for flag in response.red_flags}
    assert any("payment request" in item.lower() for item in response.evidence)


def test_english_credential_request_is_flagged_but_protective_advice_is_not() -> None:
    request_message = analyzer.analyze_text(AnalysisRequest(input_type="text", content="Please send your OTP to confirm the payment.", language="en", incident_status="unknown"))
    protective = analyzer.analyze_text(AnalysisRequest(input_type="text", content="Never share your OTP with anyone.", language="en", incident_status="unknown"))
    arrival = analyzer.analyze_text(AnalysisRequest(input_type="text", content="Your OTP will arrive shortly.", language="en", incident_status="unknown"))

    assert request_message.analysis_mode == "english_experimental_rules"
    assert request_message.verdict.value == "suspicious"
    assert protective.analysis_mode == "english_ml"
    assert arrival.analysis_mode == "english_ml"


def test_english_baseline_behavior_is_preserved_without_rule_match() -> None:
    response = analyzer.analyze_text(AnalysisRequest(input_type="text", content="Your monthly electricity bill is due tomorrow.", language="en", incident_status="unknown"))

    assert response.analysis_mode == "english_ml"
    assert response.risk_score is not None
    assert response.verdict.value in {"no_obvious_red_flags", "likely_scam"}

