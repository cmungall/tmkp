# Recommendations

## Use TMKP as candidate evidence, not curated truth

The raw edge layer has too many false positives for direct ingestion as a
trusted KG.

Recommended operating model:

1. Start with TMKP as candidate evidence.
2. Run deterministic QA tags.
3. Use agents to inspect high-risk rows and produce examples.
4. Estimate precision by slice.
5. Promote only high-fit rows.
6. Keep rejected rows with reasons.

## Publish trust tiers

Do not publish one undifferentiated KG. Publish trust tiers.

| Tier | Meaning |
| --- | --- |
| Trust after review | Exact mention match, direct claim, no obvious context problem. |
| Candidate | Useful text, but predicate or node may need checking. |
| Evidence only | Text is useful, edge is too broad or shifted. |
| Quarantine | Likely false positive from normalization or context. |
| Drop | Common-word, wrong entity type, or unsupported cross-product. |

## Hard quarantine candidates

Automatically quarantine or heavily down-rank:

- common-word subject/object mentions
- known abbreviation collisions
- family fan-out to unsupported specific genes
- negated or hedged causality
- method/protocol/reagent context
- list-sentence cross-products

## Review queue candidates

Route these to agents or manual review:

- short mentions with plausible expansions
- broad disease or symptom objects
- model or assay readouts
- biomarker/expression context
- treatment/cohort/adverse context with weak predicate fit
- generic family mentions where a specific node was assigned

## Concrete QA outputs per release

For each TMKP release, generate:

| File | Purpose |
| --- | --- |
| promoted candidates | Rows with strong mention, predicate, and context fit. |
| likely false positives | High-precision error signatures. |
| abbreviation collisions | Short mentions requiring local expansion. |
| family fan-out | `TNF` / `VEGF` / `PPAR` / `PD-1` / `COX2` cases. |
| model/assay rows | Useful evidence but not patient-level facts. |
| manual-review sample | Measured precision by slice. |

## What not to do

Do not:

- accept every normalized edge as a curated fact
- treat evidence count as validation
- mix true treatment, cohort exposure, and adverse event as one signal
- treat HPO symptom objects as clean disease phenotypes
- treat family-level molecular mentions as specific gene edges
- ignore negation and list context

These are the main causes of false positives in the current audit.

## Priority next work

1. Generate combined rule scores across all reviewed batches.
2. Add deterministic queue labels directly to audit export.
3. Add local abbreviation expansion checks.
4. Add family-level concept handling for `TNF`, `VEGF`, `PPAR`, `PD-1`, and
   `COX2`.
5. Separate clinical treatment, adverse-event, model-assay, biomarker, and
   molecular mechanism contexts.
6. Publish promoted/quarantine files with measured precision.
