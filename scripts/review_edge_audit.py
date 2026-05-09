"""Interactively review TMKP edge audit rows and store manual labels."""

from __future__ import annotations

import argparse
import csv
from datetime import date
from pathlib import Path


DEFAULT_REVIEW = Path("evaluations/tmkp_edge_audit_2026_04_21_batch_001_manual_review.csv")

EDGE_SUPPORT_VALUES = {"s": "supported", "p": "partially_supported", "u": "unsupported", "c": "unclear"}
FIT_VALUES = {"g": "good", "p": "partial", "b": "bad", "u": "unclear"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW)
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--reviewer", default="manual")
    return parser.parse_args()


def prompt_choice(prompt: str, choices: dict[str, str], allow_skip: bool = True) -> str | None:
    suffix = ", ".join(f"{key}={value}" for key, value in choices.items())
    if allow_skip:
        suffix += ", enter=skip"
    while True:
        value = input(f"{prompt} ({suffix}): ").strip().lower()
        if allow_skip and value == "":
            return None
        if value in choices:
            return choices[value]
        print("Invalid choice.")


def main() -> None:
    args = parse_args()
    with args.review.open(newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    reviewed = 0
    for row in rows:
        if row.get("manual_review_status") == "complete":
            continue
        print("\n" + "=" * 88)
        print(f"Audit ID: {row['audit_id']}")
        print(f"Stratum: {row['stratum']}")
        print(
            f"Edge: {row['subject_name']} [{row['subject_mention']}] "
            f"-- {row['predicate']} / {row['qualified_predicate'] or '<none>'} --> "
            f"{row['object_name']} [{row['object_mention']}]"
        )
        print(f"Triage: {row['audit_decision']} | {row['audit_tags']}")
        print(f"Source: {row['source_xref']} ({row['supporting_text_section_type']}, {row['supporting_document_year']})")
        print(f"Text: {row['supporting_text']}")

        support = prompt_choice("Manual edge support", EDGE_SUPPORT_VALUES)
        if support is None:
            continue
        predicate_fit = prompt_choice("Predicate fit", FIT_VALUES, allow_skip=False)
        normalization_fit = prompt_choice("Normalization fit", FIT_VALUES, allow_skip=False)
        error_tags = input("Manual error tags, pipe-separated: ").strip()
        notes = input("Manual notes: ").strip()

        row["manual_review_status"] = "complete"
        row["manual_reviewer"] = args.reviewer
        row["manual_reviewed_at"] = date.today().isoformat()
        row["manual_edge_support"] = support
        row["manual_predicate_fit"] = predicate_fit or ""
        row["manual_normalization_fit"] = normalization_fit or ""
        row["manual_error_tags"] = error_tags
        row["manual_notes"] = notes
        reviewed += 1

        if reviewed >= args.limit:
            break

    with args.review.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Reviewed {reviewed} rows.")


if __name__ == "__main__":
    main()
