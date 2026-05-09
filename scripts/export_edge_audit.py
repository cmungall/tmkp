"""Export a stratified TMKP edge audit CSV from the local DuckDB database."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import duckdb


DEFAULT_DB = Path("downloads/tmkp/2026_04_21/tmkp.duckdb")
DEFAULT_OUTPUT = Path("audits/tmkp_edge_audit_2026_04_21_batch_001.csv")
RELEASE_VERSION = "2026_04_21"
DEFAULT_BATCH_ID = "tmkp-2026-04-21-edge-audit-batch-001"
AUDITED_AT = "2026-05-04"
REVIEWER = "codex"
AUDIT_METHOD = "assistant_structured_evidence_review_v1"


STRATA_QUOTAS = {
    "gene_disease_contributes": 500,
    "chemical_disease_treatment": 450,
    "chemical_disease_contributes": 300,
    "chemical_gene_mechanism": 450,
    "gene_gene_mechanism": 400,
    "gene_phenotype": 250,
    "chemical_phenotype_treatment": 225,
    "chemical_phenotype_contributes": 225,
    "protein_disease": 100,
    "protein_gene_mechanism": 100,
}


FIELDNAMES = [
    "audit_id",
    "audit_batch_id",
    "release_version",
    "audited_at",
    "reviewer",
    "audit_method",
    "audit_decision",
    "audit_confidence",
    "audit_tags",
    "audit_note",
    "stratum",
    "edge_id",
    "subject_id",
    "subject_name",
    "subject_category",
    "predicate",
    "qualified_predicate",
    "object_id",
    "object_name",
    "object_category",
    "evidence_count",
    "edge_confidence_score",
    "source_xref",
    "supporting_document_year",
    "supporting_text_section_type",
    "study_result_id",
    "extraction_confidence_score",
    "subject_mention",
    "object_mention",
    "subject_mention_match",
    "object_mention_match",
    "supporting_text",
]


CHEMICAL_CATEGORIES = {
    "biolink:ChemicalEntity",
    "biolink:ChemicalMixture",
    "biolink:Drug",
    "biolink:MolecularMixture",
    "biolink:SmallMolecule",
}

GENERIC_OBJECTS = {
    "abnormality",
    "abnormality of physiology",
    "cancer",
    "disease",
    "disorder",
    "illness",
    "neoplasm",
    "pain",
    "syndrome",
    "tumor",
}

COMMON_BAD_MENTIONS = {
    "group",
    "groups",
    "his",
    "ten",
    "duration",
    "solution",
    "ligand",
    "biomarker",
    "control",
    "case",
    "cases",
}

FAMILY_TERMS = {
    "akt",
    "calcineurin",
    "cox",
    "cox2",
    "cox-2",
    "egf",
    "erk",
    "hsp",
    "il-1",
    "il1",
    "mapk",
    "nf-kb",
    "nfkb",
    "p38",
    "pd-1",
    "pd1",
    "ppar",
    "stat",
    "tgf-beta",
    "tgfb",
    "tnf",
    "vegf",
}

NEGATION_TERMS = (
    "absence of",
    "did not",
    "does not",
    "failed to",
    "lack of",
    "no evidence",
    "no significant",
    "not associated",
    "not caused",
    "not detected",
    "not found",
    "questionable",
    "unlikely",
    "without",
)

TREATMENT_TERMS = (
    "administered",
    "benefit",
    "cure",
    "dose",
    "drug",
    "efficacy",
    "improved",
    "management",
    "patients received",
    "therapy",
    "therapeutic",
    "treat",
    "treatment",
    "trial",
)

ADVERSE_RISK_TERMS = (
    "adverse",
    "associated with",
    "caused",
    "complication",
    "contributes",
    "death",
    "exposure",
    "induced",
    "induces",
    "risk",
    "side effect",
    "toxicity",
    "toxic",
    "triggered",
)

COHORT_EXPOSURE_TERMS = (
    "administered to a patient with",
    "case report",
    "cohort",
    "comorbidity",
    "history of",
    "in a patient with",
    "in patients with",
    "patient with",
    "patients with",
    "received",
    "safely administered",
)

MECHANISM_TERMS = (
    "activated",
    "activation",
    "bind",
    "downregulation",
    "expression",
    "inhibit",
    "inhibited",
    "inhibition",
    "knockdown",
    "phosphorylation",
    "regulates",
    "silencing",
    "suppressed",
    "upregulation",
)

BIOMARKER_TERMS = (
    "biomarker",
    "detected",
    "diagnostic",
    "expressed",
    "expression",
    "level",
    "marker",
    "prognosis",
    "prognostic",
    "serum",
    "survival",
)

MODEL_ASSAY_TERMS = (
    "animal model",
    "assay",
    "cell line",
    "cultured",
    "drosophila",
    "in vitro",
    "mice",
    "mouse",
    "murine",
    "rat",
    "rats",
    "zebrafish",
)

METHOD_REAGENT_TERMS = (
    "antibody",
    "buffer",
    "coverslip",
    "incubat",
    "medium",
    "pcr",
    "protocol",
    "reagent",
    "staining",
    "western blot",
)

LIST_CONTEXT_TERMS = (
    "including",
    "such as",
    "respectively",
    "genes including",
    "mutations in",
)


@dataclass
class Evidence:
    study_result_id: str = ""
    xref: str = ""
    text: str = ""
    subject_mention: str = ""
    object_mention: str = ""
    extraction_confidence_score: str = ""
    supporting_document_year: str = ""
    supporting_text_section_type: str = ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--batch-id", default=DEFAULT_BATCH_ID)
    parser.add_argument("--audited-at", default=AUDITED_AT)
    parser.add_argument("--reviewer", default=REVIEWER)
    parser.add_argument("--audit-method", default=AUDIT_METHOD)
    parser.add_argument(
        "--exclude-audit",
        action="append",
        type=Path,
        default=[],
        help="Existing audit CSV whose edge_id values should be skipped. Can be repeated.",
    )
    parser.add_argument(
        "--candidate-multiplier",
        type=int,
        default=10,
        help="Per-stratum candidate pool size as quota * multiplier before evidence filtering.",
    )
    return parser.parse_args()


def canonical(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())


def tokens(value: Any) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", str(value or "").lower()) if len(token) > 2}


def contains_any(text: str, terms: tuple[str, ...] | set[str]) -> bool:
    lower = text.lower()
    return any(term in lower for term in terms)


def mention_from_offsets(text: str, offsets: Any) -> str:
    if not isinstance(offsets, list) or len(offsets) != 2:
        return ""
    start, end = offsets
    if not isinstance(start, int) or not isinstance(end, int):
        return ""
    if start < 0 or end < start or end > len(text):
        return ""
    return text[start:end]


def mention_matches(mention: str, name: str) -> bool:
    mention_canon = canonical(mention)
    name_canon = canonical(name)
    if not mention_canon or not name_canon:
        return False
    if mention_canon == name_canon:
        return True
    if len(mention_canon) >= 4 and (mention_canon in name_canon or name_canon in mention_canon):
        return True
    return bool(tokens(mention) & tokens(name))


def short_mismatch(mention: str, name: str) -> bool:
    mention_canon = canonical(mention)
    return 0 < len(mention_canon) <= 4 and not mention_matches(mention, name)


def common_bad_mention(mention: str) -> bool:
    return canonical(mention) in {canonical(value) for value in COMMON_BAD_MENTIONS}


def choose_evidence(payload: str) -> Evidence:
    try:
        studies = json.loads(payload)
    except json.JSONDecodeError:
        return Evidence()

    results: list[dict[str, Any]] = []
    for study in studies.values():
        if not isinstance(study, dict):
            continue
        for result in study.get("has_study_results", []):
            if isinstance(result, dict):
                results.append(result)

    if not results:
        return Evidence()

    def result_score(result: dict[str, Any]) -> tuple[int, int, float, int]:
        score = result.get("extraction_confidence_score")
        if not isinstance(score, (int, float)):
            score = 0.0
        text = result.get("supporting_text", [""])
        text_value = text[0] if isinstance(text, list) and text else ""
        text_string = str(text_value)
        subject_mention = mention_from_offsets(text_string, result.get("subject_location_in_text"))
        object_mention = mention_from_offsets(text_string, result.get("object_location_in_text"))
        has_both_mentions = int(bool(subject_mention and object_mention))
        is_abstract = int(str(result.get("supporting_text_section_type", "")).lower() == "abstract")
        return has_both_mentions, is_abstract, float(score), len(text_string)

    result = max(results, key=result_score)
    text_list = result.get("supporting_text", [""])
    text = str(text_list[0]) if isinstance(text_list, list) and text_list else ""
    xref_list = result.get("xref", [""])
    xref = str(xref_list[0]) if isinstance(xref_list, list) and xref_list else ""
    score = result.get("extraction_confidence_score", "")
    return Evidence(
        study_result_id=str(result.get("id", "")),
        xref=xref,
        text=text,
        subject_mention=mention_from_offsets(text, result.get("subject_location_in_text")),
        object_mention=mention_from_offsets(text, result.get("object_location_in_text")),
        extraction_confidence_score=str(round(float(score), 6)) if isinstance(score, (int, float)) else "",
        supporting_document_year=str(result.get("supporting_document_year", "")),
        supporting_text_section_type=str(result.get("supporting_text_section_type", "")),
    )


def audit_row(row: dict[str, Any], evidence: Evidence) -> tuple[str, str, list[str], str]:
    text = evidence.text
    subject_mention = evidence.subject_mention
    object_mention = evidence.object_mention
    subject_name = str(row["subject_name"] or "")
    object_name = str(row["object_name"] or "")
    predicate = str(row["predicate"] or "")
    object_category = str(row["object_primary_category"] or "")
    stratum = str(row["stratum"] or "")

    tags: list[str] = []
    notes: list[str] = []

    subject_match = mention_matches(subject_mention, subject_name)
    object_match = mention_matches(object_mention, object_name)

    if not text or not subject_mention or not object_mention:
        tags.append("text_span_missing")
        notes.append("supporting text or mention offsets are missing")

    if short_mismatch(subject_mention, subject_name) or short_mismatch(object_mention, object_name):
        tags.append("short_mention_risk")
        notes.append("short mention has low lexical agreement with normalized node")

    if common_bad_mention(subject_mention) or common_bad_mention(object_mention):
        tags.append("common_word_mention")
        notes.append("mention is a common word or nonspecific term")

    if not subject_match or not object_match:
        tags.append("mention_mismatch")
        notes.append("mention text has weak lexical agreement with normalized label")

    object_lower = object_name.lower()
    if object_lower in GENERIC_OBJECTS or object_lower.endswith(" syndrome") and object_lower == "syndrome":
        tags.append("generic_object")
        notes.append("object label is generic or low-specificity")

    mention_terms = {subject_mention.lower(), object_mention.lower(), subject_name.lower(), object_name.lower()}
    if any(canonical(term) in {canonical(family) for family in FAMILY_TERMS} for term in mention_terms):
        tags.append("family_mention_fanout")
        notes.append("family-level molecular mention may have been normalized to a specific node")

    if contains_any(text, NEGATION_TERMS):
        tags.append("negation_or_hedging")
        notes.append("evidence contains negation or hedging language")

    if contains_any(text, TREATMENT_TERMS):
        tags.append("treatment_context")
    if contains_any(text, ADVERSE_RISK_TERMS):
        tags.append("adverse_or_risk_context")
    if contains_any(text, COHORT_EXPOSURE_TERMS):
        tags.append("cohort_or_exposure_context")
    if contains_any(text, MECHANISM_TERMS):
        tags.append("mechanism_context")
    if contains_any(text, BIOMARKER_TERMS):
        tags.append("biomarker_or_expression_context")
    if contains_any(text, MODEL_ASSAY_TERMS):
        tags.append("model_or_assay_context")
    if contains_any(text, METHOD_REAGENT_TERMS):
        tags.append("method_or_reagent_context")

    comma_count = text.count(",")
    semicolon_count = text.count(";")
    if contains_any(text, LIST_CONTEXT_TERMS) and comma_count + semicolon_count >= 3:
        tags.append("list_or_cross_product_context")
        notes.append("evidence looks like a list context that may cross-product entities")

    normalization_risk = {
        "common_word_mention",
        "family_mention_fanout",
        "mention_mismatch",
        "short_mention_risk",
        "text_span_missing",
    } & set(tags)

    context_risk = {
        "generic_object",
        "adverse_or_risk_context",
        "cohort_or_exposure_context",
        "list_or_cross_product_context",
        "mechanism_context",
        "method_or_reagent_context",
        "model_or_assay_context",
        "negation_or_hedging",
    } & set(tags)

    if "common_word_mention" in tags:
        decision = "unsupported"
        confidence = "medium"
    elif normalization_risk:
        decision = "needs_review"
        confidence = "medium"
    elif "method_or_reagent_context" in tags:
        decision = "needs_review"
        confidence = "medium"
        notes.append("methods or reagent context weakens the edge assertion")
    elif "negation_or_hedging" in tags:
        decision = "needs_review"
        confidence = "medium"
        notes.append("negation or hedging requires manual confirmation")
    elif "treats_or_applied_or_studied_to_treat" in predicate and "treatment_context" in tags:
        decision = "partially_supported" if context_risk or object_category != "biolink:Disease" else "supported"
        confidence = "medium"
        notes.append("treatment language matches treatment-style predicate")
    elif "contributes_to" in predicate and "adverse_or_risk_context" in tags:
        decision = "partially_supported"
        confidence = "medium"
        notes.append("risk/adverse language matches broad contributes_to semantics")
    elif "affects" in predicate and "mechanism_context" in tags and stratum.endswith("mechanism"):
        decision = "partially_supported"
        confidence = "medium"
        notes.append("mechanistic language matches broad affects semantics")
    elif "biomarker_or_expression_context" in tags:
        decision = "partially_supported"
        confidence = "low"
        notes.append("evidence supports expression/biomarker context, not necessarily causality")
    elif "model_or_assay_context" in tags:
        decision = "partially_supported"
        confidence = "low"
        notes.append("evidence appears model or assay based")
    else:
        decision = "needs_review"
        confidence = "low"
        notes.append("evidence has co-mentions but no high-confidence audit rule fired")

    unique_tags = sorted(set(tags))
    note = "; ".join(dict.fromkeys(notes))[:500]
    return decision, confidence, unique_tags, note


def load_excluded_edge_ids(paths: list[Path]) -> set[str]:
    edge_ids: set[str] = set()
    for path in paths:
        with path.open(newline="") as handle:
            for row in csv.DictReader(handle):
                edge_id = str(row.get("edge_id") or "")
                if edge_id:
                    edge_ids.add(edge_id)
    return edge_ids


def fetch_rows(db_path: Path, candidate_multiplier: int) -> list[dict[str, Any]]:
    if candidate_multiplier < 1:
        raise SystemExit("--candidate-multiplier must be at least 1")

    con = duckdb.connect(str(db_path), read_only=True)
    quotas_sql = "\nUNION ALL\n".join(
        f"SELECT '{stratum}' AS stratum, {quota} AS quota" for stratum, quota in STRATA_QUOTAS.items()
    )
    query = f"""
    WITH quotas AS (
        {quotas_sql}
    ),
    candidates AS (
        SELECT
            CASE
                WHEN subject_primary_category = 'biolink:Gene'
                  AND object_primary_category = 'biolink:Disease'
                  AND qualified_predicate = 'biolink:contributes_to'
                    THEN 'gene_disease_contributes'
                WHEN subject_primary_category IN {tuple(CHEMICAL_CATEGORIES)}
                  AND object_primary_category = 'biolink:Disease'
                  AND predicate = 'biolink:treats_or_applied_or_studied_to_treat'
                    THEN 'chemical_disease_treatment'
                WHEN subject_primary_category IN {tuple(CHEMICAL_CATEGORIES)}
                  AND object_primary_category = 'biolink:Disease'
                  AND predicate = 'biolink:contributes_to'
                    THEN 'chemical_disease_contributes'
                WHEN subject_primary_category IN {tuple(CHEMICAL_CATEGORIES)}
                  AND object_primary_category IN ('biolink:Gene', 'biolink:Protein')
                  AND predicate = 'biolink:affects'
                    THEN 'chemical_gene_mechanism'
                WHEN subject_primary_category = 'biolink:Protein'
                  AND object_primary_category = 'biolink:Gene'
                  AND predicate = 'biolink:affects'
                    THEN 'protein_gene_mechanism'
                WHEN subject_primary_category IN ('biolink:Gene', 'biolink:Protein')
                  AND object_primary_category IN ('biolink:Gene', 'biolink:Protein')
                  AND predicate = 'biolink:affects'
                    THEN 'gene_gene_mechanism'
                WHEN subject_primary_category IN ('biolink:Gene', 'biolink:Protein')
                  AND object_primary_category = 'biolink:PhenotypicFeature'
                    THEN 'gene_phenotype'
                WHEN subject_primary_category IN {tuple(CHEMICAL_CATEGORIES)}
                  AND object_primary_category = 'biolink:PhenotypicFeature'
                  AND predicate = 'biolink:treats_or_applied_or_studied_to_treat'
                    THEN 'chemical_phenotype_treatment'
                WHEN subject_primary_category IN {tuple(CHEMICAL_CATEGORIES)}
                  AND object_primary_category = 'biolink:PhenotypicFeature'
                  AND predicate = 'biolink:contributes_to'
                    THEN 'chemical_phenotype_contributes'
                WHEN subject_primary_category = 'biolink:Protein'
                  AND object_primary_category = 'biolink:Disease'
                    THEN 'protein_disease'
            END AS stratum,
            id,
            subject,
            subject_name,
            subject_primary_category,
            predicate,
            qualified_predicate,
            object,
            object_name,
            object_primary_category,
            evidence_count,
            has_confidence_score,
            CAST(has_supporting_studies AS VARCHAR) AS has_supporting_studies
        FROM edges_enriched
    ),
    ranked AS (
        SELECT
            c.*,
            q.quota,
            row_number() OVER (PARTITION BY c.stratum ORDER BY hash(c.id)) AS rn
        FROM candidates c
        JOIN quotas q ON q.stratum = c.stratum
        WHERE c.stratum IS NOT NULL
    )
    SELECT *
    FROM ranked
    WHERE rn <= quota * {candidate_multiplier}
    ORDER BY stratum, rn;
    """
    rows = con.execute(query).fetchall()
    columns = [column[0] for column in con.description]
    con.close()
    return [dict(zip(columns, row)) for row in rows]


def build_output_row(
    index: int,
    row: dict[str, Any],
    batch_id: str,
    audited_at: str,
    reviewer: str,
    audit_method: str,
) -> dict[str, str]:
    evidence = choose_evidence(str(row["has_supporting_studies"] or ""))
    decision, confidence, tags, note = audit_row(row, evidence)
    subject_match = mention_matches(evidence.subject_mention, str(row["subject_name"] or ""))
    object_match = mention_matches(evidence.object_mention, str(row["object_name"] or ""))
    edge_score = row["has_confidence_score"]
    return {
        "audit_id": f"{batch_id}-{index:04d}",
        "audit_batch_id": batch_id,
        "release_version": RELEASE_VERSION,
        "audited_at": audited_at,
        "reviewer": reviewer,
        "audit_method": audit_method,
        "audit_decision": decision,
        "audit_confidence": confidence,
        "audit_tags": "|".join(tags),
        "audit_note": note,
        "stratum": str(row["stratum"] or ""),
        "edge_id": str(row["id"] or ""),
        "subject_id": str(row["subject"] or ""),
        "subject_name": str(row["subject_name"] or ""),
        "subject_category": str(row["subject_primary_category"] or ""),
        "predicate": str(row["predicate"] or ""),
        "qualified_predicate": str(row["qualified_predicate"] or ""),
        "object_id": str(row["object"] or ""),
        "object_name": str(row["object_name"] or ""),
        "object_category": str(row["object_primary_category"] or ""),
        "evidence_count": str(row["evidence_count"] or ""),
        "edge_confidence_score": str(round(float(edge_score), 6)) if isinstance(edge_score, (int, float)) else "",
        "source_xref": evidence.xref,
        "supporting_document_year": evidence.supporting_document_year,
        "supporting_text_section_type": evidence.supporting_text_section_type,
        "study_result_id": evidence.study_result_id,
        "extraction_confidence_score": evidence.extraction_confidence_score,
        "subject_mention": evidence.subject_mention,
        "object_mention": evidence.object_mention,
        "subject_mention_match": str(subject_match).lower(),
        "object_mention_match": str(object_match).lower(),
        "supporting_text": evidence.text,
    }


def main() -> None:
    args = parse_args()
    candidates = fetch_rows(args.db, args.candidate_multiplier)
    excluded_edge_ids = load_excluded_edge_ids(args.exclude_audit)
    expected = sum(STRATA_QUOTAS.values())
    selected_rows: list[dict[str, Any]] = []
    selected_counts: Counter[str] = Counter()
    for row in candidates:
        if str(row["id"] or "") in excluded_edge_ids:
            continue
        stratum = str(row["stratum"] or "")
        if selected_counts[stratum] >= STRATA_QUOTAS[stratum]:
            continue
        evidence = choose_evidence(str(row["has_supporting_studies"] or ""))
        if not evidence.text or not evidence.subject_mention or not evidence.object_mention:
            continue
        selected_rows.append(row)
        selected_counts[stratum] += 1

    if len(selected_rows) != expected:
        raise SystemExit(f"Expected {expected} sampled rows, got {len(selected_rows)}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        for index, row in enumerate(selected_rows, start=1):
            writer.writerow(
                build_output_row(
                    index,
                    row,
                    batch_id=args.batch_id,
                    audited_at=args.audited_at,
                    reviewer=args.reviewer,
                    audit_method=args.audit_method,
                )
            )

    print(f"Wrote {len(selected_rows)} audit rows to {args.output}")
    if excluded_edge_ids:
        print(f"Excluded {len(excluded_edge_ids)} previously audited edge IDs")


if __name__ == "__main__":
    main()
