# Data ingestion scripts

These scripts provide a reproducible ingestion framework without downloading, bundling, or generating datasets.

## Inspect a source file

```bash
python scripts/data/inspect_dataset.py path/to/local-file.csv
python scripts/data/inspect_dataset.py path/to/local-file.csv --label-column category
```

The inspector supports local JSON and CSV files and reports file type, count, fields, samples, label-like values, missing values, and duplicate rows. It does not assume a particular source column layout.

## Normalize a source file

```bash
python scripts/data/normalize_dataset.py SOURCE_ID input.csv output.json
```

The normalizer is intentionally adapter-based. Approved sources have stubs until their exact source metadata, columns, labels, licensing, and mappings are reviewed. It does not guess mappings or force URL data into the message schema.

## Validate normalized data

```bash
python scripts/data/validate_normalized_data.py path/to/normalized.json
```

The normalized validator checks the ingestion schema, provenance, mapping status, languages/scripts, labels, categories, red flags, and consistency rules. It returns a non-zero exit code on failure.
