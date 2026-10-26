"""Adapter-based normalization framework for approved local source files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Protocol

try:
    from scripts.data.inspect_dataset import load_records
except ModuleNotFoundError:  # Allow direct execution from the repository root.
    from inspect_dataset import load_records


class SourceAdapter(Protocol):
    """Interface implemented by a reviewed source-specific adapter."""

    def normalize(self, record: dict[str, Any], source_id: str) -> dict[str, Any]:
        """Normalize one source record without guessing its label semantics."""


class AdapterStub:
    """Placeholder adapter that refuses unreviewed source mappings."""

    def normalize(self, record: dict[str, Any], source_id: str) -> dict[str, Any]:
        raise NotImplementedError(
            f"no reviewed adapter is implemented for source_id={source_id!r}"
        )


SOURCE_ADAPTERS: dict[str, SourceAdapter] = {
    "mendeley_sms_phishing": AdapterStub(),
    "uci_sms_spam_collection": AdapterStub(),
    "mendeley_bangla_sms_spam_ham": AdapterStub(),
    "bttc_bangla": AdapterStub(),
    "hindi_sms_pending_license": AdapterStub(),
    "mendeley_phishing_url": AdapterStub(),
}


def normalize_records(source_id: str, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalize records through a registered, reviewed source adapter."""
    adapter = SOURCE_ADAPTERS.get(source_id)
    if adapter is None:
        raise ValueError(f"no adapter registered for source_id={source_id!r}")
    return [adapter.normalize(record, source_id) for record in records]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_id")
    parser.add_argument("input_file", type=Path)
    parser.add_argument("output_file", type=Path)
    args = parser.parse_args(argv)

    try:
        _, records = load_records(args.input_file)
        normalized = normalize_records(args.source_id, records)
    except (OSError, ValueError, json.JSONDecodeError, NotImplementedError) as error:
        print(f"Normalization stopped: {error}")
        return 1

    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    args.output_file.write_text(
        json.dumps(normalized, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(normalized)} records to {args.output_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
