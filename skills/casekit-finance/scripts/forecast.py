#!/usr/bin/env python3
"""Calculate a transparent revenue-first funnel forecast from JSON input."""

import argparse
import json
import math
from pathlib import Path


REQUIRED = (
    "eligible_audience",
    "reach_rate",
    "response_rate",
    "qualified_rate",
    "purchase_rate",
    "average_order_value",
    "purchase_frequency",
    "variable_cost_per_order",
    "channel_cost",
)


def validate_rate(name, value):
    if not 0 <= value <= 1:
        raise ValueError(f"{name} must be between 0 and 1; got {value}")


def calculate(scenario, target_revenue, fixed_cost):
    missing = [key for key in REQUIRED if key not in scenario]
    if missing:
        raise ValueError(f"Missing scenario fields: {', '.join(missing)}")

    for key in ("reach_rate", "response_rate", "qualified_rate", "purchase_rate"):
        validate_rate(key, scenario[key])

    reached = scenario["eligible_audience"] * scenario["reach_rate"]
    responses = reached * scenario["response_rate"]
    qualified = responses * scenario["qualified_rate"]
    orders = qualified * scenario["purchase_rate"]
    gross_revenue = orders * scenario["average_order_value"] * scenario["purchase_frequency"]
    variable_cost = orders * scenario["variable_cost_per_order"]
    contribution = gross_revenue - variable_cost - scenario["channel_cost"]
    operating_result = contribution - fixed_cost

    net_per_order = scenario["average_order_value"] * scenario["purchase_frequency"]
    required_orders = target_revenue / net_per_order if net_per_order else math.inf
    full_conversion = (
        scenario["reach_rate"]
        * scenario["response_rate"]
        * scenario["qualified_rate"]
        * scenario["purchase_rate"]
    )
    required_audience = required_orders / full_conversion if full_conversion else math.inf
    contribution_per_order = net_per_order - scenario["variable_cost_per_order"]
    attributable_fixed = fixed_cost + scenario["channel_cost"]
    break_even_orders = (
        attributable_fixed / contribution_per_order if contribution_per_order > 0 else math.inf
    )

    result = {
        "reached": reached,
        "responses": responses,
        "qualified": qualified,
        "orders": orders,
        "gross_revenue": gross_revenue,
        "variable_cost": variable_cost,
        "channel_cost": scenario["channel_cost"],
        "fixed_cost": fixed_cost,
        "contribution": contribution,
        "operating_result": operating_result,
        "target_revenue": target_revenue,
        "target_attainment": gross_revenue / target_revenue if target_revenue else None,
        "required_orders_for_target": required_orders,
        "required_eligible_audience_for_target": required_audience,
        "break_even_orders": break_even_orders,
    }
    return {
        key: round(value, 2) if isinstance(value, float) and math.isfinite(value) else value
        for key, value in result.items()
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Path to forecast JSON")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args()

    data = json.loads(args.input.read_text(encoding="utf-8"))
    target = data.get("target_revenue", 0)
    fixed = data.get("fixed_cost", 0)
    scenarios = data.get("scenarios")
    if not scenarios:
        raise ValueError("Input must contain a non-empty scenarios object")

    output = {
        "currency": data.get("currency", "unspecified"),
        "scenarios": {
            name: calculate(values, target, fixed) for name, values in scenarios.items()
        },
    }
    print(json.dumps(output, ensure_ascii=False, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()
