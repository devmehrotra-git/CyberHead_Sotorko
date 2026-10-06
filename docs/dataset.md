# Sotorko Dataset Specification

## Purpose

The Sotorko dataset will support future development and evaluation of vernacular digital-safety analysis. It is intended to represent short messages and URLs in Bengali, Banglish, Hindi, and English, with consistent scam/genuine labels and human-readable safety metadata.

The dataset specification is documentation only. It does not implement machine learning, detection rules, collection, or annotation tooling.

## Record schema

The canonical record is represented as JSON or as one row in a CSV export.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `record_id` | string | yes | Stable unique identifier for the record. |
| `content` | string | yes | Message text or URL submitted for annotation. It must be non-empty. |
| `language` | enum | yes | `bn`, `banglish`, `hi`, or `en`. |
| `script` | enum | yes | `bengali`, `latin`, `devanagari`, or `mixed`. |
| `label` | enum | yes | `scam` or `genuine`. |
| `scam_category` | enum | yes | A category from the taxonomy below; genuine records use `none`. |
| `red_flags` | array of enum values | yes | Zero or more red flags from the taxonomy below. |
| `source_type` | enum | yes | Provenance classification from the values below. |
| `source_reference` | string | yes | Human-readable provenance reference, such as a source ID, citation, or collection note. |
| `is_example` | boolean | yes | `true` for documentation examples; examples are never evaluation data. |
| `split` | enum or null | yes | `train`, `validation`, or `test` for dataset records; `null` for example-only records. |

### JSON and CSV representation

JSON uses an array of objects, with `red_flags` represented as an array. CSV uses one record per row and stores `red_flags` as a semicolon-separated list of taxonomy values. Empty CSV lists are represented by an empty field. UTF-8 must be used for both formats.

Example-only records may set `is_example` to `true` and `split` to `null`. They must not be included in any train, validation, or test export.

## Controlled values

### Language

- `bn` — Bengali language
- `banglish` — Bengali expressed primarily with Latin characters
- `hi` — Hindi language
- `en` — English language

### Script

- `bengali` — Bengali script
- `latin` — Latin/Roman script
- `devanagari` — Devanagari script
- `mixed` — More than one script in the same record

### Labels

- `scam` — The record contains a deceptive or fraudulent attempt, or is a faithful representation of one.
- `genuine` — The record is a legitimate, non-deceptive message.

### Scam categories

The `scam_category` taxonomy is locked to exactly these five values:

- `banking_payment` — Fraud involving payments, transfers, wallets, or banking.
- `government_utility` — Fraud impersonating or abusing government, utility, or public-service workflows.
- `employment_financial_opportunity` — Fraudulent jobs, investments, prizes, grants, or other financial opportunities.
- `identity_account` — Attempts to obtain identity information, credentials, OTPs, or account access.
- `none` — Required for `genuine` records.

Terms such as phishing, lottery, and delivery describe scam patterns or message context. They must be represented in `red_flags` or explanatory text, never as additional `scam_category` values.

### Red-flag taxonomy

- `urgent_action` — Pressure to act immediately.
- `request_for_otp` — Request for a one-time password or verification code.
- `request_for_pin` — Request for a PIN or similar secret.
- `request_for_password` — Request for a password or login credential.
- `request_for_payment` — Request for money, fees, or a transfer.
- `suspicious_link` — Link or URL presented as suspicious or misleading.
- `impersonation` — Sender claims a trusted identity without reliable proof.
- `unrealistic_reward` — Unusually large, guaranteed, or implausible benefit.
- `secrecy_pressure` — Request to hide the interaction from others.
- `remote_access_request` — Request to install software or grant device access.
- `mismatched_sender` — Sender identity does not match the claimed organization.
- `grammar_or_spelling_anomaly` — Notable language anomalies that support suspicion.
- `credential_harvesting` — Message directs the recipient to submit sensitive information.
- `advance_fee` — Payment is required before a promised service, prize, or benefit.
- `crypto_payment` — Cryptocurrency payment is requested as part of the claim.

### Source type

- `human_submitted` — Submitted by a user or participant.
- `synthetic_example` — Created solely to illustrate the schema or a concept.
- `public_report` — Derived from a publicly available report with provenance recorded separately.
- `moderation_review` — Collected or confirmed during a moderation review.
- `expert_curated` — Curated or reviewed by a qualified annotator.

### Source reference

`source_reference` identifies where the record came from without embedding sensitive source data. For a public report, use a citation or stable report identifier. For a human-submitted or reviewed record, use a consented internal reference. For a synthetic example, use a clear note such as `documentation example only`.

## Data quality rules

1. Records must be UTF-8 and contain a non-empty `content` value.
2. Each record must have exactly one `language`, `script`, `label`, `scam_category`, and `source_type` value from the controlled lists.
3. `genuine` records must use `scam_category: none`; scam records must not use `none`.
4. `genuine` records should have an empty `red_flags` array unless an annotation note explains why a flag is present.
5. Annotations must describe the content faithfully and must not add facts absent from the record.
6. Personally identifying information, live credentials, OTPs, payment details, and active malicious links must be removed or safely redacted before inclusion.
7. Each record must be reviewed for language and script accuracy.
8. `source_reference` must be a non-empty provenance reference and must not contain secrets or unnecessary personal information.
9. Example records must have `is_example: true`, `source_type: synthetic_example`, a documentation-only `source_reference`, and `split: null`.

## Deduplication

Duplicate and near-duplicate records must be detected and removed before splitting. Exact duplicates, normalized duplicates, and copied message templates with only superficial substitutions must not appear across different splits. If duplicates are retained for an annotation reason, all members of the duplicate group must remain in the same split.

## Dataset split

The target split is:

- 70% training data
- 15% validation data
- 15% test data

The split should be stratified where practical across language, label, and scam category. The test data must remain isolated during development: it must not be used for rule tuning, model training, threshold selection, prompt iteration, or repeated manual inspection. Test data may be accessed only for the final evaluation procedure.
