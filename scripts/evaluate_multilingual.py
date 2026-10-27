"""Run a small, synthetic multilingual smoke evaluation of current Sotorko behavior.

This is a diagnostic, not a validated benchmark. Unsupported responses are counted
as abstentions, never as proof that a message is genuine.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE = ROOT / "tests" / "fixtures" / "multilingual_smoke_cases.json"
sys.path.insert(0, str(ROOT))

from app.schemas.analysis import AnalysisRequest  # noqa: E402
from app.services import analyzer, bengali  # noqa: E402

LANGUAGES = {"bn", "banglish", "hi", "en"}
LABELS = {"scam", "genuine"}


def load_cases(path: Path = DEFAULT_FIXTURE) -> list[dict[str, Any]]:
    """Load and validate the synthetic evaluation fixture."""
    cases = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(cases, list) or not cases:
        raise ValueError("evaluation fixture must be a non-empty JSON array")
    ids: set[str] = set()
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            raise ValueError(f"case {index} must be an object")
        required = {"record_id", "language", "script", "label", "scenario", "content", "synthetic"}
        missing = required - case.keys()
        if missing:
            raise ValueError(f"case {index} missing fields: {sorted(missing)}")
        if not isinstance(case["record_id"], str) or not case["record_id"].strip():
            raise ValueError(f"case {index} has an empty record_id")
        if case["record_id"] in ids:
            raise ValueError(f"duplicate record_id: {case['record_id']}")
        ids.add(case["record_id"])
        if case["language"] not in LANGUAGES:
            raise ValueError(f"case {case['record_id']} has invalid language")
        if case["label"] not in LABELS:
            raise ValueError(f"case {case['record_id']} has invalid label")
        if not isinstance(case["content"], str) or not case["content"].strip():
            raise ValueError(f"case {case['record_id']} has empty content")
        if case["synthetic"] is not True:
            raise ValueError(f"case {case['record_id']} must be explicitly marked synthetic")
    return cases


def analyze_case(case: dict[str, Any]) -> Any:
    request = AnalysisRequest(
        input_type="text",
        content=case["content"],
        language=case["language"],
        incident_status="unknown",
    )
    if case["language"] == "bn":
        return bengali.analyze(request)
    # The main analysis service deliberately returns unsupported for hi and Banglish.
    return analyzer.analyze_text(request)


def evaluate(cases: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, dict[str, int]]]:
    details: list[dict[str, Any]] = []
    metrics: dict[str, dict[str, int]] = defaultdict(
        lambda: {"total": 0, "scam": 0, "genuine": 0, "alerts_scam": 0,
                 "alerts_genuine": 0, "abstentions": 0, "resolved_scam": 0,
                 "resolved_genuine": 0, "missed_scam_alerts": 0}
    )
    for case in cases:
        response = analyze_case(case)
        language = case["language"]
        is_abstention = response.status.value != "predicted" or response.verdict.value == "unsupported"
        alert = response.verdict.value in {"suspicious", "likely_scam"}
        row = {
            "record_id": case["record_id"],
            "language": language,
            "label": case["label"],
            "status": response.status.value,
            "verdict": response.verdict.value,
            "analysis_mode": response.analysis_mode,
            "outcome": "ABSTAIN" if is_abstention else ("ALERT" if alert else "NO_ALERT"),
        }
        details.append(row)
        metric = metrics[language]
        metric["total"] += 1
        metric[case["label"]] += 1
        if is_abstention:
            metric["abstentions"] += 1
            continue
        metric[f"resolved_{case['label']}"] += 1
        if alert and case["label"] == "scam":
            metric["alerts_scam"] += 1
        elif alert and case["label"] == "genuine":
            metric["alerts_genuine"] += 1
        elif case["label"] == "scam":
            metric["missed_scam_alerts"] += 1
    return details, dict(metrics)


def pct(numerator: int, denominator: int) -> str:
    return "n/a" if denominator == 0 else f"{numerator / denominator:.0%}"


def main() -> int:
    try:
        cases = load_cases()
        details, metrics = evaluate(cases)
    except Exception as exc:
        print(f"Evaluation could not run: {exc}", file=sys.stderr)
        return 1

    print("SOTORKO MULTILINGUAL SMOKE EVALUATION")
    print(f"Synthetic cases: {len(cases)} | Languages: {', '.join(sorted(LANGUAGES))}")
    print("OUTCOME counts: ALERT = warning verdict; NO_ALERT = resolved without warning; ABSTAIN = unsupported/unavailable.")
    print()
    print(f"{'ID':<20} {'LANG':<9} {'LABEL':<8} {'OUTCOME':<10} {'VERDICT':<23} MODE")
    for row in details:
        print(f"{row['record_id']:<20} {row['language']:<9} {row['label']:<8} "
              f"{row['outcome']:<10} {row['verdict']:<23} {row['analysis_mode']}")
    print()
    print("PER-LANGUAGE SUMMARY")
    print(f"{'LANG':<9} {'CASES':>5} {'SCAM ALERT':>12} {'GENUINE ALERT':>14} {'ABSTAIN':>8} {'RESOLVED SCAM':>14}")
    for lang in sorted(metrics):
        m = metrics[lang]
        print(f"{lang:<9} {m['total']:>5} "
              f"{pct(m['alerts_scam'], m['scam']):>12} "
              f"{pct(m['alerts_genuine'], m['genuine']):>14} "
              f"{m['abstentions']:>8} {m['resolved_scam']:>14}")
    print()
    print("Interpretation: scam alert rate uses all synthetic scam cases; abstentions are not treated as successful detections.")
    print("Genuine alert rate uses all synthetic genuine cases. These figures are descriptive only, not real-world accuracy estimates.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
