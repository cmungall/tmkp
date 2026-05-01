---
marp: true
title: TMKP KGX Audit Findings
description: Qualitative audit findings for the 2026-04-21 TMKP KGX release
theme: default
paginate: true
size: 16:9
---

<!--
_class: lead
paginate: false
-->

# TMKP KGX Audit Findings

Qualitative review of evidence-backed text-mined edges

2026-04-21 TMKP KGX release

---

# What Was Audited

- Latest release inspected: `2026_04_21`
- `32,276` nodes
- `1,861,988` edges
- Evidence stored in `has_supporting_studies`
- Loaded into DuckDB for grouped review and sampling

---

# Main Takeaway

TMKP is best treated as a text-mined assertion and evidence index.

It contains many useful candidate edges, but the normalized KGX edge should not be consumed as curated truth without stratification or review.

---

# Evidence Quality

- `supporting_text` is usually literal source text
- PubMed/PMC checks found source text spans, not generated paraphrases
- The hard problem is not evidence hallucination
- The hard problem is whether normalization and predicate semantics match the evidence

---

# High-Value Signals Are Present

- Gene-disease: `PORCN -> focal dermal hypoplasia`
- Gene/phenotype: `SCN1A -> Febrile Seizure`
- Drug/disease: colchicine/familial Mediterranean fever
- Drug/phenotype: ondansetron/nausea and vomiting
- Mechanism: EGFR inhibitors, HER2/trastuzumab, IL6/tocilizumab

---

# Dominant Failure Mode

Normalization errors dominate.

- Short mentions: `ACS`, `MDS`, `SCD`, `DSS`
- Common words: `his`, `ten`, `duration`
- Drug/gene collisions: `DEX`, `CCL`, `AMD`, `ADH1`, `Asp`
- Some short mentions are valid in context, so this is a review flag, not an automatic reject

---

# Family Terms Become Specific Edges

Family-level mentions often fan out to many specific nodes.

| Mention | Normalized objects |
| --- | --- |
| `TNF` | `TNF`, `TNFSF*`, `CD40LG`, `CD70`, `EDA` |
| `VEGF` | `VEGFA`, `VEGFB`, `VEGFC`, `VEGFD` |
| `PPAR` | `PPARA`, `PPARD`, `PPARG` |
| `PD-1` | `PDCD1`, `RPL17`, `SPATA2` |
| `COX2` | `PTGS2`, `MT-CO2` |

---

# Predicate Semantics Are Broad

`treats_or_applied_or_studied_to_treat`

- true treatment
- trial context
- cohort exposure
- weak "used in patients with" evidence

`contributes_to`

- adverse event
- risk factor
- teratogen
- true causation

---

# Mechanism Edges Are Coarse

Chemical/drug to gene/protein:

- `587,444` edges
- all `biolink:affects`
- all `qualified_predicate=biolink:causes`
- no SemMed support

Gene/protein to gene/protein:

- `359,704` edges
- same predicate/qualifier pattern
- includes direct regulation, pathway context, biomarkers, and family fan-out

---

# Phenotype Findings

- No direct `Disease -> PhenotypicFeature` edges
- No reverse `PhenotypicFeature -> Disease` edges
- Phenotype edges are mostly:
  - chemical/drug -> HPO
  - gene/protein -> HPO

Common HPO objects such as edema, fever, pain, vomiting, and cognitive impairment mix treatment targets, adverse effects, disease manifestations, and assay readouts.

---

# Negation And Hedging

Negation is not reliably represented in the normalized edge.

Example:

`CALR3 -> cardiomyopathy`

The evidence questions monogenic causality, but the KGX edge has no negation qualifier and is encoded as a positive `contributes_to` assertion.

---

# Evidence Count Caveat

High evidence count can amplify systematic errors.

Examples:

- `TNF` fan-out to TNF-superfamily genes
- `VEGF` cross-products
- `PD-1 -> RPL17/SPATA2`
- `COX2 -> MT-CO2`

Repeated evidence is not the same as validated specificity.

---

# Practical Use Pattern

Do not use the full KGX edge set as a curated KG.

Use it as stratified review queues:

- likely useful direct treatment
- useful adverse/risk edges
- Mendelian candidate edges
- mechanism candidates
- normalization-risk edges
- model/assay-only edges
- biomarker/cohort context edges

---

# Review Taxonomy

Core recurring buckets:

- short mention or abbreviation risk
- generic disease or phenotype object
- family-level molecular mention
- model or assay context
- biomarker or expression context
- list/cross-product context
- negation or hedging
- weak exposure/cohort context

---

# Best Next Step

Keep qualitative examples, but make the taxonomy executable.

Export deterministic flags:

- short mention
- family mention fan-out
- generic object
- negation/hedging
- model/assay context
- treatment language
- adverse/risk language
- biomarker/cohort context

Then estimate precision by stratum.

---

<!--
_class: lead
paginate: false
-->

# Summary

TMKP has real evidence and useful candidate edges.

The main quality challenge is edge normalization and semantic overloading, not missing source text.

Use it as an evidence-backed triage layer.
