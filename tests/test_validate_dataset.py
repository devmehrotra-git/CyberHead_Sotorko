"""Tests for the dataset validation tooling."""

import json
from pathlib import Path

from ml.validate_dataset import load_dataset, main, summarize_records, validate_records


SAMPLE_PATH = Path("data/samples/sample_messages.json")


def test_sample_dataset_is_valid() -> None:
    records = load_dataset(SAMPLE_PATH)

    assert validate_records(records) == []
    assert summarize_records(records)["label"] == {"genuine": 4, "scam": 4}
    assert set(summarize_records(records)["scam_category"]) == {
        "banking_payment",
        "employment_financial_opportunity",
        "identity_account",
        "none",
    }


def test_validator_rejects_duplicate_ids_and_invalid_red_flags() -> None:
    records = [
        {
            "record_id": "duplicate",
            "content": "Example",
            "language": "en",
            "script": "latin",
            "label": "genuine",
            "scam_category": "none",
            "red_flags": ["not_a_real_flag"],
            "source_type": "synthetic_example",
            "source_reference": "test fixture",
            "is_example": True,
            "split": None,
        },
        {
            "record_id": "duplicate",
            "content": "Another example",
            "language": "en",
            "script": "latin",
            "label": "scam",
            "scam_category": "none",
            "red_flags": [],
            "source_type": "synthetic_example",
            "source_reference": "test fixture",
            "is_example": True,
            "split": None,
        },
    ]

    errors = validate_records(records)

    assert any("duplicate record_id" in error for error in errors)
    assert any("invalid red_flag" in error for error in errors)
    assert any("scam records must have" in error for error in errors)


def test_validator_rejects_pattern_names_as_categories() -> None:
    record = {
        "record_id": "legacy-category",
        "content": "Example",
        "language": "en",
        "script": "latin",
        "label": "scam",
        "scam_category": "phishing",
        "red_flags": [],
        "source_type": "synthetic_example",
        "source_reference": "test fixture",
        "is_example": True,
        "split": None,
    }

    errors = validate_records([record])

    assert any("invalid scam_category" in error for error in errors)


def test_validator_cli_returns_nonzero_for_invalid_json(tmp_path: Path, capsys) -> None:
    dataset_path = tmp_path / "invalid.json"
    dataset_path.write_text(json.dumps([{"record_id": "missing-fields"}]), encoding="utf-8")

    exit_code = main([str(dataset_path)])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "validation: failed" in captured.out
