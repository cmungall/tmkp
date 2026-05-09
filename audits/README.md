# TMKP edge audit artifacts

This directory tracks structured review tables for TMKP KGX edge audits.

The current CSV schema is designed for edge-level review from the local DuckDB
database at `downloads/tmkp/2026_04_21/tmkp.duckdb`.

## Files

- `tmkp_edge_audit_2026_04_21_batch_001.csv`: stratified 3,000-row audit table.
- `tmkp_edge_audit_2026_04_21_batch_002.csv`: second stratified 3,000-row
  audit table excluding all batch 001 edge IDs.
- `manifest.yml`: expected counts and batch metadata for tracked audit files.

Validate the tracked batches with:

```sh
uv run python scripts/validate_edge_audit.py
uv run python scripts/validate_edge_audit.py \
  audits/tmkp_edge_audit_2026_04_21_batch_002.csv \
  --expected-batch-id tmkp-2026-04-21-edge-audit-batch-002 \
  --skip-decision-count-check
```

## Batch 001 summary

- Rows: 3,000 edge/evidence reviews plus one CSV header row.
- Distinct KGX edges: 3,000.
- Rows with populated supporting text: 3,000.
- Audit method: `assistant_structured_evidence_review_v1`.
- Reviewer: `codex`.
- Review date: `2026-05-04`.

Decision counts:

| Decision | Rows |
| --- | ---: |
| `needs_review` | 2,068 |
| `partially_supported` | 848 |
| `supported` | 65 |
| `unsupported` | 19 |

Stratum counts:

| Stratum | Rows |
| --- | ---: |
| `gene_disease_contributes` | 500 |
| `chemical_disease_treatment` | 450 |
| `chemical_gene_mechanism` | 450 |
| `gene_gene_mechanism` | 400 |
| `chemical_disease_contributes` | 300 |
| `gene_phenotype` | 250 |
| `chemical_phenotype_treatment` | 225 |
| `chemical_phenotype_contributes` | 225 |
| `protein_disease` | 100 |
| `protein_gene_mechanism` | 100 |

## Batch 002 summary

- Rows: 3,000 edge/evidence reviews plus one CSV header row.
- Distinct KGX edges: 3,000.
- Rows with populated supporting text: 3,000.
- Audit method: `assistant_structured_evidence_review_v1`.
- Reviewer: `codex`.
- Review date: `2026-05-04`.
- Overlap with batch 001 edge IDs: 0.

Decision counts:

| Decision | Rows |
| --- | ---: |
| `needs_review` | 2,106 |
| `partially_supported` | 825 |
| `supported` | 51 |
| `unsupported` | 18 |

Stratum counts:

| Stratum | Rows |
| --- | ---: |
| `gene_disease_contributes` | 500 |
| `chemical_disease_treatment` | 450 |
| `chemical_gene_mechanism` | 450 |
| `gene_gene_mechanism` | 400 |
| `chemical_disease_contributes` | 300 |
| `gene_phenotype` | 250 |
| `chemical_phenotype_contributes` | 225 |
| `chemical_phenotype_treatment` | 225 |
| `protein_disease` | 100 |
| `protein_gene_mechanism` | 100 |

## Key columns

- `audit_id`: stable row identifier for this audit batch.
- `audit_batch_id`: batch identifier for grouping rows.
- `audit_method`: review method used to assign `audit_decision` and `audit_tags`.
- `audit_decision`: one of `supported`, `partially_supported`, `unsupported`, or
  `needs_review`.
- `audit_tags`: pipe-separated taxonomy tags, such as `short_mention_risk`,
  `generic_object`, `family_mention_fanout`, `negation_or_hedging`,
  `model_or_assay_context`, `biomarker_or_expression_context`,
  `treatment_context`, `adverse_or_risk_context`,
  `cohort_or_exposure_context`, `method_or_reagent_context`, and
  `mention_mismatch`.
- `audit_note`: short explanation of why the row received the decision/tags.
- `stratum`: broad subject/object/predicate review slice used for sampling.
- `edge_id`, `subject_id`, `predicate`, `object_id`: KGX edge identity.
- `subject_mention`, `object_mention`, `supporting_text`: evidence text and
  extracted mention spans used for the review row.

For high-evidence-count edges, each row records one representative supporting
study result selected from the KGX evidence payload. Treat `unsupported` or
`needs_review` as evidence-row findings unless every supporting study has been
reviewed.
