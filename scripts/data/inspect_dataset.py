"""Inspect a local JSON or CSV dataset without assuming source columns."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


def load_records(path: str | Path) -> tuple[str, list[dict[str, Any]]]:
    """Load local JSON or CSV records and return the file type and rows."""
    file_path = Path(path)
    suffix = file_path.suffix.lower()
    if suffix == ".csv":
        with file_path.open("r", encoding="utf-8-sig", newline="") as input_file:
            return "CSV", [dict(row) for row in csv.DictReader(input_file)]
    if suffix == ".json":
        with file_path.open("r", encoding="utf-8") as input_file:
            value = json.load(input_file)
        if isinstance(value, list) and all(isinstance(row, dict) for row in value):
            return "JSON", value
        if isinstance(value, dict):
            return "JSON", [value]
        raise ValueError("JSON input must be an object or an array of objects")
    raise ValueError("unsupported file type; use .json or .csv")


def field_names(records: list[dict[str, Any]]) -> list[str]:
    """Return field names in first-seen order across records."""
    names: list[str] = []
    seen: set[str] = set()
    for record in records:
        for name in record:
            if name not in seen:
                names.append(name)
                seen.add(name)
    return names


def duplicate_count(records: list[dict[str, Any]]) -> int:
    """Count duplicate rows using canonical JSON serialization."""
    serialized = [json.dumps(row, ensure_ascii=False, sort_keys=True) for row in records]
    return len(serialized) - len(set(serialized))


def missing_values(records: list[dict[str, Any]], fields: list[str]) -> dict[str, int]:
    """Count missing or empty values for every discovered field."""
    return {
        field: sum(record.get(field) in (None, "") for record in records)
        for field in fields
    }


def label_values(records: list[dict[str, Any]], label_column: str | None) -> dict[str, int]:
    """Return unique values for an explicitly selected or obvious label field."""
    selected = label_column
    if selected is None:
        available = field_names(records)
        selected = next((field for field in available if field.lower() in {"label", "class", "category"}), None)
    if selected is None or not records or selected not in field_names(records):
        return {}
    return dict(Counter(str(record.get(selected)) for record in records))


def inspect(path: str | Path, label_column: str | None = None) -> dict[str, Any]:
    """Build an inspection report for a local dataset file."""
    file_type, records = load_records(path)
    fields = field_names(records)
    return {
        "file_type": file_type,
        "record_count": len(records),
        "fields": fields,
        "sample_records": records[:3],
        "unique_label_values": label_values(records, label_column),
        "missing_values": missing_values(records, fields),
        "duplicate_count": duplicate_count(records),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_file", type=Path)
    parser.add_argument("--label-column")
    args = parser.parse_args(argv)
    try:
        report = inspect(args.input_file, args.label_column)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        parser.error(str(error))
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
