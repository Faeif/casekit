#!/usr/bin/env python3
"""Validate CaseKit ledgers for required columns, IDs, ranges, and references."""

import argparse
import csv
import re
import sys
from pathlib import Path


FILES = {
    "evidence": (
        "01-evidence-ledger.csv",
        ["claim_id", "source_id", "claim", "status"],
        {"claim_id": r"CLM-\d{3,}", "source_id": r"SRC-\d{3,}"},
        [],
    ),
    "assumptions": (
        "02-assumptions.csv",
        ["assumption_id", "variable", "low", "base", "high", "confidence", "status"],
        {"assumption_id": r"ASM-\d{3,}"},
        ["assumption_id"],
    ),
    "metrics": (
        "03-metric-tree.csv",
        ["metric_id", "metric", "metric_type", "formula", "unit"],
        {"metric_id": r"MET-\d{3,}"},
        ["metric_id"],
    ),
    "premises": (
        "08-premises.csv",
        ["premise_id", "premise", "type", "confidence", "decision_impact", "status"],
        {"premise_id": r"PRM-\d{3,}"},
        ["premise_id"],
    ),
    "experiments": (
        "09-experiments.csv",
        ["experiment_id", "premise_ids", "method", "pass_threshold", "stop_threshold", "status"],
        {"experiment_id": r"EXP-\d{3,}"},
        ["experiment_id"],
    ),
}


def read_rows(path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader)


def as_float(value):
    if value is None or value.strip() == "":
        return None
    return float(value.replace(",", ""))


def validate(root):
    errors = []
    warnings = []
    seen = {}
    official = root / "03-OFFICIAL"
    if not official.is_dir():
        official = root

    for group, (filename, required, patterns, unique_fields) in FILES.items():
        path = official / filename
        if not path.exists():
            errors.append(f"Missing required file: {filename}")
            continue
        fields, rows = read_rows(path)
        missing = [field for field in required if field not in fields]
        if missing:
            errors.append(f"{filename}: missing columns: {', '.join(missing)}")
            continue

        for line, row in enumerate(rows, start=2):
            for field, pattern in patterns.items():
                value = (row.get(field) or "").strip()
                if not value:
                    warnings.append(f"{filename}:{line}: blank {field}")
                    continue
                if not re.fullmatch(pattern, value):
                    errors.append(f"{filename}:{line}: invalid {field} '{value}'")
                unique_key = f"{field}:{value}"
                if field in unique_fields and unique_key in seen:
                    errors.append(
                        f"{filename}:{line}: duplicate ID {value}; first seen at {seen[unique_key]}"
                    )
                elif field in unique_fields:
                    seen[unique_key] = f"{filename}:{line}"

            if group == "evidence":
                pair = f"{row.get('claim_id', '').strip()}:{row.get('source_id', '').strip()}"
                pair_key = f"evidence-pair:{pair}"
                if pair != ":" and pair_key in seen:
                    errors.append(
                        f"{filename}:{line}: duplicate claim-source pair {pair}; first seen at {seen[pair_key]}"
                    )
                elif pair != ":":
                    seen[pair_key] = f"{filename}:{line}"

            if group == "assumptions":
                try:
                    low, base, high = (as_float(row.get(k)) for k in ("low", "base", "high"))
                    if None not in (low, base, high) and not low <= base <= high:
                        errors.append(
                            f"{filename}:{line}: expected low <= base <= high; got {low}, {base}, {high}"
                        )
                except ValueError:
                    warnings.append(
                        f"{filename}:{line}: non-numeric range; verify ordered categorical values manually"
                    )

            if group == "metrics" and not (row.get("formula") or "").strip():
                warnings.append(f"{filename}:{line}: metric has no formula")

    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path, help="Case project directory")
    args = parser.parse_args()
    errors, warnings = validate(args.project)

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    print(f"Validation complete: {len(errors)} error(s), {len(warnings)} warning(s)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
