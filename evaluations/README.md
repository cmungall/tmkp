# TMKP edge audit evaluation

This directory evaluates the deterministic triage rules against an independent
manual review layer. The audit CSVs remain in `audits/`; this directory stores
manual labels, merged manual-review tables, and rule-score outputs.

## Current artifacts

| Batch | Audit source | Manual review | Rule scores |
| --- | --- | --- | --- |
| `001` | `audits/tmkp_edge_audit_2026_04_21_batch_001.csv` | `evaluations/tmkp_edge_audit_2026_04_21_batch_001_manual_review.csv` | `evaluations/tmkp_edge_audit_2026_04_21_batch_001_rule_scores.csv` |
| `002` | `audits/tmkp_edge_audit_2026_04_21_batch_002.csv` | `evaluations/tmkp_edge_audit_2026_04_21_batch_002_manual_review.csv` | `evaluations/tmkp_edge_audit_2026_04_21_batch_002_rule_scores.csv` |

Batch 002 manual labels were applied from chunk files under
`evaluations/batch_002/`.

## Workflow

Initialize a manual review table for a specific audit file:

```sh
uv run python scripts/init_edge_audit_evaluation.py \
  --audit audits/tmkp_edge_audit_2026_04_21_batch_002.csv \
  --output evaluations/tmkp_edge_audit_2026_04_21_batch_002_manual_review.csv
```

Apply a prepared label chunk:

```sh
uv run python scripts/apply_edge_audit_manual_labels.py \
  --review evaluations/tmkp_edge_audit_2026_04_21_batch_002_manual_review.csv \
  --labels evaluations/batch_002/manual_review_labels_2901_3000.csv
```

Review rows interactively:

```sh
uv run python scripts/review_edge_audit.py \
  --review evaluations/tmkp_edge_audit_2026_04_21_batch_002_manual_review.csv \
  --limit 25
```

Score the triage rules once manual labels exist:

```sh
uv run python scripts/score_edge_audit_rules.py \
  --review evaluations/tmkp_edge_audit_2026_04_21_batch_002_manual_review.csv \
  --output evaluations/tmkp_edge_audit_2026_04_21_batch_002_rule_scores.csv
```

The scoring script intentionally refuses to run unless at least one row has
`manual_review_status=complete`. This prevents accidentally evaluating the
rules against their own deterministic output.

## Manual label counts

Batch 001 final labels:

| Manual edge support | Rows |
| --- | ---: |
| `unsupported` | 1,332 |
| `supported` | 1,018 |
| `partially_supported` | 633 |
| `unclear` | 17 |

Batch 002 final labels:

| Manual edge support | Rows |
| --- | ---: |
| `supported` | 1,199 |
| `unsupported` | 1,166 |
| `partially_supported` | 623 |
| `unclear` | 12 |

## Manual labels

Use `manual_edge_support` for the final edge/evidence judgment:

- `supported`: the evidence text supports the normalized edge and predicate.
- `partially_supported`: the evidence supports a weaker or related claim, but
  the normalized edge or predicate is too broad.
- `unsupported`: the evidence does not support the normalized edge.
- `unclear`: the row cannot be judged from the recorded evidence text alone.

Use `manual_error_tags` for pipe-separated failure modes such as:

- `normalization_error`
- `predicate_overbroad`
- `abbreviation_collision`
- `generic_object`
- `family_fanout`
- `model_or_assay_only`
- `biomarker_or_expression_only`
- `cohort_or_exposure_only`
- `negation_or_hedging`
- `list_or_cross_product`
- `method_or_reagent_only`
