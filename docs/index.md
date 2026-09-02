# TMKP KGX Trust Assessment

This site summarizes a manual and deterministic QA audit of the TMKP KGX
release `2026_04_21`.

[View the trust assessment slides](slides/tmkp_analysis_recommendations.html){ .md-button }
[View the audit findings slides](slides/tmkp_audit_findings.html){ .md-button }

## Bottom line

The raw TMKP KGX edge layer is **not trustable as curated truth**.

The evidence text is often useful, but the normalized edge is too often wrong,
too broad, or semantically shifted. The practical use is as an evidence-backed
candidate index plus QA/review queues.

## Audit scope

| Item | Value |
| --- | ---: |
| TMKP nodes | 32,276 |
| TMKP edges | 1,861,988 |
| Manual audit batches | 2 |
| Manual review rows | 6,000 |
| Distinct edges reviewed | 6,000 |
| Batch overlap | 0 edge IDs |

## Manual review result

| Manual review label | Rows | Share |
| --- | ---: | ---: |
| `supported` | 2,217 | 37.0% |
| `partially_supported` | 1,256 | 20.9% |
| `unsupported` | 2,498 | 41.6% |
| `unclear` | 29 | 0.5% |

`supported` means the evidence text supports the normalized edge and predicate.
`partially_supported` means the text supports a weaker, broader, or related
claim. Those rows may still be useful, but should not be consumed as clean KG
facts without repair or review.

## Main finding

False positives are frequent and systematic. Many are easy to find with simple
agentic checks:

- Compare extracted mention text to normalized node names.
- Expand short local abbreviations.
- Detect common words such as `his`, `ten`, `duration`, and `solution`.
- Detect family-level molecular mentions such as `TNF`, `VEGF`, `PPAR`,
  `PD-1`, and `COX2`.
- Detect negation, hedging, list sentences, model systems, and method/reagent
  context.

## Site map

- [Trust Assessment](trust-assessment.md): the core answer to whether the KG is
  trustable.
- [False Positive Examples](false-positives.md): concrete bad edges found in
  the audit.
- [Deterministic QA](deterministic-qa.md): what the scripts check and how to
  interpret the tags.
- [Recommendations](recommendations.md): how to use TMKP safely.
- [Artifacts](artifacts.md): tracked audit/evaluation files and commands.
- [Slides](slides.md): both rendered Marp decks.
