# False Positive Examples

These examples are the clearest reason the raw KG should not be consumed as
curated truth.

## Gene-disease false positives

| KGX edge | What went wrong |
| --- | --- |
| `BCAR1 -> syndrome` | `Cas` came from `CRISPR/Cas9`; object `syndrome` is too vague. |
| `RDH11 -> cancer` | Text supports expression in cancer cell lines, not disease causation. |
| `SRY -> neoplasm` | `SRY` is a marker for tumor-cell origin, not a cancer driver. |
| `SMC6 -> cancer` | Text is about `RAD18`; subject normalized to `SMC6`. |
| `DEFA4 -> papilloma` | `HP-4` is likely a virus designation, not defensin `DEFA4`. |
| `PAK4 -> Severe Dengue` | `DSS` means disease-specific survival, not dengue shock syndrome. |

## Mendelian-looking false positives

| KGX edge | What went wrong |
| --- | --- |
| `CALR3 -> cardiomyopathy` | Evidence questions monogenic causality. |
| `DNAJC6 -> dopa-responsive dystonia` | Multi-gene / movement-disorder list. |
| `VPS35 -> dopa-responsive dystonia` | Same list-sentence cross-product issue. |
| `SALL4 -> horizontal gaze palsy with progressive scoliosis` | Several genes and phenotypes listed together. |
| `CNGB3 -> choroideremia` | Retinal-disease panel context, wrong specific object. |
| `CYP24A1 -> distal renal tubular acidosis` | Differential list; `CYP24A1` belongs to another item. |
| `NSUN2 -> autosomal recessive hypophosphatemic rickets` | Multi-case sequencing list cross-product. |

## Drug-disease false positives

| KGX edge | What went wrong |
| --- | --- |
| `Givinostat -> Duane Syndrome` | Object mention was `duration`. |
| `Zafirlukast -> kidney disorder` | Subjects without renal disease received zafirlukast. |
| `Hydralazine -> thyroid disease` | Thyroid disease is a risk factor for hydralazine-induced AAV. |
| `Aminohippuric acid -> neoplasm` | `PAH` likely means polycyclic aromatic hydrocarbons. |
| `Bisphenol A -> cancer` as treatment | Evidence says data are lacking, not that BPA treats cancer. |
| `Domperidone -> digestive system disorder` | Disease context plus cardiac adverse-effect discussion, not clean treatment. |

## Rare-disease abbreviation collisions

| KGX edge | Local meaning |
| --- | --- |
| `Azacitidine -> Miller-Dieker lissencephaly syndrome` | `MDS` means myelodysplastic syndrome. |
| `Decitabine -> Miller-Dieker lissencephaly syndrome` | Same `MDS` collision. |
| `Clopidogrel -> acute chest syndrome` | `ACS` often means acute coronary syndrome. |
| `Clopidogrel -> acrocallosal syndrome` | Same `ACS`, different wrong rare disease. |
| `Ticagrelor -> acute chest syndrome` | Cardiology `ACS` context. |
| `Hydroxyurea -> Schnyder corneal dystrophy` | `SCD` means sickle cell disease. |

## Phenotype false positives

| KGX edge | What went wrong |
| --- | --- |
| `alteplase -> Edema` | `TPA-induced ear edema` uses phorbol ester, not alteplase. |
| `Methyldopa -> Impaired Vision` | `AMD` means age-related macular degeneration. |
| `GH1 -> Short stature` | Text is about growth hormone treatment, not `GH1` gene causation. |
| `VEGFC -> Edema` | Generic `VEGF` mapped to a specific family member. |
| `MAPT -> Cognitive impairment` | CSF tau biomarker context, not direct gene causation. |
| `INS -> Edema` | Insulin/metabolic model context; edema is histopathology. |
| `solution -> Edema` | Generic reagent/exposure artifact. |

## Chemical -> phenotype false positives

| KGX edge | What went wrong |
| --- | --- |
| `Pentaerythritol tetranitrate -> Fever` | Subject mention `ten` came from "ten patients". |
| `Histidine -> Fever` | Subject mention `his` was a pronoun. |
| `Histidine -> Vomiting` | Same pronoun problem. |
| `Dextromethorphan -> Edema` | `DEX` meant dexamethasone. |
| `solution -> Edema` | Generic experimental solution. |
| `Acetaminophen -> Fever` | Patient had fever and took paracetamol; weak exposure context. |

## Model readouts that look clinical

| KGX edge | What the text was really about |
| --- | --- |
| `Histamine -> Edema` | Rat paw edema model. |
| `Formaldehyde -> Edema` | Formalin-induced paw edema. |
| `Serotonin -> Edema` | 5-HT induced paw edema model. |
| `Bradykinin -> Edema` | Mediator-induced edema model. |
| `Capsaicin -> Edema` | Mouse ear edema model. |
| `sodium oxybate -> Absence Seizure` | GHB-induced seizures in animal models. |

## Mechanism false positives

| KGX edge | What went wrong |
| --- | --- |
| `Pembrolizumab -> RPL17` | Object mention `PD-1`; useful target is `PDCD1`. |
| `Pembrolizumab -> SPATA2` | Same `PD-1` collision. |
| `Infliximab -> TNFSF18` | Generic `TNF` fanned out. |
| `Infliximab -> CD40LG` | Same `TNF` fan-out. |
| `Celecoxib -> MT-CO2` | `COX2` should mean `PTGS2` here. |
| `Methyldopa -> CXCR4` | `AMD` came from AMD3100, not alpha-methyldopa. |
| `Cefaclor -> CCL4` | `CCL` is a chemokine prefix, not cefaclor. |
| `Dextromethorphan -> IL6` | `Dex` usually meant dexamethasone. |

## Family fan-out

| Mention | Normalized objects |
| --- | --- |
| `TNF` | `TNF`, `TNFSF12`, `TNFSF13`, `TNFSF13B`, `TNFSF18`, `TNFSF4`, `TNFSF8`, `TNFSF9`, `CD40LG`, `CD70`, `EDA` |
| `VEGF` | `VEGFA`, `VEGFB`, `VEGFC`, `VEGFD` |
| `PPAR` | `PPARA`, `PPARD`, `PPARG` |
| `calcineurin` | `PPP3CA`, `PPP3CB`, `PPP3CC`, `PPP3R1`, `PPP3R2` |
| `PD-1` | `PDCD1`, `RPL17`, `SPATA2` |
| `COX2` | `PTGS2`, `MT-CO2` |

High evidence count does not fix this. Repeated extraction can repeat the same
normalization error.
