"""Validate normalized Sotorko message records and source registry metadata."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable

try:
    from ml.validate_dataset import (
        ALLOWED_LANGUAGES,
        ALLOWED_RED_FLAGS,
        ALLOWED_SCAM_CATEGORIES,
        ALLOWED_SCRIPTS,
        ALLOWED_SOURCE_TYPES,
    )
except ModuleNotFoundError:  # Allow direct execution from the repository root.
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from ml.validate_dataset import (
        ALLOWED_LANGUAGES,
        ALLOWED_RED_FLAGS,
        ALLOWED_SCAM_CATEGORIES,
        ALLOWED_SCRIPTS,
        ALLOWED_SOURCE_TYPES,
    )


REQUIRED_FIELDS = {
    "id",
    "text",
    "language",
    "script",
    "label",
    "scam_category",
    "red_flags",
    "source_type",
    "source_reference",
    "source_id",
    "source_record_id",
    "original_label",
    "mapping_status",
}
ALLOWED_LABELS = {"scam", "genuine"}
ALLOWED_MAPPING_STATUSES = {"mapped", "excluded", "pending_review"}
REGISTRY_FIELDS = {
    "source_id",
    "name",
    "provider",
    "language",
    "input_type",
    "license",
    "license_status",
    "source_url",
    "original_labels",
    "intended_use",
    "redistribution_status",
    "attribution_required",
    "notes",
}


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _allowed(value: Any, values: set[str]) -> bool:
    return isinstance(value, str) and value in values


def validate_records(records: Iterable[Any]) -> list[str]:
    """Return validation errors for normalized message records."""
    errors: list[str] = []
    seen_ids: set[str] = set()

    for index, record in enumerate(records):
        prefix = f"record {index}"
        if not isinstance(record, dict):
            errors.append(f"{prefix}: record must be an object")
            continue

        missing = sorted(REQUIRED_FIELDS - record.keys())
        if missing:
            errors.append(f"{prefix}: missing required fields: {', '.join(missing)}")

        record_id = record.get("id")
        if not _non_empty_string(record_id):
            errors.append(f"{prefix}: id must be a non-empty string")
        elif record_id in seen_ids:
            errors.append(f"{prefix}: duplicate normalized id: {record_id}")
        else:
            seen_ids.add(record_id)

        if not _non_empty_string(record.get("text")):
            errors.append(f"{prefix}: text must be a non-empty string")

        enum_fields = {
            "language": ALLOWED_LANGUAGES,
            "script": ALLOWED_SCRIPTS,
            "scam_category": ALLOWED_SCAM_CATEGORIES,
            "source_type": ALLOWED_SOURCE_TYPES,
            "mapping_status": ALLOWED_MAPPING_STATUSES,
        }
        for field, allowed_values in enum_fields.items():
            if not _allowed(record.get(field), allowed_values):
                errors.append(f"{prefix}: invalid {field}: {record.get(field)!r}")

        label = record.get("label")
        mapping_status = record.get("mapping_status")
        if label is not None and not _allowed(label, ALLOWED_LABELS):
            errors.append(f"{prefix}: invalid label: {label!r}")
        if mapping_status == "mapped" and label not in ALLOWED_LABELS:
            errors.append(f"{prefix}: mapped records must have label scam or genuine")
        if mapping_status in {"excluded", "pending_review"} and label is not None:
            errors.append(f"{prefix}: {mapping_status} records must have label null")

        red_flags = record.get("red_flags")
        if not isinstance(red_flags, list):
            errors.append(f"{prefix}: red_flags must be an array")
        else:
            for red_flag in red_flags:
                if not _allowed(red_flag, ALLOWED_RED_FLAGS):
                    errors.append(f"{prefix}: invalid red_flag: {red_flag!r}")

        for field in ("source_reference", "source_id", "source_record_id", "original_label"):
            if not _non_empty_string(record.get(field)):
                errors.append(f"{prefix}: {field} must be a non-empty string")

        category = record.get("scam_category")
        if label == "scam" and category == "none":
            errors.append(f"{prefix}: scam records must have scam_category other than 'none'")
        if label == "genuine" and category != "none":
            errors.append(f"{prefix}: genuine records must have scam_category 'none'")
        if mapping_status in {"excluded", "pending_review"} and category != "none":
            errors.append(f"{prefix}: unmapped records must have scam_category 'none'")

    return errors


def load_json_records(path: str | Path) -> list[Any]:
    """Load a JSON array from a normalized dataset file."""
    with Path(path).open("r", encoding="utf-8") as input_file:
        records = json.load(input_file)
    if not isinstance(records, list):
        raise ValueError("normalized dataset root must be a JSON array")
    return records


def load_source_registry(path: str | Path) -> list[dict[str, Any]]:
    """Load and minimally validate the source registry structure."""
    with Path(path).open("r", encoding="utf-8") as input_file:
        registry = json.load(input_file)
    if not isinstance(registry, list):
        raise ValueError("source registry root must be a JSON array")

    errors: list[str] = []
    source_ids: set[str] = set()
    for index, entry in enumerate(registry):
        if not isinstance(entry, dict):
            errors.append(f"registry entry {index} must be an object")
            continue
        missing = sorted(REGISTRY_FIELDS - entry.keys())
        if missing:
            errors.append(f"registry entry {index} missing: {', '.join(missing)}")
        source_id = entry.get("source_id")
        if not _non_empty_string(source_id):
            errors.append(f"registry entry {index} has invalid source_id")
        elif source_id in source_ids:
            errors.append(f"registry entry {index} duplicates source_id {source_id}")
        else:
            source_ids.add(source_id)
    if errors:
        raise ValueError("; ".join(errors))
    return registry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_file", type=Path)
    args = parser.parse_args(argv)
    try:
        records = load_json_records(args.input_file)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"Validation failed: {error}", file=sys.stderr)
        return 1

    errors = validate_records(records)
    if errors:
        print("validation: failed")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"validation: passed ({len(records)} records)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
