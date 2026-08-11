#!/usr/bin/env python3
"""Calculate a weighted judge-readiness score from a rubric CSV."""

import argparse
import csv
from pathlib import Path


REQUIRED = {"criterion", "weight", "score", "max_score", "evidence", "gap", "owner"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rubric", type=Path)
    args = parser.parse_args()
    with args.rubric.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED - set(reader.fieldnames or [])
        if missing:
            raise SystemExit(f"Missing rubric columns: {', '.join(sorted(missing))}")
        rows = [row for row in reader if any((value or "").strip() for value in row.values())]
    total_weight = sum(float(row["weight"]) for row in rows)
    if total_weight <= 0:
        raise SystemExit("Total rubric weight must be positive")
    weighted = 0.0
    priorities = []
    for row in rows:
        weight, score, maximum = float(row["weight"]), float(row["score"]), float(row["max_score"])
        if not 0 <= score <= maximum or maximum <= 0:
            raise SystemExit(f"Invalid score for {row['criterion']}")
        weighted += weight * score / maximum
        lost = weight * (1 - score / maximum)
        priorities.append((lost, row["criterion"], row["gap"], row["owner"]))
    print(f"Weighted readiness: {100 * weighted / total_weight:.1f}/100")
    print("Priority gaps:")
    for lost, criterion, gap, owner in sorted(priorities, reverse=True)[:5]:
        print(f"- {criterion}: {gap or 'unspecified gap'}; owner={owner or 'unassigned'}; weighted points at risk={100 * lost / total_weight:.1f}")


if __name__ == "__main__":
    main()
