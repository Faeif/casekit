#!/usr/bin/env python3
"""Calculate evidence-linked CAC, cohort LTV, payback, retention, and cash metrics."""

import argparse
import json
from pathlib import Path


CHANNEL_KINDS = {"paid", "organic", "partner", "sales", "referral", "other"}


def require(mapping, fields, context):
    missing = [field for field in fields if field not in mapping]
    if missing:
        raise ValueError(f"{context}: missing fields: {', '.join(missing)}")


def nonnegative(name, value):
    if not isinstance(value, (int, float)) or value < 0:
        raise ValueError(f"{name} must be a non-negative number")


def rate(name, value):
    if not isinstance(value, (int, float)) or not 0 <= value <= 1:
        raise ValueError(f"{name} must be between 0 and 1")


def ratio(numerator, denominator):
    return numerator / denominator if denominator else None


def rounded(value):
    return round(value, 4) if isinstance(value, float) else value


def calculate(data):
    require(data, ["unit_name", "period_name", "currency", "cac_basis", "acquisition", "cohort"], "root")
    if data["cac_basis"] not in {"attributable", "fully_loaded"}:
        raise ValueError("cac_basis must be attributable or fully_loaded")
    discount = data.get("discount_rate_per_period", 0)
    rate("discount_rate_per_period", discount)

    acquisition = data["acquisition"]
    require(acquisition, ["new_customers", "attributable_spend", "fully_loaded_spend", "source_or_assumption_ids"], "acquisition")
    customers = acquisition["new_customers"]
    if not isinstance(customers, (int, float)) or customers <= 0:
        raise ValueError("acquisition.new_customers must be positive")
    for field in ("attributable_spend", "fully_loaded_spend"):
        nonnegative(f"acquisition.{field}", acquisition[field])
    if acquisition["fully_loaded_spend"] < acquisition["attributable_spend"]:
        raise ValueError("fully_loaded_spend cannot be lower than attributable_spend")
    if not acquisition["source_or_assumption_ids"]:
        raise ValueError("acquisition.source_or_assumption_ids must be non-empty")

    channel_rows = []
    channel_customers = 0
    channel_spend = 0
    paid_customers = 0
    paid_spend = 0
    for index, channel in enumerate(acquisition.get("channels", []), 1):
        require(channel, ["name", "kind", "spend", "new_customers", "source_or_assumption_ids"], f"channel {index}")
        if channel["kind"] not in CHANNEL_KINDS:
            raise ValueError(f"channel {index}: unsupported kind {channel['kind']}")
        nonnegative(f"channel {index}.spend", channel["spend"])
        nonnegative(f"channel {index}.new_customers", channel["new_customers"])
        if not channel["source_or_assumption_ids"]:
            raise ValueError(f"channel {index}.source_or_assumption_ids must be non-empty")
        channel_cac = ratio(channel["spend"], channel["new_customers"])
        channel_rows.append({"name": channel["name"], "kind": channel["kind"], "spend": channel["spend"], "new_customers": channel["new_customers"], "cac": rounded(channel_cac), "source_or_assumption_ids": channel["source_or_assumption_ids"]})
        channel_customers += channel["new_customers"]
        channel_spend += channel["spend"]
        if channel["kind"] == "paid":
            paid_customers += channel["new_customers"]
            paid_spend += channel["spend"]
    if channel_customers > customers:
        raise ValueError("channel new_customers exceed acquisition.new_customers")
    if channel_spend > acquisition["attributable_spend"]:
        raise ValueError("channel spend exceeds attributable_spend")

    attributable_cac = acquisition["attributable_spend"] / customers
    fully_loaded_cac = acquisition["fully_loaded_spend"] / customers
    selected_cac = attributable_cac if data["cac_basis"] == "attributable" else fully_loaded_cac

    cohort = data["cohort"]
    if not isinstance(cohort, list) or not cohort:
        raise ValueError("cohort must be a non-empty list")
    expected_period = 1
    previous_retention = 1.0
    period_rows = []
    cumulative_discounted = 0.0
    cumulative_undiscounted = 0.0
    payback_period = None
    basis_ids = set(acquisition["source_or_assumption_ids"])
    first_revenue = None
    for row in cohort:
        require(row, ["period", "logo_retention_rate", "revenue_per_active_customer", "gross_margin_rate", "incremental_service_cost_per_active_customer", "source_or_assumption_ids"], f"cohort period {expected_period}")
        if row["period"] != expected_period:
            raise ValueError(f"cohort periods must be sequential from 1; expected {expected_period}")
        retention = row["logo_retention_rate"]
        rate(f"period {expected_period}.logo_retention_rate", retention)
        if retention > previous_retention:
            raise ValueError(f"period {expected_period}: logo retention cannot increase")
        for field in ("revenue_per_active_customer", "incremental_service_cost_per_active_customer"):
            nonnegative(f"period {expected_period}.{field}", row[field])
        rate(f"period {expected_period}.gross_margin_rate", row["gross_margin_rate"])
        if not row["source_or_assumption_ids"]:
            raise ValueError(f"period {expected_period}.source_or_assumption_ids must be non-empty")
        basis_ids.update(row["source_or_assumption_ids"])

        active_customers = customers * retention
        revenue = active_customers * row["revenue_per_active_customer"]
        contribution_per_active = row["revenue_per_active_customer"] * row["gross_margin_rate"] - row["incremental_service_cost_per_active_customer"]
        if contribution_per_active < 0:
            raise ValueError(f"period {expected_period}: contribution per active customer is negative")
        contribution_per_acquired = retention * contribution_per_active
        discounted = contribution_per_acquired / ((1 + discount) ** (expected_period - 1))
        cumulative_undiscounted += contribution_per_acquired
        cumulative_discounted += discounted
        if payback_period is None and cumulative_discounted >= selected_cac:
            payback_period = expected_period
        if first_revenue is None:
            first_revenue = revenue
        period_rows.append({
            "period": expected_period,
            "logo_retention_rate": retention,
            "active_customers": rounded(active_customers),
            "revenue": rounded(revenue),
            "contribution_per_active_customer": rounded(contribution_per_active),
            "contribution_per_acquired_customer": rounded(contribution_per_acquired),
            "discounted_contribution_per_acquired_customer": rounded(discounted),
            "cumulative_discounted_contribution_per_acquired_customer": rounded(cumulative_discounted),
            "source_or_assumption_ids": row["source_or_assumption_ids"],
        })
        previous_retention = retention
        expected_period += 1

    ltv = cumulative_discounted
    output = {
        "unit_name": data["unit_name"],
        "period_name": data["period_name"],
        "currency": data["currency"],
        "cac_basis_used_for_decision": data["cac_basis"],
        "acquisition": {
            "new_customers": customers,
            "attributable_spend": acquisition["attributable_spend"],
            "fully_loaded_spend": acquisition["fully_loaded_spend"],
            "paid_spend": paid_spend,
            "paid_customers": paid_customers,
            "attributable_cac": rounded(attributable_cac),
            "fully_loaded_cac": rounded(fully_loaded_cac),
            "paid_cac": rounded(ratio(paid_spend, paid_customers)),
            "unallocated_customers": rounded(customers - channel_customers),
            "unallocated_fully_loaded_spend": rounded(acquisition["fully_loaded_spend"] - channel_spend),
            "channels": channel_rows,
        },
        "unit_economics": {
            "selected_cac": rounded(selected_cac),
            "undiscounted_cohort_ltv_contribution": rounded(cumulative_undiscounted),
            "discounted_cohort_ltv_contribution": rounded(ltv),
            "ltv_to_cac": rounded(ratio(ltv, selected_cac)),
            "cac_payback_periods": payback_period,
            "payback_reached_within_horizon": payback_period is not None,
            "ending_logo_retention_rate": cohort[-1]["logo_retention_rate"],
            "ending_cohort_revenue_retention_rate": rounded(ratio(period_rows[-1]["revenue"], first_revenue)),
            "modeled_horizon_periods": len(cohort),
        },
        "cohort_periods": period_rows,
        "source_or_assumption_ids": [],
        "warnings": [],
    }
    if payback_period is None:
        output["warnings"].append("CAC payback is not reached within the modeled cohort horizon")

    recurring = data.get("recurring_revenue")
    if recurring is not None:
        require(recurring, ["starting_mrr", "new_mrr", "expansion_mrr", "contraction_mrr", "churned_mrr", "source_or_assumption_ids"], "recurring_revenue")
        for field in ("starting_mrr", "new_mrr", "expansion_mrr", "contraction_mrr", "churned_mrr"):
            nonnegative(f"recurring_revenue.{field}", recurring[field])
        start = recurring["starting_mrr"]
        if start <= 0:
            raise ValueError("recurring_revenue.starting_mrr must be positive")
        if recurring["contraction_mrr"] + recurring["churned_mrr"] > start:
            raise ValueError("contraction_mrr plus churned_mrr cannot exceed starting_mrr")
        if not recurring["source_or_assumption_ids"]:
            raise ValueError("recurring_revenue.source_or_assumption_ids must be non-empty")
        periods_per_year = recurring.get("periods_per_year", 12)
        if not isinstance(periods_per_year, (int, float)) or periods_per_year <= 0:
            raise ValueError("recurring_revenue.periods_per_year must be positive")
        ending = start + recurring["new_mrr"] + recurring["expansion_mrr"] - recurring["contraction_mrr"] - recurring["churned_mrr"]
        output["recurring_revenue"] = {
            "starting_mrr": start,
            "new_mrr": recurring["new_mrr"],
            "expansion_mrr": recurring["expansion_mrr"],
            "contraction_mrr": recurring["contraction_mrr"],
            "churned_mrr": recurring["churned_mrr"],
            "periods_per_year": periods_per_year,
            "ending_mrr": rounded(ending),
            "arr_run_rate": rounded(ending * periods_per_year),
            "gross_revenue_retention": rounded((start - recurring["contraction_mrr"] - recurring["churned_mrr"]) / start),
            "net_revenue_retention": rounded((start + recurring["expansion_mrr"] - recurring["contraction_mrr"] - recurring["churned_mrr"]) / start),
            "mrr_growth_rate": rounded((ending - start) / start),
            "source_or_assumption_ids": recurring["source_or_assumption_ids"],
        }
        basis_ids.update(recurring["source_or_assumption_ids"])

    cash = data.get("cash")
    if cash is not None:
        require(cash, ["cash_balance", "cash_inflow_per_period", "cash_outflow_per_period", "source_or_assumption_ids"], "cash")
        for field in ("cash_balance", "cash_inflow_per_period", "cash_outflow_per_period"):
            nonnegative(f"cash.{field}", cash[field])
        if not cash["source_or_assumption_ids"]:
            raise ValueError("cash.source_or_assumption_ids must be non-empty")
        net_burn = max(cash["cash_outflow_per_period"] - cash["cash_inflow_per_period"], 0)
        output["cash"] = {
            "cash_balance": cash["cash_balance"],
            "cash_inflow_per_period": cash["cash_inflow_per_period"],
            "cash_outflow_per_period": cash["cash_outflow_per_period"],
            "net_burn_per_period": rounded(net_burn),
            "net_cash_generation_per_period": rounded(max(cash["cash_inflow_per_period"] - cash["cash_outflow_per_period"], 0)),
            "runway_periods": rounded(ratio(cash["cash_balance"], net_burn)),
            "source_or_assumption_ids": cash["source_or_assumption_ids"],
        }
        basis_ids.update(cash["source_or_assumption_ids"])

    thresholds = data.get("decision_thresholds", {})
    threshold_results = []
    if any(key in thresholds for key in ("minimum_ltv_to_cac", "maximum_payback_periods")):
        if not thresholds.get("source_or_assumption_ids"):
            raise ValueError("decision_thresholds.source_or_assumption_ids must be non-empty")
        basis_ids.update(thresholds["source_or_assumption_ids"])
    if "minimum_ltv_to_cac" in thresholds:
        nonnegative("decision_thresholds.minimum_ltv_to_cac", thresholds["minimum_ltv_to_cac"])
        actual = output["unit_economics"]["ltv_to_cac"]
        threshold_results.append({"metric": "ltv_to_cac", "operator": ">=", "threshold": thresholds["minimum_ltv_to_cac"], "actual": actual, "pass": actual is not None and actual >= thresholds["minimum_ltv_to_cac"], "source_or_assumption_ids": thresholds["source_or_assumption_ids"]})
    if "maximum_payback_periods" in thresholds:
        nonnegative("decision_thresholds.maximum_payback_periods", thresholds["maximum_payback_periods"])
        actual = payback_period
        threshold_results.append({"metric": "cac_payback_periods", "operator": "<=", "threshold": thresholds["maximum_payback_periods"], "actual": actual, "pass": actual is not None and actual <= thresholds["maximum_payback_periods"], "source_or_assumption_ids": thresholds["source_or_assumption_ids"]})
    output["decision_threshold_results"] = threshold_results
    if not threshold_results:
        output["warnings"].append("No case-specific unit-economics decision thresholds were supplied")
    for channel in channel_rows:
        basis_ids.update(channel["source_or_assumption_ids"])
    output["source_or_assumption_ids"] = sorted(basis_ids)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    try:
        result = calculate(json.loads(args.input.read_text(encoding="utf-8")))
    except (ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Input error: {exc}") from exc
    rendered = json.dumps(result, ensure_ascii=False, indent=2 if args.pretty or args.output else None, allow_nan=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Wrote unit economics -> {args.output}")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
