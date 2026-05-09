"""Score deterministic TMKP edge-audit rules against manual review labels."""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path


DEFAULT_REVIEW = Path("evaluations/tmkp_edge_audit_2026_04_21_batch_001_manual_review.csv")
DEFAULT_OUTPUT = Path("evaluations/tmkp_edge_audit_2026_04_21_batch_001_rule_scores.csv")

FAILURE_LABELS = {"unsupported", "unclear"}
WEAK_OR_BAD_LABELS = {"partially_supported", "unsupported", "unclear"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def split_tags(value: str) -> list[str]:
    return [tag for tag in value.split("|") if tag]


def pct(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return ""
    return f"{100 * numerator / denominator:.1f}"


def main() -> None:
    args = parse_args()
    with args.review.open(newline="") as handle:
        rows = [row for row in csv.DictReader(handle)]

    complete_rows = [row for row in rows if row.get("manual_review_status") == "complete"]
    if not complete_rows:
        raise SystemExit("No completed manual review rows found; cannot score rules yet")

    all_tags = sorted({tag for row in rows for tag in split_tags(row.get("audit_tags", ""))})
    scores: list[dict[str, str]] = []
    total_complete = len(complete_rows)
    total_failures = sum(row["manual_edge_support"] in FAILURE_LABELS for row in complete_rows)
    total_weak_or_bad = sum(row["manual_edge_support"] in WEAK_OR_BAD_LABELS for row in complete_rows)

    for tag in all_tags:
        tagged_rows = [row for row in complete_rows if tag in split_tags(row.get("audit_tags", ""))]
        untagged_rows = [row for row in complete_rows if tag not in split_tags(row.get("audit_tags", ""))]
        tagged = len(tagged_rows)
        failures = sum(row["manual_edge_support"] in FAILURE_LABELS for row in tagged_rows)
        weak_or_bad = sum(row["manual_edge_support"] in WEAK_OR_BAD_LABELS for row in tagged_rows)
        untagged_failures = sum(row["manual_edge_support"] in FAILURE_LABELS for row in untagged_rows)

        scores.append(
            {
                "rule_tag": tag,
                "manual_rows": str(total_complete),
                "tagged_rows": str(tagged),
                "coverage_pct": pct(tagged, total_complete),
                "failure_precision_pct": pct(failures, tagged),
                "weak_or_bad_precision_pct": pct(weak_or_bad, tagged),
                "failure_recall_pct": pct(failures, total_failures),
                "weak_or_bad_recall_pct": pct(weak_or_bad, total_weak_or_bad),
                "untagged_failure_rate_pct": pct(untagged_failures, len(untagged_rows)),
                "manual_failures_in_tagged_rows": str(failures),
                "manual_weak_or_bad_in_tagged_rows": str(weak_or_bad),
            }
        )

    scores.sort(
        key=lambda row: (
            float(row["failure_precision_pct"] or 0),
            int(row["manual_failures_in_tagged_rows"]),
            float(row["weak_or_bad_precision_pct"] or 0),
        ),
        reverse=True,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as handle:
        fieldnames = [
            "rule_tag",
            "manual_rows",
            "tagged_rows",
            "coverage_pct",
            "failure_precision_pct",
            "weak_or_bad_precision_pct",
            "failure_recall_pct",
            "weak_or_bad_recall_pct",
            "untagged_failure_rate_pct",
            "manual_failures_in_tagged_rows",
            "manual_weak_or_bad_in_tagged_rows",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(scores)

    support_counts = Counter(row["manual_edge_support"] for row in complete_rows)
    print(f"Scored {len(scores)} rule tags against {total_complete} manual rows")
    print("Manual support labels:")
    for label, count in support_counts.most_common():
        print(f"  {label}: {count}")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
