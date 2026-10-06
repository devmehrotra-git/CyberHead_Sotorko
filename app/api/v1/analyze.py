"""Analysis endpoint scaffolds."""

from fastapi import APIRouter, File, UploadFile

from app.schemas.analysis import (
    AnalysisRequest,
    AnalysisResponse,
    InputLanguage,
    RecommendedAction,
    RedFlag,
    ScamCategory,
    Verdict,
)

router = APIRouter(tags=["analysis"])


@router.post("/analyze", response_model=AnalysisResponse)
def analyze_content(request: AnalysisRequest) -> AnalysisResponse:
    """Return the contract-shaped placeholder until analysis is implemented."""
    output_language = (
        InputLanguage.EN
        if request.language == InputLanguage.AUTO
        else request.language
    )
    return AnalysisResponse(
        verdict=Verdict.NO_OBVIOUS_RED_FLAGS,
        risk_score=0.0,
        detected_language=InputLanguage.AUTO,
        output_language=output_language,
        scam_category=ScamCategory.NOT_IMPLEMENTED,
        red_flags=[RedFlag.NOT_IMPLEMENTED],
        explanation="The Sotorko analysis engine is not implemented yet.",
        recommended_actions=[RecommendedAction.NOT_IMPLEMENTED],
        reporting={
            "available": False,
            "message": "Reporting guidance is not implemented yet.",
        },
    )


@router.post("/analyze/screenshot")
def analyze_screenshot(file: UploadFile = File(...)) -> dict[str, str]:
    """Accept an image upload and report that OCR is not implemented."""
    return {
        "status": "not_implemented",
        "message": "OCR is not implemented yet.",
        "filename": file.filename or "unnamed",
    }
