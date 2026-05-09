---
marp: true
title: TMKP KGX Trust Assessment
description: Concrete false-positive analysis and recommendations for the 2026-04-21 TMKP KGX release
theme: default
paginate: true
size: 16:9
style: |
  section {
    font-size: 27px;
    color: #172033;
  }
  h1 {
    color: #102033;
    font-size: 43px;
  }
  h2 {
    color: #102033;
    font-size: 34px;
  }
  table {
    font-size: 18px;
  }
  .small {
    font-size: 22px;
  }
  .tiny {
    font-size: 17px;
  }
  .two-col {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 34px;
  }
  .callout {
    border-left: 8px solid #2563eb;
    background: #eff6ff;
    padding: 14px 18px;
  }
  .warn {
    border-left: 8px solid #b45309;
    background: #fff7ed;
    padding: 14px 18px;
  }
  .bad {
    border-left: 8px solid #b91c1c;
    background: #fef2f2;
    padding: 14px 18px;
  }
---

<!--
_class: lead
paginate: false
-->

# TMKP KGX Trust Assessment

Is the raw KG trustable?

Short answer: no. The false-positive rate is too high.

---

# The Answer

The raw TMKP KGX edges should not be treated as curated truth.

Across `6,000` manually reviewed edge/evidence rows:

| Manual review label | Rows | Share |
| --- | ---: | ---: |
| `supported` | 2,217 | 37.0% |
| `partially_supported` | 1,256 | 20.9% |
| `unsupported` | 2,498 | 41.6% |
| `unclear` | 29 | 0.5% |

<div class="bad">
The naive NLP edge is wrong or too broad in most reviewed rows.
</div>

---

# What Is Still Useful

The source evidence is often real text from PubMed or PMC.

The problem is usually downstream:

- the mention was normalized to the wrong node
- the predicate is too broad
- a list sentence produced cross-products
- a biomarker or assay became a causal edge
- a family-level molecule became a specific gene
- negation or uncertainty disappeared

TMKP is useful as an evidence index and review queue. It is not safe as a raw KG.

---

# What Was Compared

The audit sampled 10 edge slices.

Here, a slice just means a subject/predicate/object bucket, for example:

- gene -> disease, `contributes_to`
- chemical -> disease, treatment predicate
- chemical -> gene, mechanism predicate
- gene -> gene, mechanism predicate
- chemical -> phenotype
- protein -> disease

This is only a sampling label. It is not a biological term.

---

# Support By Slice

| Slice | Rows | Supported | Supported + partial |
| --- | ---: | ---: | ---: |
| Chemical -> phenotype, contributes | 450 | 62.4% | 75.6% |
| Gene -> phenotype | 500 | 49.6% | 71.2% |
| Chemical -> phenotype, treatment | 450 | 51.6% | 67.8% |
| Chemical -> gene mechanism | 900 | 40.8% | 62.3% |
| Chemical -> disease treatment | 900 | 36.3% | 59.4% |
| Gene -> disease contributes | 1,000 | 35.4% | 58.3% |
| Gene -> gene mechanism | 800 | 14.0% | 32.3% |

Even the better slices need review before use.

---

# Good Edges Exist

Examples that mostly match the evidence:

| Edge | Why it looked good |
| --- | --- |
| `ENG -> hereditary hemorrhagic telangiectasia` | Abstract says HHT is caused by mutations in `ENG` or `ALK1` |
| `PORCN -> focal dermal hypoplasia` | Direct Mendelian claim |
| `ZIC3 -> congenital heart malformation` | Loss-of-function / heterotaxy evidence |
| `GCK -> monogenic diabetes` | Explicit monogenic diabetes evidence |
| `SCN1A -> Febrile Seizure` | Common variants associated with febrile seizures |

The useful signal is real. The issue is precision.

---

# False Positives Are Easy To Find

These are not subtle curation disagreements.

