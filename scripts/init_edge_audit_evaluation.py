"""Initialize a manual evaluation CSV from the 3k TMKP edge triage rows."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


DEFAULT_AUDIT = Path("audits/tmkp_edge_audit_2026_04_21_batch_001.csv")
DEFAULT_OUTPUT = Path("evaluations/tmkp_edge_audit_2026_04_21_batch_001_manual_review.csv")

MANUAL_COLUMNS = [
    "manual_review_status",
    "manual_reviewer",
    "manual_reviewed_at",
    "manual_edge_support",
    "manual_predicate_fit",
    "manual_normalization_fit",
    "manual_error_tags",
    "manual_notes",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.output.exists() and not args.force:
        raise SystemExit(f"{args.output} already exists; pass --force to overwrite")

    with args.audit.open(newline="") as source:
        reader = csv.DictReader(source)
        source_rows = list(reader)
        source_columns = reader.fieldnames or []

    output_columns = source_columns + MANUAL_COLUMNS
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=output_columns)
        writer.writeheader()
        for row in source_rows:
            for column in MANUAL_COLUMNS:
                row[column] = "pending" if column == "manual_review_status" else ""
            writer.writerow(row)

    print(f"Initialized {len(source_rows)} pending manual review rows at {args.output}")


if __name__ == "__main__":
    main()
