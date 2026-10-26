"""Validate Sotorko JSON dataset records against the documented schema."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

REQUIRED_FIELDS = {
    "record_id",
    "content",
    "language",
    "script",
    "label",
    "scam_category",
    "red_flags",
    "source_type",
    "source_reference",
    "is_example",
    "split",
}

ALLOWED_LANGUAGES = {"bn", "banglish", "hi", "en"}
ALLOWED_SCRIPTS = {"bengali", "latin", "devanagari", "mixed"}
ALLOWED_LABELS = {"scam", "genuine"}
ALLOWED_SCAM_CATEGORIES = {
    "banking_payment",
    "government_utility",
    "employment_financial_opportunity",
    "identity_account",
    "none",
}
ALLOWED_RED_FLAGS = {
    "urgent_action",
    "request_for_otp",
    "request_for_pin",
    "request_for_password",
    "request_for_payment",
    "suspicious_link",
    "impersonation",
    "unrealistic_reward",
    "secrecy_pressure",
    "remote_access_request",
    "mismatched_sender",
    "grammar_or_spelling_anomaly",
    "credential_harvesting",
    "advance_fee",
    "crypto_payment",
}
ALLOWED_SOURCE_TYPES = {
    "human_submitted",
    "synthetic_example",
    "public_report",
    "moderation_review",
    "expert_curated",
}
ALLOWED_SPLITS = {"train", "validation", "test"}


def load_dataset(path: str | Path) -> list[dict[str, Any]]:
    """Load a JSON array of dataset records from ``path``."""
    with Path(path).open("r", encoding="utf-8") as dataset_file:
        records = json.load(dataset_file)

    if not isinstance(records, list):
        raise ValueError("dataset root must be a JSON array")
    return records


def _is_allowed(value: Any, allowed: set[str]) -> bool:
    return isinstance(value, str) and value in allowed


def validate_records(records: Iterable[Any]) -> list[str]:
    """Return validation errors for an iterable of dataset records."""
    errors: list[str] = []
    seen_ids: set[str] = set()

    for index, record in enumerate(records):
        prefix = f"record {index}"
        if not isinstance(record, dict):
            errors.append(f"{prefix}: record must be an object")
            continue

        missing_fields = sorted(REQUIRED_FIELDS - record.keys())
        if missing_fields:
            errors.append(f"{prefix}: missing required fields: {', '.join(missing_fields)}")

        record_id = record.get("record_id")
        if not isinstance(record_id, str) or not record_id.strip():
            errors.append(f"{prefix}: record_id must be a non-empty string")
        elif record_id in seen_ids:
            errors.append(f"{prefix}: duplicate record_id: {record_id}")
        else:
            seen_ids.add(record_id)

        content = record.get("content")
        if not isinstance(content, str) or not content.strip():
            errors.append(f"{prefix}: content must be a non-empty string")

        enum_fields = {
            "language": ALLOWED_LANGUAGES,
            "script": ALLOWED_SCRIPTS,
            "label": ALLOWED_LABELS,
            "scam_category": ALLOWED_SCAM_CATEGORIES,
            "source_type": ALLOWED_SOURCE_TYPES,
        }
        for field, allowed in enum_fields.items():
            if not _is_allowed(record.get(field), allowed):
                errors.append(f"{prefix}: invalid {field}: {record.get(field)!r}")

        red_flags = record.get("red_flags")
        if not isinstance(red_flags, list):
            errors.append(f"{prefix}: red_flags must be an array")
        else:
            for red_flag in red_flags:
                if not _is_allowed(red_flag, ALLOWED_RED_FLAGS):
                    errors.append(f"{prefix}: invalid red_flag: {red_flag!r}")

        source_reference = record.get("source_reference")
        if not isinstance(source_reference, str) or not source_reference.strip():
            errors.append(f"{prefix}: source_reference must be a non-empty string")

        if not isinstance(record.get("is_example"), bool):
            errors.append(f"{prefix}: is_example must be a boolean")

        split = record.get("split")
        if split is not None and not _is_allowed(split, ALLOWED_SPLITS):
            errors.append(f"{prefix}: invalid split: {split!r}")

        label = record.get("label")
        category = record.get("scam_category")
        if label == "scam" and category == "none":
            errors.append(f"{prefix}: scam records must have a scam_category other than 'none'")
        if label == "genuine" and category != "none":
            errors.append("{}: genuine records must have scam_category 'none'".format(prefix))

    return errors


def summarize_records(records: Iterable[Any]) -> dict[str, dict[str, int]]:
    """Return counts by label, language, and scam category."""
    counters = {
        "label": Counter(),
        "language": Counter(),
        "scam_category": Counter(),
    }
    for record in records:
        if isinstance(record, dict):
            for field, counter in counters.items():
                value = record.get(field, "<missing>")
                counter[str(value)] += 1
    return {field: dict(counter) for field, counter in counters.items()}


def _print_summary(summary: dict[str, dict[str, int]]) -> None:
    for field in ("label", "language", "scam_category"):
        counts = ", ".join(
            f"{value}={count}" for value, count in sorted(summary[field].items())
        )
        print(f"{field}: {counts or '(none)'}")


def main(argv: list[str] | None = None) -> int:
    """Run the validator CLI and return a process exit code."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path, help="Path to a JSON dataset file")
    args = parser.parse_args(argv)

    try:
        records = load_dataset(args.dataset)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"Validation failed: {error}", file=sys.stderr)
        return 1

    errors = validate_records(records)
    print(f"records: {len(records)}")
    _print_summary(summarize_records(records))

    if errors:
        print("validation: failed")
        for error in errors:
            print(f"- {error}")
        return 1

    print("validation: passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
