from pathlib import Path

from app.main import app


def test_frontend_assets_exist_and_reference_api() -> None:
    root = Path(__file__).resolve().parents[1]
    html = (root / "frontend/index.html").read_text(encoding="utf-8")
    javascript = (root / "frontend/app.js").read_text(encoding="utf-8")

    assert (root / "frontend/styles.css").is_file()
    assert '<html lang="bn">' in html
    assert 'lang="bn"' in html
    assert "/styles.css" in html
    assert "/app.js" in html
    assert "fonts.googleapis.com" not in html
    assert "#analyzer" in html
    assert "#how-it-works" in html
    assert "result-explanation" in html
    assert "screenshot-file" in html
    assert "ocr-text" in html
    assert 'fetch("/api/v1/analyze"' in javascript
    assert 'fetch("/api/v1/analyze/screenshot"' in javascript
    assert 'data-i18n="analyzeReviewed"' in html
    assert "isPlaceholder" in javascript
    assert 'response.verdict === "unsupported"' in javascript
    assert "response.status === 422" in javascript
    assert "TypeError" in javascript
    assert 'const isBengaliExperimental = response.analysis_mode === "bengali_experimental_rules"' in javascript
    assert 'const isEnglishExperimental = response.analysis_mode === "english_experimental_rules"' in javascript
    assert 'const isExperimentalRules = isBengaliExperimental || isEnglishExperimental' in javascript
    assert 'const isGenericLimited = !isExperimentalRules' in javascript
    assert 'else if (isGenericLimited)' in javascript
    assert 'languageSelector.value = "auto";' in javascript
    assert 'status === "unavailable"' in javascript
    assert 'status === "failed"' in javascript
    assert 'data-i18n="footer"' in html
    assert 'data-i18n="languageControl"' in html
    assert 'data-i18n="languageHint"' in html
    assert "Don't read Bengali? Switch to English." in html
    assert "Not an official government service" not in html
    assert "VBYLD 2027" not in html
    assert "fonts.googleapis.com" not in html
    assert "language-support-warning" in html
    assert "updateLanguageSupportWarning" in javascript
    assert "Bengali OCR works independently" in javascript
    assert "Banglish scam classification is not yet supported" in javascript
    assert 'languageSupportWarning.hidden = true;' in javascript
    assert 'setInterfaceLocale("bn")' in javascript
    assert 'setInterfaceLocale("en")' in javascript
    assert 'locale-bn' in html and 'locale-en' in html
    assert 'document.documentElement.lang = interfaceLocale;' in javascript
    assert 'language: languageSelector.value' in javascript
    assert 'document.querySelector(".brand").setAttribute("aria-label"' in javascript
    assert 'document.querySelector(".locale-switch").setAttribute("aria-label"' in javascript
    assert "languageHint" in javascript
    assert "localizedExplanation" in javascript
    assert "lastResponse" in javascript
    assert "resultExplanation.textContent = localizedExplanation(response);" in javascript
    assert "hasDirectMoneyTransferSignal" in javascript
    assert "financial-risk-warning" in html
    assert "separate from the ML verdict" in javascript
    assert "shared lunch" in javascript
    assert "paymentThreat" in javascript
    assert 'data.risk_score === null || typeof data.risk_score === "number"' in javascript
    assert "bengali_experimental_rules" in javascript
    assert "analysis-evidence" in html
    assert "safety-guidance" in html
    assert 'payload.language === "auto"' in javascript
    assert "applyDetectedLanguage(data.detected_language)" in javascript
    assert 'resultWarning.hidden = isExperimentalRules' in javascript
    bengali_branch = javascript.split('if (isBengaliExperimental || isEnglishExperimental)', 1)[1].split('else if (isGenericLimited)', 1)[0]
    assert "limitedSummary" not in bengali_branch
    assert 'response.verdict === "suspicious"' in bengali_branch
    assert 't("bengaliSuspicious")' in bengali_branch
    assert 't("bengaliInconclusive")' in bengali_branch
    assert 't("bengaliInconclusiveSummary")' in bengali_branch
    assert 'copy.en.bengaliInconclusiveSummary = "No known warning pattern matched this message. This does not prove it is safe."' in javascript
    assert 'copy.en.bengaliInconclusive = "No sufficient rule-based evidence was found"' in javascript
    assert 't("bengaliInconclusiveSummary")' in javascript
    assert "The experimental Bengali rules found insufficient evidence. This is not proof that the message is safe." not in javascript
    assert "safetyGuidance.hidden = !response.safety_guidance" in javascript
    assert "resultWarning.hidden = isExperimentalRules" in javascript
    assert "analysisEvidence.hidden" in bengali_branch or "analysisEvidence.hidden" in javascript
    assert "english_experimental_rules" in javascript
    assert "englishExperimental" in javascript


def test_frontend_mount_is_registered_after_api_routes() -> None:
    routes = list(app.routes)
    api_paths = [getattr(route, "path", "") for route in routes if getattr(route, "path", "").startswith("/api/")]
    mount_indices = [
        index
        for index, route in enumerate(routes)
        if getattr(route, "name", "") == "frontend" and getattr(route, "path", "") == ""
    ]

    assert api_paths
    assert mount_indices
    assert max(index for index, route in enumerate(routes) if getattr(route, "path", "").startswith("/api/")) < mount_indices[-1]
