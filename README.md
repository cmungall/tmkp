# TMKP KGX DuckDB analysis

This repository contains a small, reproducible analysis of the latest TMKP KGX release from the NCATS Translator KGX storage service.

The large KGX data files are not committed. The notebook expects a local DuckDB database at:

```text
downloads/tmkp/2026_04_21/tmkp.duckdb
```

## Included artifacts

- `scripts/load_tmkp_duckdb.sql` loads extracted KGX JSONL into DuckDB.
- `notebooks/tmkp_category_summary.ipynb` summarizes nodes, edges, sources, qualifiers, evidence, and category flows.
- `notebooks/tmkp_category_summary.html` is the rendered notebook.

## Data release

Latest release inspected:

```text
https://kgx-storage.rtx.ai/releases/tmkp/2026_04_21/
```

Release metadata:

```text
source: tmkp
source_version: tmkp-2023-03-05
transform_version: 6dadae40
node_norm_version: 2025sep1
biolink_version: 4.3.6
release_version: 2026_04_21
```

## Reproduce locally

Install dependencies with `uv`:

```sh
uv sync
```

Download and extract the KGX payload:

```sh
mkdir -p downloads/tmkp/2026_04_21/kgx

curl -fsSL -o downloads/tmkp/2026_04_21/latest-release.json \
  https://kgx-storage.rtx.ai/releases/tmkp/latest-release.json

curl -fsSL -o downloads/tmkp/2026_04_21/graph-metadata.json \
  https://kgx-storage.rtx.ai/releases/tmkp/latest/graph-metadata.json

curl -fL --retry 3 --continue-at - \
  -o downloads/tmkp/2026_04_21/tmkp.tar.zst \
  https://kgx-storage.rtx.ai/releases/tmkp/latest/tmkp.tar.zst

tar --zstd -xf downloads/tmkp/2026_04_21/tmkp.tar.zst \
  -C downloads/tmkp/2026_04_21/kgx
```

Load DuckDB:

```sh
duckdb downloads/tmkp/2026_04_21/tmkp.duckdb \
  < scripts/load_tmkp_duckdb.sql
```

Execute the notebook:

```sh
uv run python -m jupyter nbconvert --to notebook --execute --inplace \
  notebooks/tmkp_category_summary.ipynb \
  --ExecutePreprocessor.timeout=900
```

Render HTML:

```sh
uv run python -m jupyter nbconvert --to html \
  notebooks/tmkp_category_summary.ipynb \
  --output tmkp_category_summary.html \
  --output-dir notebooks
```

## Quick DuckDB examples

```sh
duckdb -readonly downloads/tmkp/2026_04_21/tmkp.duckdb
```

```sql
SELECT category[1] AS primary_node_category, count(*) AS nodes
FROM nodes
GROUP BY 1
ORDER BY nodes DESC;

SELECT
  subject_primary_category,
  predicate,
  object_primary_category,
  count(*) AS edges
FROM edges_enriched
GROUP BY 1, 2, 3
ORDER BY edges DESC
LIMIT 25;
```

## Notes

Initial checks found that actual KGX counts match `graph-metadata.json`: `32,276` nodes and `1,861,988` edges. The archive has no duplicate node IDs or edge IDs and no dangling edge endpoints. The rendered notebook includes grouped summaries and quality checks by category.

## Preliminary evidence audit

TMKP edges carry nested study-result evidence under `has_supporting_studies`. For abstract-labeled snippets, a sample checked against PubMed/PMC showed that `supporting_text` is a literal source-text span rather than a generated paraphrase. The harder quality question is whether the normalized KGX edge claim is supported by that span.

For gene/protein to disease/phenotype edges, the largest relation slice is:

| Subject category | Object category | Predicate | Qualified predicate | Edges |
| --- | --- | --- | --- | ---: |
| `biolink:Gene` | `biolink:Disease` | `biolink:affects` | `biolink:contributes_to` | 398,321 |
| `biolink:Gene` | `biolink:PhenotypicFeature` | `biolink:affects` | `biolink:contributes_to` | 7,753 |

Manual inspection of sampled examples shows that good edges often have directly useful evidence, but bad edges are common enough that downstream use should treat TMKP edges as text-mined assertions requiring filtering or review.

