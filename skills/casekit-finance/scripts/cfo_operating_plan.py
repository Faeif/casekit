#!/usr/bin/env python3
"""Create a cohort-to-cash operating plan with cash, AR, and variance reconciliation."""

import argparse
import json
from pathlib import Path


def require(mapping, fields, context):
    missing = [field for field in fields if field not in mapping]
    if missing:
        raise ValueError(f"{context}: missing fields: {', '.join(missing)}")


def number(name, value, positive=False):
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0 or (positive and value <= 0):
        qualifier = "positive" if positive else "non-negative"
        raise ValueError(f"{name} must be a {qualifier} number")


def rate(name, value):
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 1:
        raise ValueError(f"{name} must be between 0 and 1")


def rounded(value):
    return round(value, 4) if isinstance(value, float) else value


def validate_and_index(data):
    require(data, ["plan_name", "currency", "period_name", "period_count", "starting_cash", "collection_lag_periods", "source_or_assumption_ids", "cohorts", "operating_periods"], "root")
    periods = data["period_count"]
    if not isinstance(periods, int) or periods <= 0:
        raise ValueError("period_count must be a positive integer")
    number("starting_cash", data["starting_cash"])
    lag = data["collection_lag_periods"]
    if not isinstance(lag, int) or not 0 <= lag < periods:
        raise ValueError("collection_lag_periods must be an integer from 0 to period_count - 1")
    if not data["source_or_assumption_ids"]:
        raise ValueError("source_or_assumption_ids must be non-empty")

    cohort_ids = set()
    cohorts = []
    for index, cohort in enumerate(data["cohorts"], 1):
        require(cohort, ["cohort_id", "start_period", "new_customers", "price_per_active_customer", "variable_cost_per_active_customer", "retention_rates", "source_or_assumption_ids"], f"cohort {index}")
        cohort_id = str(cohort["cohort_id"]).strip()
        if not cohort_id or cohort_id in cohort_ids:
            raise ValueError(f"cohort {index}: cohort_id must be unique and non-empty")
        cohort_ids.add(cohort_id)
        start = cohort["start_period"]
        if not isinstance(start, int) or not 1 <= start <= periods:
            raise ValueError(f"cohort {cohort_id}: start_period must be within the plan")
        for field in ("new_customers", "price_per_active_customer", "variable_cost_per_active_customer"):
            number(f"cohort {cohort_id}.{field}", cohort[field])
        rates = cohort["retention_rates"]
        horizon = periods - start + 1
        if not isinstance(rates, list) or len(rates) < horizon:
            raise ValueError(f"cohort {cohort_id}: retention_rates must cover every modeled period")
        previous = 1.0
        for age, value in enumerate(rates[:horizon], 1):
            rate(f"cohort {cohort_id}.retention_rates[{age}]", value)
            if value > previous:
                raise ValueError(f"cohort {cohort_id}: retention cannot increase")
            previous = value
        if not cohort["source_or_assumption_ids"]:
            raise ValueError(f"cohort {cohort_id}: source_or_assumption_ids must be non-empty")
        cohorts.append(cohort)

    operating = {}
    for row in data["operating_periods"]:
        require(row, ["period", "fixed_cost", "acquisition_spend", "one_time_cost", "source_or_assumption_ids"], "operating_period")
        period = row["period"]
        if not isinstance(period, int) or not 1 <= period <= periods or period in operating:
            raise ValueError("operating_periods must contain each plan period exactly once")
        for field in ("fixed_cost", "acquisition_spend", "one_time_cost"):
            number(f"operating period {period}.{field}", row[field])
        if not row["source_or_assumption_ids"]:
            raise ValueError(f"operating period {period}: source_or_assumption_ids must be non-empty")
        operating[period] = row
    if set(operating) != set(range(1, periods + 1)):
        raise ValueError("operating_periods must contain each plan period exactly once")
    return periods, lag, cohorts, operating


