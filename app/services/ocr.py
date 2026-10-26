"""Optional, non-persistent screenshot OCR service."""

from __future__ import annotations

import io
import logging
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.schemas.analysis import InputLanguage, OCRResponse, OCRStatus

logger = logging.getLogger(__name__)

MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_IMAGE_WIDTH = 6000
MAX_IMAGE_HEIGHT = 6000
MAX_IMAGE_PIXELS = 20_000_000
OCR_TIMEOUT_SECONDS = 20
OCR_PSM = 6
OCR_MIN_DIMENSION = 1400
ALLOWED_CONTENT_TYPES = {"image/png", "image/jpeg", "image/webp"}


@dataclass(frozen=True)
class OCRResult:
    text: str
    confidence: float | None
    languages: list[str]


def _unavailable(filename: str, message: str, languages: list[str] | None = None) -> OCRResponse:
    return OCRResponse(
        status=OCRStatus.UNAVAILABLE,
        filename=filename,
        message=message,
        available_languages=languages or [],
    )


def _detect_language(text: str) -> InputLanguage:
    if re.search(r"[\u0980-\u09ff]", text):
        return InputLanguage.BN
    if text.strip():
        return InputLanguage.EN
    return InputLanguage.AUTO


def _load_dependencies() -> tuple[Any, Any, Any] | None:
    try:
        from PIL import Image, ImageOps
        import pytesseract
    except ImportError:
        return None
    configured = os.getenv("SOTORKO_TESSERACT_CMD")
    if configured and Path(configured).is_file():
        pytesseract.pytesseract.tesseract_cmd = configured
    elif not shutil.which("tesseract") and not shutil.which("tesseract.exe"):
        for candidate in (
            Path("C:/Program Files/Tesseract-OCR/tesseract.exe"),
            Path("C:/Program Files (x86)/Tesseract-OCR/tesseract.exe"),
            Path(os.getenv("LOCALAPPDATA", "")) / "Programs/Tesseract-OCR/tesseract.exe",
        ):
            if candidate.is_file():
                pytesseract.pytesseract.tesseract_cmd = str(candidate)
                break
    return (Image, ImageOps, pytesseract)


def _available_languages(pytesseract: Any) -> list[str]:
    try:
        return sorted(str(value) for value in pytesseract.get_languages(config=""))
    except Exception:
        return []


def _validate_image(payload: bytes, content_type: str | None, image_module: Any) -> Any:
    if not payload:
        raise ValueError("The uploaded image is empty.")
    if len(payload) > MAX_FILE_BYTES:
        raise ValueError("The uploaded image is too large; the limit is 8 MB.")
    if content_type and content_type.lower() not in ALLOWED_CONTENT_TYPES:
        raise ValueError("Use a PNG, JPEG, or WebP screenshot.")
    try:
        image = image_module.open(io.BytesIO(payload))
        image.verify()
        image = image_module.open(io.BytesIO(payload))
        image.load()
    except Exception as exc:
        raise ValueError("The uploaded file is not a readable image.") from exc
    width, height = image.size
    if width < 1 or height < 1 or width > MAX_IMAGE_WIDTH or height > MAX_IMAGE_HEIGHT:
        raise ValueError("The image dimensions are outside the supported range.")
    if width * height > MAX_IMAGE_PIXELS:
        raise ValueError("The image contains too many pixels to process safely.")
    return image


def _prepare_image(image: Any, image_ops: Any) -> Any:
    """Prepare screenshots conservatively without changing the uploaded file."""
    prepared = image_ops.exif_transpose(image).convert("L")
    autocontrast = getattr(image_ops, "autocontrast", None)
    if callable(autocontrast):
        prepared = autocontrast(prepared)
    width, height = getattr(prepared, "size", (0, 0))
    resize = getattr(prepared, "resize", None)
    if callable(resize) and max(width, height) < OCR_MIN_DIMENSION and width > 0 and height > 0:
        scale = 2
        prepared = resize((width * scale, height * scale))
    return prepared


def _run_tesseract(image: Any, requested_language: InputLanguage, image_ops: Any, pytesseract: Any) -> OCRResult:
    languages = _available_languages(pytesseract)
    if "eng" not in languages:
        raise RuntimeError("Tesseract is installed but its English language data is unavailable.")
    if requested_language == InputLanguage.BN and "ben" not in languages:
        raise RuntimeError("Bengali OCR language data (ben) is unavailable.")
    if requested_language == InputLanguage.EN:
        language_config = "eng"
    elif requested_language == InputLanguage.BN:
        language_config = "ben"
    else:
        language_config = "eng+ben" if "ben" in languages else "eng"

    prepared = _prepare_image(image, image_ops)
    try:
        data = pytesseract.image_to_data(
            prepared,
            lang=language_config,
            config=f"--psm {OCR_PSM}",
            output_type=pytesseract.Output.DICT,
            timeout=OCR_TIMEOUT_SECONDS,
        )
    except TypeError:
        # Keep compatibility with small test doubles and older pytesseract wrappers.
        data = pytesseract.image_to_data(
            prepared,
            lang=language_config,
            output_type=pytesseract.Output.DICT,
            timeout=OCR_TIMEOUT_SECONDS,
        )
    words: list[str] = []
    confidences: list[float] = []
    for text, raw_conf in zip(data.get("text", []), data.get("conf", [])):
        value = str(text).strip()
        if not value:
            continue
        words.append(value)
        try:
            confidence = float(raw_conf)
        except (TypeError, ValueError):
            continue
        if confidence >= 0:
            confidences.append(confidence / 100.0)
    extracted = " ".join(words).strip()
    confidence = sum(confidences) / len(confidences) if confidences else None
    return OCRResult(text=extracted, confidence=confidence, languages=languages)


def extract_text(payload: bytes, *, filename: str, content_type: str | None, language: InputLanguage) -> OCRResponse:
    """Extract text without writing the uploaded image to disk."""
    dependencies = _load_dependencies()
    if dependencies is None:
        return _unavailable(
            filename,
            "OCR is unavailable. Install Tesseract with English and Bengali language data, then install the Python OCR dependencies.",
        )
    image_module, image_ops, pytesseract = dependencies
    try:
        image = _validate_image(payload, content_type, image_module)
    except ValueError as exc:
        return OCRResponse(status=OCRStatus.INVALID, filename=filename, message=str(exc))

    languages = _available_languages(pytesseract)
    try:
        result = _run_tesseract(image, language, image_ops, pytesseract)
    except RuntimeError as exc:
        return _unavailable(filename, str(exc), languages)
    except Exception as exc:
        logger.exception("OCR extraction failed for %s: %s", filename, exc)
        return OCRResponse(status=OCRStatus.FAILED, filename=filename, message="OCR could not process this image.", available_languages=languages)

    if not result.text:
        return OCRResponse(
            status=OCRStatus.EMPTY,
            filename=filename,
            message="No readable text was found. Try a clearer screenshot.",
            available_languages=result.languages,
        )
    return OCRResponse(
        status=OCRStatus.SUCCESS,
        filename=filename,
        extracted_text=result.text,
        detected_language=_detect_language(result.text),
        ocr_confidence=result.confidence,
        message="Text extracted. Review it carefully before analysis.",
        available_languages=result.languages,
    )
