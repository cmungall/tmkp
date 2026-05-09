# TMKP rule score notes

Completed checkpoints: 6,000 manually reviewed rows across
`tmkp_edge_audit_2026_04_21_batch_001_manual_review.csv` and
`tmkp_edge_audit_2026_04_21_batch_002_manual_review.csv`.

All sampled audit rows are now complete. The companion score files are
`tmkp_edge_audit_2026_04_21_batch_001_rule_scores.csv` and
`tmkp_edge_audit_2026_04_21_batch_002_rule_scores.csv`.

## Batch 001 final manual label counts

| Manual edge support | Rows |
| --- | ---: |
| `unsupported` | 1,332 |
| `supported` | 1,018 |
| `partially_supported` | 633 |
| `unclear` | 17 |

## Batch 001 final top rule signals

Highest failure precision after scoring all 3,000 manually reviewed rows:

| Rule tag | Tagged rows | Failure precision | Weak-or-bad precision |
| --- | ---: | ---: | ---: |
| `common_word_mention` | 19 | 89.5% | 100.0% |
| `family_mention_fanout` | 170 | 80.0% | 95.3% |
| `short_mention_risk` | 933 | 75.1% | 87.6% |
| `method_or_reagent_context` | 74 | 73.0% | 79.7% |
| `negation_or_hedging` | 117 | 61.5% | 76.1% |
| `mention_mismatch` | 1,594 | 60.0% | 78.4% |
| `cohort_or_exposure_context` | 225 | 50.2% | 71.1% |
| `mechanism_context` | 949 | 49.5% | 71.4% |

## Batch 002 final manual label counts

| Manual edge support | Rows |
| --- | ---: |
| `supported` | 1,199 |
| `unsupported` | 1,166 |
| `partially_supported` | 623 |
| `unclear` | 12 |

## Batch 002 final top rule signals

Highest failure precision after scoring all 3,000 manually reviewed rows:

| Rule tag | Tagged rows | Failure precision | Weak-or-bad precision |
| --- | ---: | ---: | ---: |
| `common_word_mention` | 18 | 100.0% | 100.0% |
| `short_mention_risk` | 979 | 66.5% | 83.7% |
| `negation_or_hedging` | 82 | 65.9% | 80.5% |
| `method_or_reagent_context` | 85 | 56.5% | 77.6% |
| `family_mention_fanout` | 168 | 54.8% | 92.9% |
| `mention_mismatch` | 1,664 | 51.6% | 71.9% |
| `cohort_or_exposure_context` | 255 | 50.2% | 65.5% |
| `mechanism_context` | 972 | 39.9% | 64.0% |

## Observations

- `common_word_mention` is rare but highly reliable. Examples include words
  such as `date`, `ten`, `his`, `balance`, and `monitor`.
- `family_mention_fanout` is a high precision failure signal. Most failures
  map broad family mentions such as `TNF`, `VEGF`, `PPAR`, `GSK3`, `CREB`,
  `ALP`, or `DGAT` to the wrong specific gene.
- `short_mention_risk` is a strong rule, especially when the short mention is
  an abbreviation that expands to the wrong domain.
- `mention_mismatch` has high recall for weak or bad edges, but it is not an
  automatic rejection rule because many biomedical abbreviations are legitimate
  synonyms.
- `method_or_reagent_context` is a strong precision signal. Common examples
  include antibodies, rabbit serum, culture media, assay reagents, inhibitors
  used as probes, and staining or detection contexts.
- `negation_or_hedging` remains useful. It catches explicit negative results,
  non-significant associations, uncertain causality, and inverse or protective
  findings.
- `adverse_or_risk_context` is broad. It catches many true adverse-event edges
  as well as false treatment and cohort/exposure edges, so it should be used as
  a routing flag rather than a reject flag.
- `treatment_context` is not a quality guarantee. In the treatment slice it
  mixes true treatment, supportive care, cell-line treatment, drug use in
  patients with a disease, and treatment of a different complication.
- The treatment predicate slice introduces many distinct failure modes:
  supportive-care context, cohort exposure, abbreviation expansion, disease as
  patient background, and assay-only anticancer effects.
- The chemical-gene mechanism slice is more often recoverable than the
  treatment slice when the exact mentions are correct. Direct expression,
  phosphorylation, promoter, inhibition, and protein-activity statements are
  often well supported.
- Chemical-gene failures are dominated by wrong normalization, inverse
  direction, and reagent/method context. Common examples include cell lines or
  study groups extracted as genes, gene symbols extracted as chemicals, and
  assay reagents such as blocking solutions or culture media being treated as
  mechanistic agents.
- The final protein-gene mechanism slice was dominated by normalization
  failures from ambiguous terms such as `same`, `PCa`, `ALP`, `Met`, `PND`,
  `hip`, and broad `TNF` mentions. A smaller fraction were valid direct
  mechanism or signaling edges.
- Batch 002 preserved the same broad pattern but with a slightly less severe
  failure rate for `short_mention_risk` and `mention_mismatch`. These tags are
  still the strongest high-recall routing signals for weak or bad rows.
- The batch 002 protein-disease tail exposed category and normalization
  artifacts where biologics, vaccines, amino acids, and reagents were sampled
  under the protein slice. Many valid biomedical statements were recoverable
  only after separating the mention-level claim from the normalized node.
- The batch 002 protein-gene mechanism tail confirmed that `same`, `PCa`,
  `TPA`, `Met`, `ASP`, and family labels such as `TNF` or `PPAR` need local
  expansion before accepting the normalized pair.