def calculate(data):
    periods, lag, cohorts, operating = validate_and_index(data)
    recognized = []
    plan_rows = []
    ending_cash = data["starting_cash"]
    cumulative_recognized = 0.0
    cumulative_collections = 0.0
    all_ids = set(data["source_or_assumption_ids"])

    for period in range(1, periods + 1):
        active_customers = revenue = variable_cost = 0.0
        cohort_activity = []
        for cohort in cohorts:
            age = period - cohort["start_period"]
            if age < 0:
                continue
            active = cohort["new_customers"] * cohort["retention_rates"][age]
            cohort_revenue = active * cohort["price_per_active_customer"]
            cohort_variable_cost = active * cohort["variable_cost_per_active_customer"]
            active_customers += active
            revenue += cohort_revenue
            variable_cost += cohort_variable_cost
            cohort_activity.append({"cohort_id": cohort["cohort_id"], "active_customers": rounded(active), "recognized_revenue": rounded(cohort_revenue), "variable_cost": rounded(cohort_variable_cost)})
            all_ids.update(cohort["source_or_assumption_ids"])
        recognized.append(revenue)
        cash_collections = recognized[period - lag - 1] if period - lag - 1 >= 0 else 0.0
        spend = operating[period]
        all_ids.update(spend["source_or_assumption_ids"])
        gross_profit = revenue - variable_cost
        operating_result = gross_profit - spend["fixed_cost"] - spend["acquisition_spend"] - spend["one_time_cost"]
        net_cash_flow = cash_collections - variable_cost - spend["fixed_cost"] - spend["acquisition_spend"] - spend["one_time_cost"]
        ending_cash += net_cash_flow
        cumulative_recognized += revenue
        cumulative_collections += cash_collections
        accounts_receivable = cumulative_recognized - cumulative_collections
        contribution_margin = gross_profit / revenue if revenue else None
        contribution_per_active = gross_profit / active_customers if active_customers else None
        break_even_active = (spend["fixed_cost"] + spend["acquisition_spend"] + spend["one_time_cost"]) / contribution_per_active if contribution_per_active and contribution_per_active > 0 else None
        plan_rows.append({
            "period": period,
            "active_customers": rounded(active_customers),
            "recognized_revenue": rounded(revenue),
            "cash_collections": rounded(cash_collections),
            "variable_cost": rounded(variable_cost),
            "gross_profit": rounded(gross_profit),
            "contribution_margin": rounded(contribution_margin) if contribution_margin is not None else None,
            "fixed_cost": spend["fixed_cost"],
            "acquisition_spend": spend["acquisition_spend"],
            "one_time_cost": spend["one_time_cost"],
            "operating_result": rounded(operating_result),
            "net_cash_flow": rounded(net_cash_flow),
            "ending_cash": rounded(ending_cash),
            "accounts_receivable": rounded(accounts_receivable),
            "break_even_active_customers": rounded(break_even_active) if break_even_active is not None else None,
            "cohort_activity": cohort_activity,
        })

    variance_rows = []
    rows_by_period = {row["period"]: row for row in plan_rows}
    for actual in data.get("variance_actuals", []):
        require(actual, ["period", "recognized_revenue", "cash_collections", "variable_cost", "fixed_cost", "acquisition_spend", "one_time_cost", "source_or_assumption_ids"], "variance_actual")
        period = actual["period"]
        if period not in rows_by_period:
            raise ValueError("variance_actuals period must be within the plan")
        if not actual["source_or_assumption_ids"]:
            raise ValueError(f"variance actual period {period}: source_or_assumption_ids must be non-empty")
        for field in ("recognized_revenue", "cash_collections", "variable_cost", "fixed_cost", "acquisition_spend", "one_time_cost"):
            number(f"variance actual period {period}.{field}", actual[field])
        plan = rows_by_period[period]
        actual_operating_result = actual["recognized_revenue"] - actual["variable_cost"] - actual["fixed_cost"] - actual["acquisition_spend"] - actual["one_time_cost"]
        actual_net_cash_flow = actual["cash_collections"] - actual["variable_cost"] - actual["fixed_cost"] - actual["acquisition_spend"] - actual["one_time_cost"]
        variance_rows.append({
            "period": period,
            "recognized_revenue_variance": rounded(actual["recognized_revenue"] - plan["recognized_revenue"]),
            "cash_collections_variance": rounded(actual["cash_collections"] - plan["cash_collections"]),
            "variable_cost_variance": rounded(actual["variable_cost"] - plan["variable_cost"]),
            "operating_result_variance": rounded(actual_operating_result - plan["operating_result"]),
            "net_cash_flow_variance": rounded(actual_net_cash_flow - plan["net_cash_flow"]),
            "source_or_assumption_ids": actual["source_or_assumption_ids"],
        })
        all_ids.update(actual["source_or_assumption_ids"])

    ending_cash_values = [row["ending_cash"] for row in plan_rows]
    total_revenue = sum(row["recognized_revenue"] for row in plan_rows)
    total_variable_cost = sum(row["variable_cost"] for row in plan_rows)
    summary = {
        "recognized_revenue": rounded(total_revenue),
        "cash_collections": rounded(sum(row["cash_collections"] for row in plan_rows)),
        "gross_profit": rounded(total_revenue - total_variable_cost),
        "contribution_margin": rounded((total_revenue - total_variable_cost) / total_revenue) if total_revenue else None,
        "operating_result": rounded(sum(row["operating_result"] for row in plan_rows)),
        "ending_cash": rounded(plan_rows[-1]["ending_cash"]),
        "cash_trough": rounded(min(ending_cash_values)),
        "cash_trough_period": min(plan_rows, key=lambda row: row["ending_cash"])["period"],
        "ending_accounts_receivable": plan_rows[-1]["accounts_receivable"],
        "cash_break_even_period": next((row["period"] for row in plan_rows if row["net_cash_flow"] >= 0), None),
    }
    threshold_results = []
    thresholds = data.get("decision_thresholds")
    if thresholds:
        require(thresholds, ["minimum_ending_cash", "minimum_cash_trough", "minimum_contribution_margin", "source_or_assumption_ids"], "decision_thresholds")
        for field in ("minimum_ending_cash", "minimum_cash_trough", "minimum_contribution_margin"):
            number(f"decision_thresholds.{field}", thresholds[field])
        rate("decision_thresholds.minimum_contribution_margin", thresholds["minimum_contribution_margin"])
        if not thresholds["source_or_assumption_ids"]:
            raise ValueError("decision_thresholds.source_or_assumption_ids must be non-empty")
        checks = (("minimum_ending_cash", summary["ending_cash"], thresholds["minimum_ending_cash"], ">="), ("minimum_cash_trough", summary["cash_trough"], thresholds["minimum_cash_trough"], ">="), ("minimum_contribution_margin", summary["contribution_margin"], thresholds["minimum_contribution_margin"], ">="))
        for metric, actual, threshold, operator in checks:
            threshold_results.append({"metric": metric, "actual": actual, "threshold": threshold, "operator": operator, "pass": actual is not None and actual >= threshold})
        all_ids.update(thresholds["source_or_assumption_ids"])

    return {
        "plan_name": data["plan_name"], "currency": data["currency"], "period_name": data["period_name"], "period_count": periods,
        "starting_cash": data["starting_cash"], "collection_lag_periods": lag, "periods": plan_rows, "summary": summary,
        "variance": variance_rows, "decision_threshold_results": threshold_results,
        "source_or_assumption_ids": sorted(all_ids),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    try:
        output = calculate(json.loads(args.input.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise SystemExit(f"CFO operating-plan error: {exc}")
    rendered = json.dumps(output, ensure_ascii=False, indent=2 if args.pretty or args.output else None)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Wrote CFO operating plan: {args.output}")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
