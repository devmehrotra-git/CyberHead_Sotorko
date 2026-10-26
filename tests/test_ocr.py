from types import SimpleNamespace

from app.schemas.analysis import InputLanguage, OCRStatus
from app.services import ocr


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


class FakeTesseract:
    Output = SimpleNamespace(DICT="dict")

    @staticmethod
    def get_languages(config: str = "") -> list[str]:
        return ["ben", "eng"]

    @staticmethod
    def image_to_data(image: FakeImage, *, lang: str, output_type: str, timeout: int) -> dict[str, list[str]]:
        assert lang == "eng+ben"
        return {"text": ["আপনার", "account"], "conf": ["92", "88"]}


def test_successful_ocr_extracts_mixed_script(monkeypatch) -> None:
    monkeypatch.setattr(ocr, "_load_dependencies", lambda: (FakeImageModule, FakeImageOps, FakeTesseract))

    response = ocr.extract_text(b"image-bytes", filename="message.png", content_type="image/png", language=InputLanguage.AUTO)

    assert response.status == OCRStatus.SUCCESS
    assert response.extracted_text == "আপনার account"
    assert response.detected_language == InputLanguage.BN
    assert response.ocr_confidence == 0.9


def test_prepare_image_upscales_small_screenshots() -> None:
    image = FakeImage()

    prepared = ocr._prepare_image(image, FakeImageOps)

    assert prepared.size == (640, 360)


def test_invalid_image_is_rejected_without_ocr(monkeypatch) -> None:
    monkeypatch.setattr(ocr, "_load_dependencies", lambda: (FakeImageModule, FakeImageOps, FakeTesseract))
    monkeypatch.setattr(FakeImageModule, "open", staticmethod(lambda stream: (_ for _ in ()).throw(ValueError("bad"))))

    response = ocr.extract_text(b"not-an-image", filename="message.png", content_type="image/png", language=InputLanguage.AUTO)

    assert response.status == OCRStatus.INVALID
    assert response.extracted_text == ""


def test_missing_ocr_dependencies_are_explicit(monkeypatch) -> None:
    monkeypatch.setattr(ocr, "_load_dependencies", lambda: None)

    response = ocr.extract_text(b"image-bytes", filename="message.png", content_type="image/png", language=InputLanguage.AUTO)

    assert response.status == OCRStatus.UNAVAILABLE
    assert "Tesseract" in response.message


def test_oversized_upload_is_rejected(monkeypatch) -> None:
    monkeypatch.setattr(ocr, "_load_dependencies", lambda: (FakeImageModule, FakeImageOps, FakeTesseract))

    response = ocr.extract_text(b"x" * (ocr.MAX_FILE_BYTES + 1), filename="message.png", content_type="image/png", language=InputLanguage.AUTO)

    assert response.status == OCRStatus.INVALID
    assert "too large" in response.message
