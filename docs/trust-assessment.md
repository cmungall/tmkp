# Trust Assessment

## Is the KG trustable?

Not as a raw KG.

TMKP should be treated as a text-mined assertion and evidence index. It is a
good source of candidates, but it is not a curated knowledge graph without a QA
layer.

## Why not?

The audit found that many source snippets are real biomedical text, but the
normalized KGX edge often does not match the snippet.

Common failure modes:

| Failure mode | What happens |
| --- | --- |
| Wrong normalized subject | Text is about one entity, edge subject is another. |
| Wrong normalized object | Abbreviation or short text span maps to the wrong disease, gene, or chemical. |
| Predicate too broad | Treatment, exposure, risk, assay, and cohort context collapse into one predicate. |
| Family fan-out | `TNF`, `VEGF`, `PPAR`, `PD-1`, or `COX2` becomes many specific nodes. |
| List cross-products | Sentences with many genes and diseases create pairings not asserted by the text. |
| Negation or hedging lost | Evidence says "not associated" or "questionable", but edge is positive. |
| Model/assay context | Animal or cell-line assay readouts look like clinical assertions. |

## Support by sampled slice

Here, a slice is just a subject/predicate/object bucket used for audit sampling,
for example gene -> disease or chemical -> phenotype.

| Slice | Rows | Supported | Supported + partial |
| --- | ---: | ---: | ---: |
| Chemical -> phenotype, contributes | 450 | 62.4% | 75.6% |
| Gene -> phenotype | 500 | 49.6% | 71.2% |
| Chemical -> phenotype, treatment | 450 | 51.6% | 67.8% |
| Chemical -> gene mechanism | 900 | 40.8% | 62.3% |
| Chemical -> disease treatment | 900 | 36.3% | 59.4% |
| Gene -> disease contributes | 1,000 | 35.4% | 58.3% |
| Chemical -> disease contributes | 600 | 30.0% | 56.3% |
| Protein -> disease | 200 | 35.0% | 54.0% |
| Protein -> gene mechanism | 200 | 23.0% | 44.5% |
| Gene -> gene mechanism | 800 | 14.0% | 32.3% |

Even the better slices need QA before use. The gene -> gene mechanism slice is
especially noisy.

## What remains valuable?

Good edges do exist. Examples include:

| Edge | Why it looked good |
| --- | --- |
| `ENG -> hereditary hemorrhagic telangiectasia` | Abstract says HHT is caused by mutations in `ENG` or `ALK1`. |
| `PORCN -> focal dermal hypoplasia` | Direct Mendelian claim. |
| `ZIC3 -> congenital heart malformation` | Loss-of-function / heterotaxy evidence. |
| `GCK -> monogenic diabetes` | Explicit monogenic diabetes evidence. |
| `SCN1A -> Febrile Seizure` | Common variants associated with febrile seizures. |
| `Colchicine -> familial Mediterranean fever` | Evidence describes colchicine as mainstay treatment. |
| `Ondansetron -> Nausea and vomiting` | Evidence describes use for chemotherapy-associated nausea and vomiting. |

The right product is not "use all edges" or "discard TMKP." It is trust-tiered
candidate evidence.