### Examples where the claim mostly matches the evidence

| Edge | Evidence read |
| --- | --- |
| `ENG -> hereditary hemorrhagic telangiectasia` | The abstract states that hereditary hemorrhagic telangiectasia is caused by mutations in `ENG` or `ALK1`, so the edge is directly supported. |
| `PKD1 -> polycystic kidney disease` | The abstract links polycystin/PKD proteins to polycystic kidney disease. This supports an association, though the text is broader than `PKD1` alone. |
| `ZEB1 -> pediatric osteosarcoma` | The abstract reports ZEB1 upregulation in osteosarcoma cells and suppression of proliferation, migration, and invasion after ZEB1 inhibition. |
| `HMGB2 -> glioma` | The abstract describes a miRNA-HMGB2 signaling axis regulating glioma growth and metastasis. |
| `IRF8 -> B-cell acute lymphoblastic leukemia` | The abstract says PU.1/IRF8 double-deficient mice developed pre-B-cell acute lymphoblastic leukemia. |

### Likely bad or over-generalized edges after reading the full abstracts

| KGX edge | Mention spans | PubMed context | Assessment |
| --- | --- | --- | --- |
| `BCAR1 -> syndrome` | subject mention `Cas`; object mention `syndrome` | [PMID:29437009](https://pubmed.ncbi.nlm.nih.gov/29437009/) is about Drosophila `Nulp1` femur development and a phenotype resembling Stuve-Weidemann syndrome. | The largest practical problem is the object: `syndrome` is too vague to be actionable. There is also a secondary subject issue because `Cas` came from `CRISPR/Cas9` and was normalized to `BCAR1`. |
| `RDH11 -> cancer` | subject mention `RalR1`; object mention `cancer` | [PMID:14674758](https://pubmed.ncbi.nlm.nih.gov/14674758/) characterizes retinal reductase/RalR1/RDH11 and reports expression in normal tissues and cancer cell lines. | The subject normalization is plausible, but the text supports expression in cancer cell lines, not that RDH11 contributes to cancer. |
| `SRY -> neoplasm` | subject mention `SRY`; object mention `tumor` | [PMID:19033127](https://pubmed.ncbi.nlm.nih.gov/19033127/) uses SRY as a marker to track tumor-cell origin in female mice. | The abstract is about metastasis tracking; SRY is a marker/control, not a causal disease gene. |
| `SMC6 -> cancer` | subject mention `RAD18`; object mention `cancer` | [PMID:31432163](https://pubmed.ncbi.nlm.nih.gov/31432163/) reports RAD18 effects in cervical cancer cells. | The biomedical statement is useful for RAD18, but the subject is normalized to SMC6, so the finalized edge is wrong. |
| `DEFA4 -> papilloma` | subject mention `HP-4`; object mention `papilloma` | [PMID:217936](https://pubmed.ncbi.nlm.nih.gov/217936/) discusses HPV-3/HPV-4 and epidermodysplasia verruciformis. | Likely abbreviation/identifier collision: `HP-4` appears to be a virus designation, not defensin `DEFA4`. |
| `PAK4 -> Severe Dengue` | subject mention `PAK4`; object mention `DSS` | [PMID:26614788](https://pubmed.ncbi.nlm.nih.gov/26614788/) studies PAK4 expression as a prognostic factor in gastric cancer; `DSS` means disease-specific survival. | Subject is correct, but `DSS` was normalized to Severe Dengue. The useful edge would be about gastric cancer/prognosis, not dengue. |

### Preliminary error taxonomy

1. **Acronym and short-token normalization errors**
   - Examples: `DSS` mapped to Severe Dengue; `Cas` from `CRISPR/Cas9` mapped to `BCAR1`.
   - Detection signal: extracted mention length is very short, all caps/mixed abbreviation, and normalized label is semantically distant from surrounding text.

2. **Wrong normalized subject despite a useful source claim**
   - Example: text is about `RAD18` in cervical cancer, but the edge subject is `SMC6`.
   - Detection signal: extracted subject mention string does not match the normalized node name, synonyms, or equivalent identifiers.

3. **Over-broad disease/object normalization**
   - Examples: `syndrome`, `cancer`, `neoplasm`.
   - Detection signal: object node is a high-degree generic MONDO term, while the abstract names a more specific disease or experimental context. In many cases this is enough to make the edge unhelpful even if the subject mention is reasonable.

4. **Marker/control relations mistaken for causal disease contribution**
   - Example: SRY used as a sex-chromosome marker in tumor tracking.
   - Detection signal: local dependency/context verbs include "marker", "detected", "control", "expression examined", or experimental tracking language rather than disease mechanism language.

5. **Cell-line or expression context promoted to disease contribution**
   - Example: RDH11/RalR1 expression in cancer cell lines converted to `contributes_to cancer`.
   - Detection signal: evidence says "expressed in", "cell line", "tissues", or assay context without perturbation, association, mutation, prognosis, or mechanism.

6. **Model-organism phenotype mapped too directly to human disease**
   - Example: Drosophila Nulp1 femur phenotype resembling a human syndrome.
   - Detection signal: source mentions a model organism plus "similar to", "model for", or "resembling" rather than a direct human gene-disease association.

### Mendelian candidate scan

A first pass scanned the `Gene -> Disease` `biolink:affects` / `biolink:contributes_to` slice for Mendelian-like signals in the evidence text. The heuristic score used:

- variant/inheritance terms such as `mutation`, `variant`, `loss-of-function`, `homozygous`, `de novo`, `autosomal`, `familial`, `hereditary`, `congenital`
- causal/association terms such as `caused by`, `due to`, `responsible for`, `associated with`, `linked to`
- explicit Mendelian terms such as `OMIM`, `monogenic`, `Mendelian`, `proband`, `pedigree`, `consanguineous`
- direct lexical presence of the normalized gene and disease labels in the supporting text
- a penalty for very generic object labels such as `cancer`, `neoplasm`, `syndrome`, `disease`, and `disorder`

Score distribution over 398,321 gene-disease edges:

| Score | Edges | Interpretation |
| ---: | ---: | --- |
| 7 | 317 | Highest-signal; usually explicit variant/causal/Mendelian text with both labels present. |
| 6 | 823 | Very strong, but some generic-object and list-sentence errors remain. |
| 5 | 8,359 | Good candidate pool for review. |
| 4 | 21,054 | Broader recall-oriented pool; more generic disease labels and weaker relation text. |
| 3 or less | 367,768 | Lower confidence for Mendelian curation without additional filtering. |

Useful high-scoring candidates from manual inspection:

| Edge | PubMed/PMC | Assessment |
| --- | --- | --- |
| `PORCN -> focal dermal hypoplasia` | [PMID:26843121](https://pubmed.ncbi.nlm.nih.gov/26843121/) | Strong direct Mendelian claim: disease caused by mutations in `PORCN`. |
| `ZIC3 -> congenital heart malformation` | [PMID:21858219](https://pubmed.ncbi.nlm.nih.gov/21858219/) | Strong claim for loss of function in `ZIC3` causing X-linked heterotaxy / congenital heart malformation. |
| `KIF15 -> thrombocytopenia` | [PMID:28150392](https://pubmed.ncbi.nlm.nih.gov/28150392/) | Strong consanguineous-family/loss-of-function style evidence. |
| `RIMS1 -> inherited retinal dystrophy` | [PMID:17237123](https://pubmed.ncbi.nlm.nih.gov/17237123/) | Strong inherited retinal dystrophy phrasing. |
| `SLCO2A1 -> primary hypertrophic osteoarthropathy` | [PMID:22197487](https://pubmed.ncbi.nlm.nih.gov/22197487/) | Strong causative-mutation evidence. |
| `DNMT1 -> hereditary sensory and autonomic neuropathy type 1` | [PMID:25033457](https://pubmed.ncbi.nlm.nih.gov/25033457/) | Strong direct causal statement with OMIM-like disease context. |
| `GCK -> monogenic diabetes` | [PMID:21437567](https://pubmed.ncbi.nlm.nih.gov/21437567/) | Strong explicit monogenic diabetes evidence. |
| `SPATA7 -> retinal degeneration` | [PMID:28481129](https://pubmed.ncbi.nlm.nih.gov/28481129/) | Strong title-level evidence for a homozygous mutation causing autosomal recessive retinal degeneration. |
| `EFTUD2 -> mandibulofacial dysostosis` | [PMID:23879989](https://pubmed.ncbi.nlm.nih.gov/23879989/) | Strong direct statement that `EFTUD2` mutations cause mandibulofacial dysostosis. |
| `FASTKD2 -> mitochondrial encephalomyopathy` | [PMID:26370583](https://pubmed.ncbi.nlm.nih.gov/26370583/) | Strong explicit Mendelian disease evidence. |

High-scoring false positives or cautionary cases:

| Edge | PubMed/PMC | Likely issue |
| --- | --- | --- |
| `CALR3 -> cardiomyopathy` | [PMID:29988065](https://pubmed.ncbi.nlm.nih.gov/29988065/) | Negation/hedging: the evidence says it is questionable that `CALR3` variants are a monogenic cause of cardiomyopathy. The raw KGX edge has no negation qualifier; it is encoded as `biolink:affects` with `qualified_predicate: biolink:contributes_to`. |
| `DNAJC6 -> dopa-responsive dystonia`, `VPS35 -> dopa-responsive dystonia`, `ATP13A2 -> dopa-responsive dystonia` | [PMID:31779813](https://pubmed.ncbi.nlm.nih.gov/31779813/) | List-sentence problem: the abstract discusses multiple Parkinsonism genes and movement-disorder categories; individual gene-object pairings can be over-assigned. |
| `SALL4 -> horizontal gaze palsy with progressive scoliosis`, `CHN1 -> horizontal gaze palsy with progressive scoliosis` | [PMID:25173900](https://pubmed.ncbi.nlm.nih.gov/25173900/) | Coordinated-list problem: several genes and several phenotypes are listed together; not every gene maps to every phenotype. |
| `CNGA3 -> retinitis pigmentosa`, `CNGB3 -> choroideremia` | [PMID:28035529](https://pubmed.ncbi.nlm.nih.gov/28035529/) | Panel/list context: genes and inherited retinal disease categories co-occur, but the specific normalized object may be wrong. |
| `CYP24A1 -> distal renal tubular acidosis` | [PMID:30470867](https://pubmed.ncbi.nlm.nih.gov/30470867/) | Differential/list context: `CYP24A1` belongs to one nephrocalcinosis cause, while distal renal tubular acidosis is another listed cause. |
| `NSUN2 -> autosomal recessive hypophosphatemic rickets` | [PMID:24102521](https://pubmed.ncbi.nlm.nih.gov/24102521/) | Multi-case sequencing list: the sentence contains several genes and diagnoses; the edge likely cross-products unrelated list items. |

Additional taxonomy suggested by this scan:

7. **Coordinated gene-list / disease-list cross-products**
   - Several genes and diseases appear in one sentence, and extraction creates edges between non-corresponding pairs.
   - Detection signal: multiple comma-separated genes and multiple comma-separated diseases in the same evidence span.

8. **Negated or hedged Mendelian causality**
   - Evidence contains Mendelian keywords but says the causal claim is doubtful, absent, or only suspected.
   - Detection signal: terms such as "questionable", "not associated", "failed to", "unlikely", "may", "suspect", or "candidate" near causal language.

9. **Panel, review, or differential-diagnosis context**
   - Gene and disease names co-occur in a broad review/panel/differential list rather than a direct assertion.
   - Detection signal: section/title contains "panel", "review", "differential", "spectrum", or "genes including"; evidence has several semicolon/comma-separated alternatives.

### Candidate filters to try next

- Flag edges where the extracted subject/object mention is shorter than 4 characters.
- Flag edges where the mention string has low lexical similarity to the normalized node name and no obvious synonym/equivalent match.
- Down-rank or suppress generic disease objects such as `cancer`, `neoplasm`, and especially `syndrome` unless the source text lacks a more specific disease mention.
- Separate evidence categories: direct causation/mutation, expression/prognosis, model organism, marker/control, and cell-line-only context.
- Use higher evidence count cautiously: repeated evidence can amplify a systematic normalization error.
- For Mendelian candidates, require direct gene-disease alignment in the same clause when evidence contains multiple genes and multiple diseases.
- Add a negation/hedging pass before accepting high-scoring mutation-language edges.
