#!/usr/bin/env python3
"""Calculate transparent first-pass economics for common CaseKit model families."""

import argparse
import json
from pathlib import Path


RATE_WORDS = ("rate", "conversion", "adoption", "take_rate", "retained_share")


def require(data, fields):
    missing = [field for field in fields if field not in data]
    if missing:
        raise ValueError(f"Missing fields: {', '.join(missing)}")
    for name, value in data.items():
        if any(word in name for word in RATE_WORDS) and not 0 <= value <= 1:
            raise ValueError(f"{name} must be between 0 and 1")


def calculate(model_type, d):
    if model_type == "subscription":
        require(d, ["leads", "trial_rate", "paid_rate", "monthly_price", "active_months", "variable_cost_per_paid_user_month", "acquisition_cost", "fixed_cost"])
        trials = d["leads"] * d["trial_rate"]
        paid = trials * d["paid_rate"]
        revenue = paid * d["monthly_price"] * d["active_months"]
        variable_cost = paid * d["variable_cost_per_paid_user_month"] * d["active_months"]
        result = {"trials": trials, "paid_users": paid, "gross_revenue": revenue, "variable_cost": variable_cost}
    elif model_type == "marketplace":
        require(d, ["active_buyers", "orders_per_buyer", "average_order_value", "take_rate", "variable_cost_per_order", "acquisition_cost", "fixed_cost"])
        orders = d["active_buyers"] * d["orders_per_buyer"]
        gmv = orders * d["average_order_value"]
        revenue = gmv * d["take_rate"]
        variable_cost = orders * d["variable_cost_per_order"]
        result = {"orders": orders, "gmv": gmv, "gross_revenue": revenue, "variable_cost": variable_cost}
    elif model_type == "retail":
        require(d, ["footfall", "conversion_rate", "units_per_order", "price_per_unit", "cost_per_unit", "channel_cost", "fixed_cost"])
        orders = d["footfall"] * d["conversion_rate"]
        units = orders * d["units_per_order"]
        revenue = units * d["price_per_unit"]
        variable_cost = units * d["cost_per_unit"]
        result = {"orders": orders, "units": units, "gross_revenue": revenue, "variable_cost": variable_cost}
        d = {**d, "acquisition_cost": d["channel_cost"]}
    elif model_type == "telco":
        require(d, ["eligible_base", "adoption_rate", "arpu_uplift", "active_months", "variable_cost_per_user_month", "acquisition_cost", "fixed_cost"])
        users = d["eligible_base"] * d["adoption_rate"]
        revenue = users * d["arpu_uplift"] * d["active_months"]
        variable_cost = users * d["variable_cost_per_user_month"] * d["active_months"]
        result = {"active_users": users, "gross_revenue": revenue, "variable_cost": variable_cost}
    elif model_type == "internal_transformation":
        require(d, ["eligible_users", "adoption_rate", "hours_saved_per_user", "loaded_hourly_cost", "realization_rate", "implementation_cost", "recurring_cost"])
        users = d["eligible_users"] * d["adoption_rate"]
        gross_value = users * d["hours_saved_per_user"] * d["loaded_hourly_cost"] * d["realization_rate"]
        result = {"active_users": users, "gross_revenue": gross_value, "variable_cost": d["recurring_cost"]}
        d = {**d, "acquisition_cost": 0, "fixed_cost": d["implementation_cost"]}
    elif model_type == "partnership":
        require(d, ["partner_reach", "activation_rate", "conversion_rate", "average_order_value", "retained_share", "variable_cost_per_order", "partnership_cost", "fixed_cost"])
        activated = d["partner_reach"] * d["activation_rate"]
        orders = activated * d["conversion_rate"]
        billings = orders * d["average_order_value"]
        revenue = billings * d["retained_share"]
        variable_cost = orders * d["variable_cost_per_order"]
        result = {"activated": activated, "orders": orders, "billings": billings, "gross_revenue": revenue, "variable_cost": variable_cost}
        d = {**d, "acquisition_cost": d["partnership_cost"]}
    else:
        raise ValueError(f"Unsupported model_type '{model_type}'")
    acquisition = d.get("acquisition_cost", 0)
    fixed = d.get("fixed_cost", 0)
    contribution = result["gross_revenue"] - result["variable_cost"] - acquisition
    result.update({"acquisition_or_channel_cost": acquisition, "fixed_cost": fixed, "contribution": contribution, "operating_result": contribution - fixed})
    return {key: round(value, 2) for key, value in result.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    model_type = data["model_type"]
    output = {"model_type": model_type, "currency": data.get("currency", "unspecified"), "scenarios": {name: calculate(model_type, values) for name, values in data["scenarios"].items()}}
    print(json.dumps(output, ensure_ascii=False, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()
