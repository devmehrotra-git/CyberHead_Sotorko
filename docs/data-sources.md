# Sotorko Data Sources and Ingestion Design

This document records the approved source categories for future ingestion. It is a planning and provenance document only: no external datasets are downloaded, copied, or redistributed by this repository.

## Source registry

Machine-readable source metadata is kept in [`data/sources/source_registry.json`](../data/sources/source_registry.json). Each entry records the source identity, provider, language, input type, original labels, intended use, license status, redistribution status, and attribution requirements.

License and redistribution status must be rechecked against the source's current metadata before any ingestion or public redistribution. `source_id` values are stable identifiers and must be preserved in normalized records.

## Approved sources

### Mendeley SMS Phishing Dataset

- **Language:** English
- **Input type:** Text message
- **Purpose:** Message-level smishing and fraud detection.
- **Original labels:** Source-defined phishing/smishing or related labels; preserve them exactly in `original_label`.
- **License:** Listed as CC BY 4.0; source metadata must be verified before final ingestion.
- **Redistribution:** Local use remains pending review until the source metadata and attribution requirements are verified.
- **Attribution:** Required; cite the source and provider in any derivative dataset documentation.
- **Suitability:** Useful for English message-level patterns, but source labels are not automatically Sotorko labels.

### UCI SMS Spam Collection

- **Language:** English
- **Input type:** Text message
- **Purpose:** General SMS spam/ham robustness.
- **Original labels:** `spam` and `ham`; preserve them exactly in `original_label`.
- **License:** CC BY 4.0 as recorded in the source registry.
- **Redistribution:** Approved for a public derivative subject to attribution and verification of the source terms.
- **Attribution:** Required.
- **Suitability:** Useful as a broad SMS robustness source, but `spam` is not synonymous with scam and requires an explicit mapping decision.

### Mendeley Bangla SMS Spam/Ham Dataset

- **Language:** Bengali
- **Input type:** Text message
- **Purpose:** Bengali-language adaptation and spam/ham robustness.
- **Original labels:** Source-defined spam/ham labels; preserve them exactly in `original_label`.
- **License:** Listed as CC BY 4.0; source metadata must be verified before final ingestion.
- **Redistribution:** Local use remains pending review until source terms are verified.
- **Attribution:** Required.
- **Suitability:** Useful for Bengali language coverage, but annotations must distinguish nuisance spam from fraud.

### BTTC Bangla Dataset

- **Language:** Bengali
- **Input type:** Text message
- **Purpose:** Bengali spam- and fraud-oriented coverage.
- **Original labels:** Preserve the exact labels supplied by BTTC.
- **License:** Listed as CC BY 4.0; source metadata must be verified before final ingestion.
- **Redistribution:** Local use remains pending review until source terms are verified.
- **Attribution:** Required.
- **Suitability:** Potentially useful for Bengali fraud-oriented patterns, subject to label review, provenance review, and redaction.

### Hindi SMS Dataset

- **Language:** Hindi
- **Input type:** Text message
- **Purpose:** Hindi-language adaptation.
- **Original labels:** Preserve the exact source labels; do not assume their semantics.
- **License:** Pending verification.
- **Redistribution:** `local_use_pending_review`; do not ingest it into the public redistributed pipeline yet.
- **Attribution:** Required once the source terms are verified.
- **Suitability:** Potentially useful for Hindi coverage, but it cannot be an approved redistributed source until licensing and provenance are resolved.

### Mendeley Phishing URL Dataset

- **Language:** Not applicable to the URL itself; any associated text metadata must be handled separately.
- **Input type:** URL
- **Purpose:** URL phishing analysis.
- **Original labels:** Preserve the exact URL labels.
- **License:** Listed as CC BY 4.0; source metadata must be verified before final ingestion.
- **Redistribution:** Local use remains pending review until source terms are verified.
- **Attribution:** Required.
- **Suitability:** Useful for URL analysis, but URL records remain separate from message classification and are not forced into the message schema.

## Normalization design

Ingestion separates the following concerns:

1. **Raw source label:** The unchanged value supplied by the source, stored as `original_label`.
2. **Normalized language and script:** Values normalized to the Sotorko language/script taxonomy without changing the raw content.
3. **Sotorko label:** `scam` or `genuine` only after an explicit, documented mapping decision.
4. **Sotorko scam category:** One of `banking_payment`, `government_utility`, `employment_financial_opportunity`, `identity_account`, or `none`.
5. **Red-flag annotations:** Zero or more values from the existing Sotorko red-flag taxonomy.
6. **Provenance:** `source_id`, `source_record_id`, `source_type`, `source_reference`, and `original_label`.

Every normalized message record also carries `mapping_status`, which is one of:

- `mapped` — The source label and record were confidently mapped.
- `excluded` — The record is retained for audit/provenance but excluded from model-ready data.
- `pending_review` — The record needs a human or licensing review before mapping.

Records that cannot be confidently mapped must be excluded or marked pending review. They must not be guessed into `scam` or `genuine`.

Source `spam` labels must not automatically become Sotorko `scam` labels. Spam can be unwanted advertising, bulk messaging, or nuisance content without being a deceptive financial or identity-related scam. Any mapping must be source-specific, documented, and reviewable; otherwise the record remains excluded or pending review.

## URL separation

URL sources use a separate normalized URL pipeline. URL records preserve at least `url`, `original_label`, `source_id`, and `source_record_id`. They are not forced into the message fields `text`, `language`, `script`, or message-level red flags until a separate URL schema is approved.

## Banglish as a later derived layer

Banglish augmentation is a later derived layer, not a raw-source assumption. It must be generated only after source records, licensing, labels, and Bengali-language quality are settled. Derived Banglish records must retain links to their parent record and must not be mixed into evaluation data without an explicit split and provenance policy.

## Reproducibility and safety

- External files belong under ignored `data/external/` and are never committed by default.
- Generated normalized and derived outputs belong under ignored `data/processed/` and `data/derived/`.
- Source adapters must preserve original labels and provenance.
- Attribution and license checks must be completed before public redistribution.
- No model training, rules, OCR, API changes, or external downloads are part of this ingestion foundation.