A reviewer or agent can often catch the error by checking:

- the extracted mention string
- the surrounding sentence
- whether the abbreviation expands locally
- whether the normalized node name is actually in the text
- whether the sentence is a list, assay, cohort, or negated claim

The next slides show concrete examples.

---

# Gene-Disease False Positives

| KGX edge | What went wrong |
| --- | --- |
| `BCAR1 -> syndrome` | `Cas` came from `CRISPR/Cas9`; object `syndrome` is too vague |
| `RDH11 -> cancer` | Text supports expression in cancer cell lines, not disease causation |
| `SRY -> neoplasm` | `SRY` is a marker for tumor-cell origin, not a cancer driver |
| `SMC6 -> cancer` | Text is about `RAD18`; subject normalized to `SMC6` |
| `DEFA4 -> papilloma` | `HP-4` is likely a virus designation, not defensin `DEFA4` |
| `PAK4 -> Severe Dengue` | `DSS` means disease-specific survival, not dengue shock syndrome |

---

# Mendelian-Looking False Positives

| KGX edge | What went wrong |
| --- | --- |
| `CALR3 -> cardiomyopathy` | Evidence questions monogenic causality |
| `DNAJC6 -> dopa-responsive dystonia` | Multi-gene / movement-disorder list |
| `VPS35 -> dopa-responsive dystonia` | Same list-sentence cross-product issue |
| `SALL4 -> horizontal gaze palsy with progressive scoliosis` | Multiple genes and phenotypes listed together |
| `CNGB3 -> choroideremia` | Retinal-disease panel context, wrong specific object |
| `CYP24A1 -> distal renal tubular acidosis` | Differential list; `CYP24A1` belongs to another item |
| `NSUN2 -> autosomal recessive hypophosphatemic rickets` | Multi-case sequencing list cross-product |

---

# Drug-Disease False Positives

| KGX edge | What went wrong |
| --- | --- |
| `Givinostat -> Duane Syndrome` | Object mention was `duration` |
| `Zafirlukast -> kidney disorder` | Subjects without renal disease received zafirlukast |
| `Hydralazine -> thyroid disease` | Thyroid disease is a risk factor for hydralazine-induced AAV |
| `Aminohippuric acid -> neoplasm` | `PAH` likely means polycyclic aromatic hydrocarbons |
| `Bisphenol A -> cancer` as treatment | Evidence says data are lacking, not that BPA treats cancer |
| `Domperidone -> digestive system disorder` | Disease context plus cardiac adverse-effect discussion, not clean treatment |

---

# Rare-Disease Abbreviation Collisions

| KGX edge | Local meaning |
| --- | --- |
| `Azacitidine -> Miller-Dieker lissencephaly syndrome` | `MDS` means myelodysplastic syndrome |
| `Decitabine -> Miller-Dieker lissencephaly syndrome` | Same `MDS` collision |
| `Clopidogrel -> acute chest syndrome` | `ACS` often means acute coronary syndrome |
| `Clopidogrel -> acrocallosal syndrome` | Same `ACS`, different wrong rare disease |
| `Ticagrelor -> acute chest syndrome` | Cardiology `ACS` context |
| `Hydroxyurea -> Schnyder corneal dystrophy` | `SCD` means sickle cell disease |

This class of false positive is common and easy to spot with local context.

---

# False Rare-Disease Inclusions

| Edge | Why it is not the intended rare-disease signal |
| --- | --- |
| `Propofol -> syndrome` | Likely propofol infusion syndrome; object is too generic |
| `Dexamethasone -> acute respiratory distress syndrome` | Acquired critical illness, not Mendelian disease |
| `Metformin -> vitamin B12 deficiency` | Clinical adverse/metabolic context, not Mendelian |
| `Chloroquine -> severe acute respiratory syndrome` | Infectious-disease object passed a broad syndrome filter |
| `Rifaximin -> irritable bowel syndrome` | Useful treatment context, not rare inherited disease |
| `Tacrolimus -> posterior leukoencephalopathy syndrome` | Drug adverse-event syndrome |

