"""Tests for the source registry and normalized ingestion validation."""

from copy import deepcopy
from pathlib import Path

from scripts.data.validate_normalized_data import (
    load_source_registry,
    validate_records,
)


REGISTRY_PATH = Path("data/sources/source_registry.json")


def valid_record() -> dict[str, object]:
    return {
        "id": "normalized-001",
        "text": "Your account needs verification. Do not share your OTP.",
        "language": "en",
        "script": "latin",
        "label": "scam",
        "scam_category": "identity_account",
        "red_flags": ["request_for_otp"],
        "source_type": "public_report",
        "source_reference": "source report 001",
        "source_id": "uci_sms_spam_collection",
        "source_record_id": "uci-001",
        "original_label": "spam",
        "mapping_status": "mapped",
    }


def test_valid_normalized_message() -> None:
    assert validate_records([valid_record()]) == []


def test_invalid_scam_category() -> None:
    record = valid_record()
    record["scam_category"] = "phishing"

    errors = validate_records([record])

    assert any("invalid scam_category" in error for error in errors)


def test_invalid_language() -> None:
    record = valid_record()
    record["language"] = "fr"

    errors = validate_records([record])

    assert any("invalid language" in error for error in errors)


def test_missing_provenance() -> None:
    record = valid_record()
    del record["source_id"]
    del record["source_record_id"]

    errors = validate_records([record])

    assert any("missing required fields" in error for error in errors)
    assert sum("source_id" in error or "source_record_id" in error for error in errors) >= 2


def test_duplicate_normalized_id() -> None:
    first = valid_record()
    second = deepcopy(first)
    second["source_record_id"] = "uci-002"

    errors = validate_records([first, second])

    assert any("duplicate normalized id" in error for error in errors)


def test_inconsistent_scam_category() -> None:
    record = valid_record()
    record["label"] = "genuine"

    errors = validate_records([record])

    assert any("genuine records must have" in error for error in errors)


def test_valid_excluded_unmapped_record() -> None:
    record = valid_record()
    record.update(
        {
            "label": None,
            "scam_category": "none",
            "red_flags": [],
            "mapping_status": "excluded",
            "original_label": "spam",
        }
    )

    assert validate_records([record]) == []


def test_source_registry_loading() -> None:
    registry = load_source_registry(REGISTRY_PATH)

    assert len(registry) == 6
    hindi = next(entry for entry in registry if entry["source_id"] == "hindi_sms_pending_license")
    assert hindi["license_status"] == "pending_verification"
    assert hindi["redistribution_status"] == "local_use_pending_review"
