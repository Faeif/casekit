#!/usr/bin/env python3
"""Rank one-way input sensitivity for a model-router scenario."""

import argparse
import json
from pathlib import Path

from model_router import RATE_WORDS, calculate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--scenario", default="base")
    parser.add_argument("--delta", type=float, default=0.10, help="Relative one-way perturbation")
    parser.add_argument("--top", type=int, default=5)
    args = parser.parse_args()
    if not 0 < args.delta < 1:
        raise SystemExit("--delta must be between 0 and 1")
    data = json.loads(args.input.read_text(encoding="utf-8"))
    values = data["scenarios"][args.scenario]
    baseline = calculate(data["model_type"], values)["operating_result"]
    scale = max(abs(baseline), 1)
    rows = []
    for name, value in values.items():
        if not isinstance(value, (int, float)) or value == 0:
            continue
        low_values, high_values = dict(values), dict(values)
        low_values[name] = value * (1 - args.delta)
        high_values[name] = value * (1 + args.delta)
        if any(word in name for word in RATE_WORDS):
            low_values[name] = max(0, low_values[name])
            high_values[name] = min(1, high_values[name])
        low = calculate(data["model_type"], low_values)["operating_result"]
        high = calculate(data["model_type"], high_values)["operating_result"]
        swing = max(abs(low - baseline), abs(high - baseline))
        rows.append({"driver": name, "baseline_input": value, "low_result": low, "base_result": baseline, "high_result": high, "absolute_swing": round(swing, 2), "relative_swing": round(swing / scale, 4)})
    rows.sort(key=lambda row: row["absolute_swing"], reverse=True)
    print(json.dumps({"model_type": data["model_type"], "scenario": args.scenario, "delta": args.delta, "ranked_drivers": rows[:args.top]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