---

# Phenotype False Positives

| KGX edge | What went wrong |
| --- | --- |
| `alteplase -> Edema` | `TPA-induced ear edema` uses phorbol ester, not alteplase |
| `Methyldopa -> Impaired Vision` | `AMD` means age-related macular degeneration |
| `GH1 -> Short stature` | Text is about growth hormone treatment, not `GH1` gene causation |
| `VEGFC -> Edema` | Generic `VEGF` mapped to a specific family member |
| `MAPT -> Cognitive impairment` | CSF tau biomarker context, not direct gene causation |
| `INS -> Edema` | Insulin/metabolic model context; edema is histopathology |
| `solution -> Edema` | Generic reagent/exposure artifact |

---

# Gene/Protein -> Phenotype False Positives

| KGX edge | What went wrong |
| --- | --- |
| `WDR46 -> Micrognathia` | Subject mention was `COL11A2` |
| `PHF1 -> Cognitive impairment` | Subject mention was `Syngap1` |
| `ADH1A -> Hypocalcemia` | `ADH1` means autosomal dominant hypocalcemia type 1 |
| `ASIP -> skeletal abnormality` | `Asp` is an amino-acid residue in an `FGFR1` variant |
| `COMP -> Gait ataxia` | `precursor` came from cerebellin precursor text |
| `TNFSF13B -> Edema` | Generic `TNF` normalized to a specific superfamily gene |
| `CD70 -> Edema` | Same generic `TNF` fan-out problem |

---

# Chemical -> Phenotype False Positives

| KGX edge | What went wrong |
| --- | --- |
| `Pentaerythritol tetranitrate -> Fever` | Subject mention `ten` came from "ten patients" |
| `Histidine -> Fever` | Subject mention `his` was a pronoun |
| `Histidine -> Vomiting` | Same pronoun problem |
| `Dextromethorphan -> Edema` | `DEX` meant dexamethasone |
| `solution -> Edema` | Generic experimental solution |
| `Acetaminophen -> Fever` | Patient had fever and took paracetamol; weak exposure context |

These are simple string/context errors, not hard biology.

---

# Pharmacology Model Readouts

Some rows are real experiments but not clinical phenotype assertions.

| KGX edge | What the text was really about |
| --- | --- |
| `Histamine -> Edema` | Rat paw edema model |
| `Formaldehyde -> Edema` | Formalin-induced paw edema |
| `Serotonin -> Edema` | 5-HT induced paw edema model |
| `Bradykinin -> Edema` | Mediator-induced edema model |
| `Capsaicin -> Edema` | Mouse ear edema model |
| `sodium oxybate -> Absence Seizure` | GHB-induced seizures in animal models |

These should not be read as patient-level KG facts without review.

---

# Chemical -> Gene False Positives

| KGX edge | What went wrong |
| --- | --- |
| `Pembrolizumab -> RPL17` | Object mention `PD-1`; useful target is `PDCD1` |
| `Pembrolizumab -> SPATA2` | Same `PD-1` collision |
| `Infliximab -> TNFSF18` | Generic `TNF` fanned out |
| `Infliximab -> CD40LG` | Same `TNF` fan-out |
| `Celecoxib -> MT-CO2` | `COX2` should mean `PTGS2` here |
| `Methyldopa -> CXCR4` | `AMD` came from AMD3100, not alpha-methyldopa |
| `Cefaclor -> CCL4` | `CCL` is chemokine prefix, not cefaclor |
| `Dextromethorphan -> IL6` | `Dex` usually meant dexamethasone |

---

# More Mechanism False Positives

