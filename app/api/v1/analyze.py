"""Analysis endpoint scaffolds."""

from fastapi import APIRouter, File, Form, UploadFile

from app.schemas.analysis import (
    AnalysisRequest,
    AnalysisResponse,
    InputLanguage,
    InputType,
    OCRResponse,
)
from app.services import analyzer
from app.services.bengali import analyze as analyze_bengali
from app.services.language import has_meaningful_bengali_script, is_probably_english
from app.services.ocr import MAX_FILE_BYTES, extract_text

router = APIRouter(tags=["analysis"])


@router.post("/analyze", response_model=AnalysisResponse)
def analyze_content(request: AnalysisRequest) -> AnalysisResponse:
    """Run the validated analyzer, preserving explicit limited states."""
    if request.input_type == InputType.TEXT and request.language == InputLanguage.AUTO and has_meaningful_bengali_script(request.content):
        return analyze_bengali(request.model_copy(update={"language": InputLanguage.BN}))
    if request.input_type == InputType.TEXT and request.language == InputLanguage.AUTO and is_probably_english(request.content):
        return analyzer.analyze_text(request.model_copy(update={"language": InputLanguage.EN}))
    if request.language == InputLanguage.BN:
        return analyze_bengali(request)
    return analyzer.analyze_text(request)


@router.post("/analyze/screenshot", response_model=OCRResponse)
def analyze_screenshot(
    file: UploadFile = File(...),
    language: InputLanguage = Form(InputLanguage.AUTO),
) -> OCRResponse:
    """Extract screenshot text when the optional local OCR engine is available."""
    payload = file.file.read(MAX_FILE_BYTES + 1)
    return extract_text(
        payload,
        filename=file.filename or "unnamed",
        content_type=file.content_type,
        language=language,
    )
