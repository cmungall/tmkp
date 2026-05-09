# Deterministic QA

The deterministic QA framework is implemented in:

- `scripts/export_edge_audit.py`
- `scripts/score_edge_audit_rules.py`

It is deliberately simple. It does not try to be a curator. It flags rows that
are risky enough to require review.

## Evidence selection

For each edge, `export_edge_audit.py` chooses one representative evidence
snippet from `has_supporting_studies`.

It prefers evidence that:

1. has both subject and object mention offsets,
2. comes from an abstract,
3. has higher extraction confidence,
4. has longer supporting text as a tie-breaker.

Same KG input means the same audit row is selected.

## Mention-to-node agreement

The script canonicalizes mention text and normalized node names by lowercasing
and stripping punctuation. It checks exact match, substring match, or token
overlap.

`mention_mismatch` is an **at-risk flag**, not an automatic rejection.

| Case type | Example | Interpretation |
| --- | --- | --- |
| Clear false positive | `ten` -> pentaerythritol tetranitrate | `ten` came from ordinary text; reject or quarantine. |
| Clear false positive | `his` -> histidine | `his` was a pronoun; reject or quarantine. |
| Likely false positive | `BMD` -> vitelliform macular dystrophy 2 | Often bone mineral density; require local expansion. |
| Likely false positive | `ACS` -> acrocallosal syndrome or acute chest syndrome | Often acute coronary syndrome in cardiology text; require local expansion. |
| Valid abbreviation | `MTX` -> methotrexate | Keep if the sentence supports methotrexate. |
| Valid abbreviation | `G-CSF` -> filgrastim | Keep if context supports granulocyte colony-stimulating factor or filgrastim. |
| Partial mismatch | `VEGF` -> `VEGFA` | Accept only if local text names VEGF-A or an exact synonym. |

Across 6,000 manually reviewed rows, `mention_mismatch` caught 71.9% of manual
failures. Its failure precision was 55.7%, so it should route rows to review,
not delete every flagged edge.

## Common-word mentions

The script has a fixed list of common bad mentions:

`group`, `his`, `ten`, `duration`, `solution`, `ligand`, `biomarker`,
`control`, `case`, `cases`.

Examples:

| Edge | Problem |
| --- | --- |
| `Histidine -> Fever` | `his` was a pronoun. |
| `Pentaerythritol tetranitrate -> Fever` | `ten` came from "ten patients". |
| `Givinostat -> Duane Syndrome` | Object mention was `duration`. |
| `solution -> Edema` | Generic method/exposure word. |

This is the strongest deterministic signal. In the manual review, it had about
95% failure precision and 100% weak-or-bad precision.

## Short mention risk

The script flags mentions of four canonical characters or fewer when they do
not lexically match the normalized node.

Examples:

- `BMD`
- `ACS`
- `MDS`
- `SCD`
- `MAD`
- `PAH`
- `HHT`
- `AHA`
- `PCV`

Short mention risk is not always wrong. `MTX` and `G-CSF` can be valid. The
point is that the edge needs local abbreviation expansion before trust.

## Family fan-out

The script checks for common family or pathway terms:

`TNF`, `VEGF`, `PPAR`, `PD-1`, `COX2`, `MAPK`, `p38`, `calcineurin`, `AKT`,
`EGF`, `STAT`, `TGF-beta`, `NF-kB`.

If these occur in the mentions or normalized names, the row gets
`family_mention_fanout`.

Examples:

| Edge | Problem |
| --- | --- |
| `Infliximab -> TNFSF18` | Generic `TNF` became a specific TNF-superfamily gene. |
| `Pembrolizumab -> RPL17` | `PD-1` collision. |
| `Celecoxib -> MT-CO2` | `COX2` should mean `PTGS2` in context. |
| `VEGFC -> Edema` | Generic `VEGF` mapped to one family member. |

## Context tags

The script also looks for fixed word lists in evidence text.

| Tag | Example trigger words |
| --- | --- |
| `negation_or_hedging` | `no significant`, `did not`, `failed to`, `not associated`, `questionable`, `unlikely` |
| `treatment_context` | `treatment`, `therapy`, `trial`, `dose`, `efficacy`, `patients received` |
| `adverse_or_risk_context` | `adverse`, `risk`, `induced`, `toxicity`, `side effect` |
| `cohort_or_exposure_context` | `patients with`, `history of`, `case report`, `cohort`, `received` |
| `mechanism_context` | `activation`, `expression`, `inhibit`, `phosphorylation`, `knockdown` |
| `biomarker_or_expression_context` | `marker`, `serum`, `level`, `prognosis`, `expressed` |
| `model_or_assay_context` | `mice`, `rat`, `in vitro`, `cell line`, `assay` |
| `method_or_reagent_context` | `buffer`, `medium`, `staining`, `western blot`, `reagent` |
| `list_or_cross_product_context` | `including`, `such as`, `respectively`, plus several commas/semicolons |

## Rule scoring

`score_edge_audit_rules.py` compares deterministic tags against manual labels.

Definitions:

- failure: `unsupported` or `unclear`
- weak-or-bad: `partially_supported`, `unsupported`, or `unclear`

Combined results across 6,000 manual rows:

| Rule tag | Tagged rows | Failure precision | Weak/bad precision | Failure recall |
| --- | ---: | ---: | ---: | ---: |
| `common_word_mention` | 37 | 94.6% | 100.0% | 1.4% |
| `short_mention_risk` | 1,912 | 70.7% | 85.6% | 53.5% |
| `family_mention_fanout` | 338 | 67.5% | 94.1% | 9.0% |
| `method_or_reagent_context` | 159 | 64.2% | 78.6% | 4.0% |
| `negation_or_hedging` | 199 | 63.3% | 77.9% | 5.0% |
| `mention_mismatch` | 3,258 | 55.7% | 75.1% | 71.9% |

The best interpretation is: these rules are QA routing signals. They identify
where agents or curators should look first.