| KGX edge | What went wrong |
| --- | --- |
| `Snail, unspecified -> CDH1` | `Snail` is a transcription factor, not a chemical |
| `solution -> ALB` | Buffer/protocol text became a mechanism edge |
| `bevacizumab -> VEGFB` | Generic `VEGF`, not explicit VEGF-B |
| `bevacizumab -> VEGFC` | Same VEGF-family fan-out |
| `nivolumab -> RPL17` | `PD-1` collision |
| `nivolumab -> SPATA2` | `PD-1` collision |
| `IL10 -> GSR` | Object mention `Gr-1`, not `GSR` |
| `MM-121 -> S1PR5` | Relevant text was `NRG1`, not `S1PR5` |

---

# Family Mentions Create Many Bad Edges

| Mention | Normalized objects |
| --- | --- |
| `TNF` | `TNF`, `TNFSF12`, `TNFSF13`, `TNFSF13B`, `TNFSF18`, `TNFSF4`, `TNFSF8`, `TNFSF9`, `CD40LG`, `CD70`, `EDA` |
| `VEGF` | `VEGFA`, `VEGFB`, `VEGFC`, `VEGFD` |
| `PPAR` | `PPARA`, `PPARD`, `PPARG` |
| `calcineurin` | `PPP3CA`, `PPP3CB`, `PPP3CC`, `PPP3R1`, `PPP3R2` |
| `PD-1` | `PDCD1`, `RPL17`, `SPATA2` |
| `COX2` | `PTGS2`, `MT-CO2` |

This is a systematic KG construction problem.

---

# High Evidence Count Does Not Save It

Repeated evidence can repeat the same normalization error.

Examples:

- generic `TNF` gets counted across many TNF-superfamily nodes
- generic `VEGF` becomes `VEGFA/B/C/D`
- `PD-1` becomes `PDCD1`, but also `RPL17` and `SPATA2`
- `COX2` becomes both `PTGS2` and mitochondrial `MT-CO2`

High count means "frequently extracted." It does not mean "curated."

---

# Why Agents Find These Quickly

The checks are mechanical:

1. Compare mention text with normalized node label.
2. Check whether short mention has a local expansion.
3. Look for list sentences with several genes and diseases.
4. Detect words like "questionable", "not", "failed", "unlikely".
5. Detect assay/model words: paw edema, cell line, marker, serum, buffer.
6. Detect family terms: TNF, VEGF, PPAR, PD-1, COX2.

That is enough to find many false positives before expert curation.

---

<!--
_class: lead
paginate: false
-->

# Technical Strategy

Use agents and deterministic rules as a QA layer before anyone trusts the KG.

---

# Current Runnable Framework

The rule framework is standalone Python.

```sh
uv run python scripts/export_edge_audit.py
uv run python scripts/validate_edge_audit.py
uv run python scripts/init_edge_audit_evaluation.py
uv run python scripts/score_edge_audit_rules.py
```

Batch-aware export:

```sh
uv run python scripts/export_edge_audit.py \
  --batch-id tmkp-2026-04-21-edge-audit-batch-002 \
  --exclude-audit audits/tmkp_edge_audit_2026_04_21_batch_001.csv \
  --candidate-multiplier 20
```

---

# Rule Results: Obvious FP Signals

Across `6,000` manual reviews:

| Rule tag | Tagged rows | Failure precision | Weak/bad precision |
| --- | ---: | ---: | ---: |
| `common_word_mention` | 37 | 94.6% | 100.0% |
| `short_mention_risk` | 1,912 | 70.7% | 85.6% |
| `family_mention_fanout` | 338 | 67.5% | 94.1% |
| `method_or_reagent_context` | 159 | 64.2% | 78.6% |
| `negation_or_hedging` | 199 | 63.3% | 77.9% |
| `mention_mismatch` | 3,258 | 55.7% | 75.1% |

The raw KG has easy-to-detect error signatures.

---

# Rule Results: Recall

