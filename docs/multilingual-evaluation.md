# Multilingual smoke evaluation

## Purpose

This is a small, reproducible diagnostic set for checking the behavior and coverage of the current Sotorko prototype across Bengali, Banglish, Hindi, and English. It contains **32 synthetic examples**: four scam-labelled and four genuine-labelled examples per language. These are illustrative test cases, not messages collected from users and not a representative benchmark.

## Run it

From the repository root, with the project's dependencies installed:

```powershell
python scripts/evaluate_multilingual.py
```

The report lists each case's current result and summarizes scam-warning coverage, warning rate on genuine examples, and abstentions by language. An `ABSTAIN` means the service did not make a supported classification; it is not a safe verdict.

The automated fixture integrity test runs with the normal test suite:

```powershell
python -m pytest -q --basetemp "$PWD\.pytest-tmp-run"
```

## Important limitations

- Labels and messages are synthetic, authored to exercise common scenarios. They have not undergone independent expert annotation.
- Eight examples per language are not enough to estimate general accuracy, precision, or recall for real users.
- The current API has an English baseline model and experimental Bengali rules. Hindi and Banglish are intentionally reported as unsupported by the analysis service; this evaluation should expose that coverage gap, not disguise it.
- The English and Bengali components use different methods. Their outcomes should not be interpreted as directly comparable confidence scores.
- No rule match does not mean a message is genuine. Do not describe this diagnostic output as proof of safety or a production readiness certification.

## Next data step

Before model training or public accuracy claims, replace or supplement these scenarios with consented and appropriately licensed messages, record provenance and annotation decisions, review language/script labels with fluent speakers, deduplicate templates, and keep a held-out test set separate from rule tuning.
