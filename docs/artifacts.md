# Artifacts

## Audit tables

| File | Description |
| --- | --- |
| `audits/tmkp_edge_audit_2026_04_21_batch_001.csv` | First 3,000-row stratified audit table. |
| `audits/tmkp_edge_audit_2026_04_21_batch_002.csv` | Second 3,000-row audit table, excluding batch 001 edge IDs. |
| `audits/manifest.yml` | Batch metadata and expected counts. |

## Manual review tables

| File | Description |
| --- | --- |
| `evaluations/tmkp_edge_audit_2026_04_21_batch_001_manual_review.csv` | Completed manual review for batch 001. |
| `evaluations/tmkp_edge_audit_2026_04_21_batch_002_manual_review.csv` | Completed manual review for batch 002. |
| `evaluations/batch_002/` | Chunked labels for batch 002. |

## Rule score outputs

| File | Description |
| --- | --- |
| `evaluations/tmkp_edge_audit_2026_04_21_batch_001_rule_scores.csv` | Deterministic tag scoring against batch 001 manual review. |
| `evaluations/tmkp_edge_audit_2026_04_21_batch_002_rule_scores.csv` | Deterministic tag scoring against batch 002 manual review. |
| `evaluations/tmkp_edge_audit_2026_04_21_rule_score_notes.md` | Notes and observations from the combined analysis. |

## Scripts

| Script | Purpose |
| --- | --- |
| `scripts/export_edge_audit.py` | Export batch-aware stratified audit CSVs and deterministic tags. |
| `scripts/validate_edge_audit.py` | Validate audit CSV schema and counts. |
| `scripts/init_edge_audit_evaluation.py` | Initialize manual review tables. |
| `scripts/apply_edge_audit_manual_labels.py` | Apply prepared manual label chunks. |
| `scripts/review_edge_audit.py` | Interactive row review helper. |
| `scripts/score_edge_audit_rules.py` | Score deterministic tags against manual labels. |

## Reproduce checks

Validate both audit batches:

```sh
uv run python scripts/validate_edge_audit.py \
  audits/tmkp_edge_audit_2026_04_21_batch_001.csv

uv run python scripts/validate_edge_audit.py \
  audits/tmkp_edge_audit_2026_04_21_batch_002.csv \
  --expected-batch-id tmkp-2026-04-21-edge-audit-batch-002 \
  --skip-decision-count-check
```

Score deterministic rules:

```sh
uv run python scripts/score_edge_audit_rules.py \
  --review evaluations/tmkp_edge_audit_2026_04_21_batch_002_manual_review.csv \
  --output evaluations/tmkp_edge_audit_2026_04_21_batch_002_rule_scores.csv
```

Render the slides:

```sh
marp slides/tmkp_analysis_recommendations.md \
  --html \
  --output slides/tmkp_analysis_recommendations.html
```

Build this website:

```sh
mkdocs build --strict
```