| Rule tag | Failure recall |
| --- | ---: |
| `mention_mismatch` | 71.9% |
| `short_mention_risk` | 53.5% |
| `mechanism_context` | 34.0% |
| `model_or_assay_context` | 32.8% |
| `treatment_context` | 26.4% |
| `adverse_or_risk_context` | 26.0% |
| `biomarker_or_expression_context` | 25.0% |

The best tags do not catch everything, but they catch enough to prove raw trust is unsafe.

---

# Mention Mismatch Means At Risk

`mention_mismatch` is not an automatic reject rule.

It means: do not trust this edge without local context.

| Case | Example | What to do |
| --- | --- | --- |
| Clear false positive | `ten` -> pentaerythritol tetranitrate | quarantine |
| Clear false positive | `his` -> histidine | quarantine |
| Likely false positive | `BMD` -> vitelliform macular dystrophy 2 | require local expansion |
| Likely false positive | `ACS` -> acrocallosal syndrome | require local expansion |
| Valid abbreviation | `MTX` -> methotrexate | keep if context supports it |
| Valid abbreviation | `G-CSF` -> filgrastim | keep if context supports it |
| Partial mismatch | `VEGF` -> `VEGFA` | require explicit VEGF-A support |

---

# Why Mention Mismatch Is Still Useful

Across `6,000` manually reviewed rows:

- `mention_mismatch` caught `71.9%` of manual failures
- failure precision was only `55.7%`
- weak-or-bad precision was `75.1%`

So it is a high-recall QA signal.

<div class="callout">
Use it to route rows to an agent or reviewer. Do not use it alone to delete every edge.
</div>

---

# What To Gate Before Use

Hard quarantine:

- common-word subject/object mentions
- known abbreviation collisions
- family fan-out to unsupported specific genes
- negated or hedged causality
- method/protocol/reagent context
- list-sentence cross-products

Review queue:

- short mentions with plausible expansions
- broad disease or symptom objects
- model or assay readouts
- biomarker/expression context
- treatment/cohort/adverse context with weak predicate fit

---

# Concrete QA Output

For each TMKP release, generate:

| File | Purpose |
| --- | --- |
| promoted candidates | rows with strong mention, predicate, and context fit |
| likely false positives | high-precision error signatures |
| abbreviation collisions | short mentions requiring local expansion |
| family fan-out | TNF/VEGF/PPAR/PD-1/COX2 style cases |
| model/assay rows | useful evidence but not patient-level facts |
| manual-review sample | measured precision by slice |

This answers "what can we trust?" with evidence, not vibes.

---

# What Not To Do

Do not:

- accept every normalized edge as a curated fact
- treat evidence count as validation
- mix true treatment, cohort exposure, and adverse event as one signal
- treat HPO symptom objects as clean disease phenotypes
- treat family-level molecular mentions as specific gene edges
- ignore negation and list context

These are the main causes of false positives in the current audit.

---

# Better Operating Model

1. Start with TMKP as candidate evidence.
2. Run deterministic QA tags.
3. Have agents inspect the highest-risk rows and summarize examples.
4. Estimate precision by slice.
5. Promote only high-fit rows.
6. Keep rejected rows with reasons.

The output is not one KG. It is a set of trust tiers.

---

# Recommended Trust Tiers

| Tier | Meaning |
| --- | --- |
| Trust after review | exact mention match, direct claim, no obvious context problem |
| Candidate | useful text, but predicate or node may need checking |
| Evidence only | text is useful, edge is too broad or shifted |
| Quarantine | likely false positive from normalization or context |
| Drop | common-word, wrong entity type, or unsupported cross-product |

This is the right product shape for a naive NLP KG.

---

# Bottom Line

TMKP has useful biomedical evidence.

But the raw KG edge layer is not trustable as-is.

The false positives are too frequent, too systematic, and easy to find with agentic review plus simple deterministic rules.

Use TMKP as a candidate/evidence index. Do not use it as a curated KG without QA.
