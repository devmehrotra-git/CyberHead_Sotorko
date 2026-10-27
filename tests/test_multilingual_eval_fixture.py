import json
from collections import Counter
from pathlib import Path

from scripts.evaluate_multilingual import LANGUAGES, LABELS, load_cases


def test_multilingual_fixture_is_synthetic_balanced_and_unique() -> None:
    cases = load_cases()
    assert len(cases) == 32
    assert {case["language"] for case in cases} == LANGUAGES
    assert {case["label"] for case in cases} == LABELS
    counts = Counter((case["language"], case["label"]) for case in cases)
    assert all(counts[(language, label)] == 4 for language in LANGUAGES for label in LABELS)
    assert all(case["synthetic"] is True for case in cases)
    assert len({case["record_id"] for case in cases}) == len(cases)


def test_multilingual_fixture_content_is_nonempty_utf8_json() -> None:
    path = Path(__file__).parent / "fixtures" / "multilingual_smoke_cases.json"
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert all(case["content"].strip() for case in loaded)
    assert all(case["source_reference"] if "source_reference" in case else True for case in loaded)
