"""Apply a batch of manual labels to the TMKP edge audit evaluation CSV."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


DEFAULT_REVIEW = Path("evaluations/tmkp_edge_audit_2026_04_21_batch_001_manual_review.csv")
DEFAULT_LABELS = Path("evaluations/manual_review_labels_batch_001_seed.csv")

MANUAL_COLUMNS = [
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
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW)
    parser.add_argument("--labels", type=Path, default=DEFAULT_LABELS)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with args.review.open(newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    with args.labels.open(newline="") as handle:
        labels = {row["audit_id"]: row for row in csv.DictReader(handle)}

    applied = 0
    for row in rows:
        label = labels.get(row["audit_id"])
        if not label:
            continue
        row["manual_review_status"] = "complete"
        for column in MANUAL_COLUMNS:
            row[column] = label[column]
        applied += 1

    with args.review.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Applied {applied} manual labels from {args.labels}")


if __name__ == "__main__":
    main()
