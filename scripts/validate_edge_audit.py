"""Validate tracked TMKP edge audit CSV artifacts."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


DEFAULT_AUDIT = Path("audits/tmkp_edge_audit_2026_04_21_batch_001.csv")
EXPECTED_ROWS = 3000
EXPECTED_BATCH = "tmkp-2026-04-21-edge-audit-batch-001"
EXPECTED_RELEASE = "2026_04_21"
EXPECTED_METHOD = "assistant_structured_evidence_review_v1"
EXPECTED_REVIEWER = "codex"

EXPECTED_DECISIONS = {
    "needs_review": 2068,
    "partially_supported": 848,
    "supported": 65,
    "unsupported": 19,
}

EXPECTED_STRATA = {
    "gene_disease_contributes": 500,
    "chemical_disease_treatment": 450,
    "chemical_gene_mechanism": 450,
    "gene_gene_mechanism": 400,
    "chemical_disease_contributes": 300,
    "gene_phenotype": 250,
    "chemical_phenotype_treatment": 225,
    "chemical_phenotype_contributes": 225,
    "protein_disease": 100,
    "protein_gene_mechanism": 100,
}

REQUIRED_COLUMNS = [
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

REQUIRED_NONEMPTY = {
    "audit_id",
    "audit_batch_id",
    "release_version",
    "audited_at",
    "reviewer",
    "audit_method",
    "audit_decision",
    "audit_confidence",
    "audit_note",
    "stratum",
    "edge_id",
    "subject_id",
    "subject_name",
    "subject_category",
    "predicate",
    "object_id",
    "object_name",
    "object_category",
    "source_xref",
    "study_result_id",
    "subject_mention",
    "object_mention",
    "supporting_text",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("audit_csv", nargs="?", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--expected-rows", type=int, default=EXPECTED_ROWS)
    parser.add_argument("--expected-batch-id", default=EXPECTED_BATCH)
    parser.add_argument("--expected-release", default=EXPECTED_RELEASE)
    parser.add_argument("--expected-method", default=EXPECTED_METHOD)
    parser.add_argument("--expected-reviewer", default=EXPECTED_REVIEWER)
    parser.add_argument(
        "--skip-decision-count-check",
        action="store_true",
        help="Skip exact audit_decision counts when validating a newly exported batch.",
    )
    return parser.parse_args()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> None:
    args = parse_args()
    with args.audit_csv.open(newline="") as handle:
        reader = csv.DictReader(handle)
        require(reader.fieldnames == REQUIRED_COLUMNS, "CSV columns do not match the expected audit schema")
        rows = list(reader)

    require(len(rows) == args.expected_rows, f"Expected {args.expected_rows} rows, found {len(rows)}")

    edge_ids = [row["edge_id"] for row in rows]
    audit_ids = [row["audit_id"] for row in rows]
    require(len(set(edge_ids)) == args.expected_rows, "Audit file does not contain distinct edge IDs for every row")
    require(len(set(audit_ids)) == args.expected_rows, "Audit file does not contain distinct audit IDs for every row")

    for index, row in enumerate(rows, start=2):
        for column in REQUIRED_NONEMPTY:
            require(row[column].strip() != "", f"Row {index} has empty required column {column}")
        require(row["audit_batch_id"] == args.expected_batch_id, f"Row {index} has unexpected audit_batch_id")
        require(row["release_version"] == args.expected_release, f"Row {index} has unexpected release_version")
        require(row["audit_method"] == args.expected_method, f"Row {index} has unexpected audit_method")
        require(row["reviewer"] == args.expected_reviewer, f"Row {index} has unexpected reviewer")
        require(row["audit_decision"] in EXPECTED_DECISIONS, f"Row {index} has invalid audit_decision")
        require(row["stratum"] in EXPECTED_STRATA, f"Row {index} has invalid stratum")

    decision_counts = Counter(row["audit_decision"] for row in rows)
    stratum_counts = Counter(row["stratum"] for row in rows)
    if not args.skip_decision_count_check:
        require(dict(decision_counts) == EXPECTED_DECISIONS, "Decision counts differ from the manifest")
    require(dict(stratum_counts) == EXPECTED_STRATA, "Stratum counts differ from the manifest")

    print(f"Validated {len(rows)} audit rows from {args.audit_csv}")
    print(f"Distinct edge IDs: {len(set(edge_ids))}")
    print("Decision counts:")
    for decision, count in decision_counts.most_common():
        print(f"  {decision}: {count}")
    if args.skip_decision_count_check:
        print("Exact decision count check skipped")


if __name__ == "__main__":
    main()
