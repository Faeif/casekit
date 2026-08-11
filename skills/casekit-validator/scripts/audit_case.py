#!/usr/bin/env python3
"""Audit CaseKit ledgers and deck spec for cross-artifact integrity."""

import argparse
import csv
import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import urlparse


ID_PATTERNS = {
    "claim_id": r"CLM-\d{3,}",
    "source_id": r"SRC-\d{3,}",
    "assumption_id": r"ASM-\d{3,}",
    "metric_id": r"MET-\d{3,}",
    "decision_id": r"DEC-\d{3,}",
    "risk_id": r"RSK-\d{3,}",
    "premise_id": r"PRM-\d{3,}",
    "experiment_id": r"EXP-\d{3,}",
    "option_id": r"OPT-\d{3,}",
    "integration_id": r"INT-\d{3,}",
    "idea_id": r"IDEA-\d{3,}",
}

FILES = {
    "evidence": ("01-evidence-ledger.csv", ["claim_id", "claim", "source_id", "source_type", "url", "accessed_date", "page_or_section", "quality", "recency", "relevance", "status"], []),
    "assumptions": ("02-assumptions.csv", ["assumption_id", "variable", "unit", "low", "base", "high", "basis", "source_ids", "confidence", "sensitivity", "validation_method", "owner", "status"], ["assumption_id"]),
    "metrics": ("03-metric-tree.csv", ["metric_id", "parent_metric_id", "metric", "metric_type", "formula", "unit", "source_or_assumption_ids", "owner"], ["metric_id"]),
    "decisions": ("04-decision-log.csv", ["decision_id", "date", "decision", "alternatives", "criteria", "rationale", "evidence_and_assumption_ids", "owner", "status"], ["decision_id"]),
    "risks": ("05-risk-register.csv", ["risk_id", "risk", "category", "likelihood", "impact", "mitigation", "contingency", "owner", "status"], ["risk_id"]),
    "premises": ("08-premises.csv", ["premise_id", "premise", "type", "evidence_ids", "confidence", "decision_impact", "falsification_test", "owner", "status"], ["premise_id"]),
    "experiments": ("09-experiments.csv", ["experiment_id", "premise_ids", "method", "pass_threshold", "stop_threshold", "owner", "deadline", "status"], ["experiment_id"]),
}

ENUMS = {
    "confidence": {"low", "medium", "high"},
    "sensitivity": {"low", "medium", "high"},
    "quality": {"low", "medium", "high"},
    "recency": {"low", "medium", "high"},
    "relevance": {"low", "medium", "high"},
    "metric_type": {"north-star", "outcome", "driver", "guardrail", "diagnostic", "capacity"},
    "likelihood": {"low", "medium", "high"},
    "impact": {"low", "medium", "high"},
}

GROUP_ENUMS = {
    "evidence": {"status": {"verified", "partially-verified", "unverified", "superseded"}},
    "assumptions": {
        "basis": {"primary-research", "secondary-research", "analogy", "derived", "management-target", "team-judgment"},
        "status": {"open", "validated", "rejected", "superseded"},
    },
    "decisions": {"status": {"proposed", "approved", "rejected", "superseded", "revisit"}},
    "risks": {"status": {"open", "mitigated", "accepted", "closed"}},
    "premises": {
        "type": {"desirability", "feasibility", "viability", "usability", "legal", "operational", "growth"},
        "status": {"open", "validated", "falsified", "superseded"},
    },
    "experiments": {"status": {"planned", "running", "passed", "iterated", "stopped", "closed"}},
}

NONEMPTY = {
    "evidence": {"claim_id", "claim", "source_id", "publisher", "title", "url", "accessed_date", "page_or_section", "interpretation", "owner"},
    "assumptions": {"assumption_id", "variable", "definition", "unit", "low", "base", "high", "basis", "validation_method", "owner", "status"},
    "metrics": {"metric_id", "metric", "metric_type", "formula", "unit", "time_horizon", "source_or_assumption_ids", "owner"},
    "decisions": {"decision_id", "date", "decision", "alternatives", "criteria", "rationale", "evidence_and_assumption_ids", "owner", "status"},
    "risks": {"risk_id", "risk", "category", "likelihood", "impact", "mitigation", "contingency", "owner", "status"},
    "premises": {"premise_id", "premise", "type", "confidence", "decision_impact", "falsification_test", "owner", "status"},
    "experiments": {"experiment_id", "premise_ids", "method", "pass_threshold", "stop_threshold", "owner", "deadline", "status"},
}


def split_ids(value):
    return [part.strip() for part in re.split(r"[|;,\s]+", value or "") if part.strip()]


def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader)


def is_blank(row):
    return not any((value or "").strip() for value in row.values())


def numeric(value):
    return float((value or "").replace(",", "").strip())


def close_enough(left, right):
    return abs(left - right) <= max(abs(right) * 1e-6, 1e-6)


def audit(project):
    errors, warnings = [], []
    tables, locations, ids = {}, {}, set()
    official = project / "03-OFFICIAL"
    if not official.is_dir():
        official = project

    for group, (filename, required, unique_fields) in FILES.items():
        path = official / filename
        if not path.exists():
            errors.append(f"{filename}: missing required artifact")
            continue
        fields, rows = read_csv(path)
        rows = [row for row in rows if not is_blank(row)]
        missing = [field for field in required if field not in fields]
        if missing:
            errors.append(f"{filename}: missing columns {', '.join(missing)}")
            continue
        tables[group] = rows
        for line, row in enumerate(rows, 2):
            for field in NONEMPTY[group]:
                if not (row.get(field) or "").strip():
                    errors.append(f"{filename}:{line}: blank required value {field}")
            for field in unique_fields:
                value = (row.get(field) or "").strip()
                if not value:
                    errors.append(f"{filename}:{line}: blank {field}")
                    continue
                pattern = ID_PATTERNS[field]
                if not re.fullmatch(pattern, value):
                    errors.append(f"{filename}:{line}: invalid {field} '{value}'")
                if value in locations:
                    errors.append(f"{filename}:{line}: duplicate ID {value}; first at {locations[value]}")
                else:
                    locations[value] = f"{filename}:{line}"
                    ids.add(value)
            for field, allowed in ENUMS.items():
                if field in fields and (row.get(field) or "").strip():
                    value = row[field].strip().lower()
                    if value not in allowed:
                        errors.append(f"{filename}:{line}: invalid {field} '{row[field]}'")
            for field, allowed in GROUP_ENUMS.get(group, {}).items():
                value = (row.get(field) or "").strip().lower()
                if value and value not in allowed:
                    errors.append(f"{filename}:{line}: invalid {field} '{row[field]}'")

    evidence_pairs = set()
    sources, claims = set(), set()
    for line, row in enumerate(tables.get("evidence", []), 2):
        claim_id, source_id = row["claim_id"].strip(), row["source_id"].strip()
        for field, value in (("claim_id", claim_id), ("source_id", source_id)):
            if not re.fullmatch(ID_PATTERNS[field], value):
                errors.append(f"01-evidence-ledger.csv:{line}: invalid {field} '{value}'")
        pair = (claim_id, source_id)
        if pair in evidence_pairs:
            errors.append(f"01-evidence-ledger.csv:{line}: duplicate claim-source pair {claim_id}/{source_id}")
        evidence_pairs.add(pair)
        claims.add(claim_id)
        sources.add(source_id)
        ids.update((claim_id, source_id))
        url = row["url"].strip()
        parsed = urlparse(url)
        if parsed.scheme not in {"https", "http"} or not parsed.netloc:
            errors.append(f"01-evidence-ledger.csv:{line}: invalid source URL '{url}'")
        try:
            accessed = date.fromisoformat(row["accessed_date"].strip())
            if accessed > date.today():
                errors.append(f"01-evidence-ledger.csv:{line}: accessed_date is in the future")
        except ValueError:
            errors.append(f"01-evidence-ledger.csv:{line}: accessed_date must be YYYY-MM-DD")
        if not row["page_or_section"].strip():
            errors.append(f"01-evidence-ledger.csv:{line}: missing page_or_section")

    assumption_ids = {row["assumption_id"].strip() for row in tables.get("assumptions", [])}
    metric_ids = {row["metric_id"].strip() for row in tables.get("metrics", [])}
    metric_rows = {row["metric_id"].strip(): row for row in tables.get("metrics", [])}
    premise_ids = {row["premise_id"].strip() for row in tables.get("premises", [])}
    risk_ids = {row["risk_id"].strip() for row in tables.get("risks", [])}

    for line, row in enumerate(tables.get("assumptions", []), 2):
        try:
            low, base, high = [numeric(row[key]) for key in ("low", "base", "high")]
            if not low <= base <= high:
                errors.append(f"02-assumptions.csv:{line}: expected low <= base <= high")
        except ValueError:
            warnings.append(f"02-assumptions.csv:{line}: non-numeric scenario; verify ordering manually")
        for ref in split_ids(row["source_ids"]):
            if ref not in sources:
                errors.append(f"02-assumptions.csv:{line}: unresolved source reference {ref}")

    for line, row in enumerate(tables.get("metrics", []), 2):
        parent = row["parent_metric_id"].strip()
        if parent and parent not in metric_ids:
            errors.append(f"03-metric-tree.csv:{line}: unresolved parent metric {parent}")
        if not row["formula"].strip():
            errors.append(f"03-metric-tree.csv:{line}: missing formula")
        for ref in split_ids(row["source_or_assumption_ids"]):
            if ref not in sources | assumption_ids | metric_ids:
                errors.append(f"03-metric-tree.csv:{line}: unresolved model reference {ref}")

    for line, row in enumerate(tables.get("decisions", []), 2):
        try:
            date.fromisoformat(row.get("date", "").strip())
        except ValueError:
            errors.append(f"04-decision-log.csv:{line}: date must be YYYY-MM-DD")
        for ref in split_ids(row["evidence_and_assumption_ids"]):
            if ref not in claims | sources | assumption_ids | metric_ids | premise_ids:
                errors.append(f"04-decision-log.csv:{line}: unresolved decision reference {ref}")

    for line, row in enumerate(tables.get("premises", []), 2):
        for ref in split_ids(row["evidence_ids"]):
            if ref not in claims | sources:
                errors.append(f"08-premises.csv:{line}: unresolved evidence reference {ref}")

    for line, row in enumerate(tables.get("experiments", []), 2):
        try:
            date.fromisoformat(row["deadline"].strip())
        except ValueError:
            errors.append(f"09-experiments.csv:{line}: deadline must be YYYY-MM-DD")
        for ref in split_ids(row["premise_ids"]):
            if ref not in premise_ids:
                errors.append(f"09-experiments.csv:{line}: unresolved premise reference {ref}")

    option_path = official / "option-portfolio.csv"
    option_count = 0
    if option_path.exists():
        option_fields, option_rows = read_csv(option_path)
        option_rows = [row for row in option_rows if not is_blank(row)]
        required_option_fields = {
            "option_id", "option_name", "rubric_fit", "impact", "feasibility", "viability",
            "differentiation", "evidence_confidence", "evidence_ids", "assumption_ids", "status",
        }
        missing_option_fields = sorted(required_option_fields - set(option_fields))
        if missing_option_fields:
            errors.append(f"option-portfolio.csv: missing columns {', '.join(missing_option_fields)}")
        else:
            option_ids = set()
            for line, row in enumerate(option_rows, 2):
                option_id = row["option_id"].strip()
                if not re.fullmatch(ID_PATTERNS["option_id"], option_id):
                    errors.append(f"option-portfolio.csv:{line}: invalid option_id '{option_id}'")
                if option_id in option_ids:
                    errors.append(f"option-portfolio.csv:{line}: duplicate option_id {option_id}")
                option_ids.add(option_id)
                if not row["option_name"].strip():
                    errors.append(f"option-portfolio.csv:{line}: blank option_name")
                for field in ("rubric_fit", "impact", "feasibility", "viability", "differentiation", "evidence_confidence"):
                    try:
                        value = float(row[field])
                        if not 1 <= value <= 5:
                            errors.append(f"option-portfolio.csv:{line}: {field} must be between 1 and 5")
                    except ValueError:
                        errors.append(f"option-portfolio.csv:{line}: {field} must be numeric")
                for ref in split_ids(row["evidence_ids"]):
                    if ref not in claims | sources:
                        errors.append(f"option-portfolio.csv:{line}: unresolved evidence reference {ref}")
                for ref in split_ids(row["assumption_ids"]):
                    if ref not in assumption_ids:
                        errors.append(f"option-portfolio.csv:{line}: unresolved assumption reference {ref}")
                if row["status"].strip().lower() not in {"proposed", "chosen", "rejected", "revisit"}:
                    errors.append(f"option-portfolio.csv:{line}: invalid status '{row['status']}'")
            if option_rows and sum(row["status"].strip().lower() == "chosen" for row in option_rows) != 1:
                errors.append("option-portfolio.csv: exactly one nonblank option must have status 'chosen'")
            option_count = len(option_rows)

    integration_path = official / "integration-contract.csv"
    integration_count = 0
    if integration_path.exists():
        integration_fields, integration_rows = read_csv(integration_path)
        integration_rows = [row for row in integration_rows if not is_blank(row)]
        required_integration_fields = {
            "integration_id", "system", "purpose", "user_journey_step", "delivery_level", "status",
            "interface_type", "data_in", "data_out", "owner", "dependency", "fallback",
            "demo_evidence", "source_or_assumption_ids", "risk_id", "go_live_gate",
        }
        missing_integration_fields = sorted(required_integration_fields - set(integration_fields))
        if missing_integration_fields:
            errors.append(f"integration-contract.csv: missing columns {', '.join(missing_integration_fields)}")
        else:
            integration_ids = set()
            valid_statuses = {"real", "sandbox", "mocked", "planned", "blocked", "deprecated"}
            valid_levels = {"concept", "prototype", "pilot", "production"}
            for line, row in enumerate(integration_rows, 2):
                integration_id = row["integration_id"].strip()
                if not re.fullmatch(ID_PATTERNS["integration_id"], integration_id):
                    errors.append(f"integration-contract.csv:{line}: invalid integration_id '{integration_id}'")
                if integration_id in integration_ids:
                    errors.append(f"integration-contract.csv:{line}: duplicate integration_id {integration_id}")
                integration_ids.add(integration_id)
                for field in ("system", "purpose", "user_journey_step", "interface_type", "data_in", "data_out", "owner", "dependency", "fallback", "demo_evidence", "go_live_gate"):
                    if not row[field].strip():
                        errors.append(f"integration-contract.csv:{line}: blank required value {field}")
                status = row["status"].strip().lower()
                if status not in valid_statuses:
                    errors.append(f"integration-contract.csv:{line}: invalid status '{row['status']}'")
                if row["delivery_level"].strip().lower() not in valid_levels:
                    errors.append(f"integration-contract.csv:{line}: invalid delivery_level '{row['delivery_level']}'")
                if status == "real":
                    for field in ("auth_method", "partner_owner", "consent_or_legal_basis", "rate_limit_or_sla", "cost_driver"):
                        if field in integration_fields and not row[field].strip():
                            errors.append(f"integration-contract.csv:{line}: real integration requires {field}")
                for ref in split_ids(row["source_or_assumption_ids"]):
                    if ref not in sources | assumption_ids | metric_ids:
                        errors.append(f"integration-contract.csv:{line}: unresolved source or assumption reference {ref}")
                risk_id = row["risk_id"].strip()
                if risk_id not in risk_ids:
                    errors.append(f"integration-contract.csv:{line}: unresolved risk reference {risk_id}")
            integration_count = len(integration_rows)

    idea_path = official / "idea-backlog.csv"
    idea_count = 0
    if idea_path.exists():
        idea_fields, idea_rows = read_csv(idea_path)
        idea_rows = [row for row in idea_rows if not is_blank(row)]
        required_idea_fields = {
            "idea_id", "title", "status", "origin", "problem_or_hypothesis", "proposed_mechanism", "owner",
            "required_evidence_or_test", "experiment_ids", "decision_id", "promoted_artifacts", "next_action", "rationale_or_disposition",
        }
        missing_idea_fields = sorted(required_idea_fields - set(idea_fields))
        if missing_idea_fields:
            errors.append(f"idea-backlog.csv: missing columns {', '.join(missing_idea_fields)}")
        else:
            valid_idea_statuses = {"exploring", "proposed", "accepted-for-test", "accepted-for-case", "rejected", "parked"}
            idea_ids = set()
            experiment_ids = {row["experiment_id"].strip() for row in tables.get("experiments", [])}
            decision_ids = {row["decision_id"].strip() for row in tables.get("decisions", [])}
            for line, row in enumerate(idea_rows, 2):
                idea_id = row["idea_id"].strip()
                if not re.fullmatch(ID_PATTERNS["idea_id"], idea_id):
                    errors.append(f"idea-backlog.csv:{line}: invalid idea_id '{idea_id}'")
                if idea_id in idea_ids:
                    errors.append(f"idea-backlog.csv:{line}: duplicate idea_id {idea_id}")
                idea_ids.add(idea_id)
                for field in ("title", "status", "origin", "problem_or_hypothesis", "proposed_mechanism", "owner", "required_evidence_or_test", "next_action"):
                    if not row[field].strip():
                        errors.append(f"idea-backlog.csv:{line}: blank required value {field}")
                status = row["status"].strip().lower()
                if status not in valid_idea_statuses:
                    errors.append(f"idea-backlog.csv:{line}: invalid status '{row['status']}'")
                experiment_refs = split_ids(row["experiment_ids"])
                if status == "accepted-for-test" and not experiment_refs:
                    errors.append(f"idea-backlog.csv:{line}: accepted-for-test requires experiment_ids")
                for ref in experiment_refs:
                    if ref not in experiment_ids:
                        errors.append(f"idea-backlog.csv:{line}: unresolved experiment reference {ref}")
                decision_id = row["decision_id"].strip()
                if status == "accepted-for-case" and not decision_id:
                    errors.append(f"idea-backlog.csv:{line}: accepted-for-case requires decision_id")
                if decision_id and decision_id not in decision_ids:
                    errors.append(f"idea-backlog.csv:{line}: unresolved decision reference {decision_id}")
                if status == "accepted-for-case" and not row["promoted_artifacts"].strip():
                    errors.append(f"idea-backlog.csv:{line}: accepted-for-case requires promoted_artifacts")
            idea_count = len(idea_rows)

    engineering_profile_path = official / "engineering" / "00-engineering-profile.json"
    engineering_level = None
    if engineering_profile_path.exists():
        try:
            engineering_profile = json.loads(engineering_profile_path.read_text(encoding="utf-8"))
            engineering_level = str(engineering_profile.get("delivery_level", "")).lower()
            if engineering_level not in {"concept", "prototype", "pilot", "production"}:
                errors.append("engineering/00-engineering-profile.json: delivery_level must be concept, prototype, pilot, or production")
            if not str(engineering_profile.get("architecture_style", "")).strip():
                errors.append("engineering/00-engineering-profile.json: architecture_style is required")
        except (json.JSONDecodeError, AttributeError):
            errors.append("engineering/00-engineering-profile.json: invalid JSON")

    if engineering_level in {"pilot", "production"}:
        required_engineering_artifacts = {
            "architecture.md", "nfr-slo.md", "threat-model.md", "data-lifecycle.md", "api-event-contracts.md",
            "deployment-runbook.md", "test-matrix.csv", "observability.md", "production-readiness.csv",
        }
        for filename in sorted(required_engineering_artifacts):
            if not (official / "engineering" / filename).exists():
                errors.append(f"engineering: missing {engineering_level} artifact engineering/{filename}")

    readiness_path = official / "engineering" / "production-readiness.csv"
    if engineering_level == "production" and readiness_path.exists():
        readiness_fields, readiness_rows = read_csv(readiness_path)
        readiness_rows = [row for row in readiness_rows if not is_blank(row)]
        required_readiness_fields = {"area", "requirement", "measurement", "owner", "status", "evidence_ids", "risk_id", "rollback_or_fallback"}
        missing_readiness_fields = sorted(required_readiness_fields - set(readiness_fields))
        if missing_readiness_fields:
            errors.append(f"engineering/production-readiness.csv: missing columns {', '.join(missing_readiness_fields)}")
        else:
            required_areas = {"reliability", "security", "privacy-data", "testing", "observability", "deployment", "incident-response", "cost-capacity"}
            by_area = {row.get("area", "").strip(): row for row in readiness_rows}
            for area in sorted(required_areas):
                row = by_area.get(area)
                if row is None:
                    errors.append(f"engineering/production-readiness.csv: missing required area {area}")
                    continue
                for field in required_readiness_fields - {"area"}:
                    if not row.get(field, "").strip():
                        errors.append(f"engineering/production-readiness.csv: {area} blank {field}")
                if row.get("status", "").strip().lower() != "passed":
                    errors.append(f"engineering/production-readiness.csv: {area} must have status passed for production")
                for ref in split_ids(row.get("evidence_ids", "")):
                    if ref not in claims | sources | assumption_ids | metric_ids:
                        errors.append(f"engineering/production-readiness.csv: {area} unresolved evidence reference {ref}")
                if row.get("risk_id", "").strip() not in risk_ids:
                    errors.append(f"engineering/production-readiness.csv: {area} unresolved risk reference {row.get('risk_id', '').strip()}")

    deck_path = official / "12-deck-spec.json"
    if deck_path.exists():
        try:
            deck = json.loads(deck_path.read_text(encoding="utf-8"))
            slides = deck.get("slides", [])
            if not slides:
                errors.append("12-deck-spec.json: slides must be non-empty")
            for index, slide in enumerate(slides, 1):
                if not slide.get("headline"):
                    errors.append(f"12-deck-spec.json: slide {index} missing headline")
                for ref in slide.get("evidence_ids", []):
                    if ref not in ids:
                        errors.append(f"12-deck-spec.json: slide {index} unresolved evidence ID {ref}")
                bindings = list(slide.get("metric_bindings", []))
                bindings.extend(stage for stage in slide.get("stages", []) if stage.get("metric_id"))
                if slide.get("type") == "metric" and not bindings:
                    errors.append(f"12-deck-spec.json: slide {index} metric slide has no numeric binding")
                for binding in bindings:
                    metric_id = binding.get("metric_id", "")
                    scenario = binding.get("scenario", "base")
                    if metric_id not in metric_rows:
                        errors.append(f"12-deck-spec.json: slide {index} unresolved bound metric {metric_id}")
                        continue
                    if scenario not in {"low", "base", "high"}:
                        errors.append(f"12-deck-spec.json: slide {index} invalid metric scenario {scenario}")
                        continue
                    try:
                        deck_value = numeric(str(binding.get("value", "")))
                        ledger_value = numeric(metric_rows[metric_id].get(scenario, ""))
                        tolerance = max(abs(ledger_value) * 1e-9, 1e-9)
                        if abs(deck_value - ledger_value) > tolerance:
                            errors.append(f"12-deck-spec.json: slide {index} number drift for {metric_id}/{scenario}: deck={deck_value:g} ledger={ledger_value:g}")
                    except ValueError:
                        errors.append(f"12-deck-spec.json: slide {index} non-numeric binding for {metric_id}/{scenario}")
                if len(slide.get("body", [])) > 6:
                    warnings.append(f"12-deck-spec.json: slide {index} has more than 6 body items")
        except (json.JSONDecodeError, AttributeError) as exc:
            errors.append(f"12-deck-spec.json: invalid JSON structure: {exc}")
    else:
        warnings.append("12-deck-spec.json: not present; required before deck freeze")

    economics_path = official / "14-unit-economics.json"
    if economics_path.exists():
        try:
            economics = json.loads(economics_path.read_text(encoding="utf-8"))
            require_sections = {"acquisition", "unit_economics", "cohort_periods", "source_or_assumption_ids"}
            missing_sections = require_sections - set(economics)
            if missing_sections:
                errors.append(f"14-unit-economics.json: missing sections {', '.join(sorted(missing_sections))}")
            else:
                acquisition = economics["acquisition"]
                unit = economics["unit_economics"]
                for field in ("selected_cac", "discounted_cohort_ltv_contribution", "ltv_to_cac", "modeled_horizon_periods"):
                    if field not in unit:
                        errors.append(f"14-unit-economics.json: missing unit_economics.{field}")
                try:
                    cac = float(unit["selected_cac"])
                    ltv = float(unit["discounted_cohort_ltv_contribution"])
                    reported_ratio = float(unit["ltv_to_cac"])
                    if cac <= 0 or ltv < 0:
                        errors.append("14-unit-economics.json: CAC must be positive and LTV non-negative")
                    elif not close_enough(reported_ratio, ltv / cac):
                        errors.append("14-unit-economics.json: LTV:CAC does not reconcile to LTV and selected CAC")
                except (KeyError, TypeError, ValueError):
                    errors.append("14-unit-economics.json: unit-economics values must be numeric")
                try:
                    customers = float(acquisition["new_customers"])
                    attributable_cac = float(acquisition["attributable_spend"]) / customers
                    fully_loaded_cac = float(acquisition["fully_loaded_spend"]) / customers
                    if not close_enough(float(acquisition["attributable_cac"]), attributable_cac):
                        errors.append("14-unit-economics.json: attributable CAC does not reconcile")
                    if not close_enough(float(acquisition["fully_loaded_cac"]), fully_loaded_cac):
                        errors.append("14-unit-economics.json: fully loaded CAC does not reconcile")
                    paid_customers = float(acquisition.get("paid_customers", 0))
                    if paid_customers and not close_enough(float(acquisition["paid_cac"]), float(acquisition["paid_spend"]) / paid_customers):
                        errors.append("14-unit-economics.json: paid CAC does not reconcile")
                    selected_expected = attributable_cac if economics.get("cac_basis_used_for_decision") == "attributable" else fully_loaded_cac
                    if not close_enough(float(unit["selected_cac"]), selected_expected):
                        errors.append("14-unit-economics.json: selected CAC does not match declared CAC basis")
                except (KeyError, TypeError, ValueError, ZeroDivisionError):
                    errors.append("14-unit-economics.json: acquisition values cannot be reconciled")
                if unit.get("modeled_horizon_periods") != len(economics.get("cohort_periods", [])):
                    errors.append("14-unit-economics.json: modeled horizon does not match cohort rows")
                recurring = economics.get("recurring_revenue")
                if recurring:
                    try:
                        start = float(recurring["starting_mrr"])
                        ending = start + float(recurring["new_mrr"]) + float(recurring["expansion_mrr"]) - float(recurring["contraction_mrr"]) - float(recurring["churned_mrr"])
                        grr = (start - float(recurring["contraction_mrr"]) - float(recurring["churned_mrr"])) / start
                        nrr = (start + float(recurring["expansion_mrr"]) - float(recurring["contraction_mrr"]) - float(recurring["churned_mrr"])) / start
                        if not close_enough(float(recurring["ending_mrr"]), ending):
                            errors.append("14-unit-economics.json: ending MRR does not reconcile")
                        if not close_enough(float(recurring["gross_revenue_retention"]), grr):
                            errors.append("14-unit-economics.json: GRR does not reconcile")
                        if not close_enough(float(recurring["net_revenue_retention"]), nrr):
                            errors.append("14-unit-economics.json: NRR does not reconcile")
                        if not close_enough(float(recurring["arr_run_rate"]), ending * float(recurring["periods_per_year"])):
                            errors.append("14-unit-economics.json: ARR run rate does not reconcile")
                    except (KeyError, TypeError, ValueError, ZeroDivisionError):
                        errors.append("14-unit-economics.json: recurring-revenue values cannot be reconciled")
                cash = economics.get("cash")
                if cash:
                    try:
                        burn = max(float(cash["cash_outflow_per_period"]) - float(cash["cash_inflow_per_period"]), 0)
                        if not close_enough(float(cash["net_burn_per_period"]), burn):
                            errors.append("14-unit-economics.json: net burn does not reconcile")
                        expected_runway = float(cash["cash_balance"]) / burn if burn else None
                        reported_runway = cash.get("runway_periods")
                        if expected_runway is None and reported_runway is not None:
                            errors.append("14-unit-economics.json: runway must be null when net burn is zero")
                        elif expected_runway is not None and not close_enough(float(reported_runway), expected_runway):
                            errors.append("14-unit-economics.json: runway does not reconcile")
                    except (KeyError, TypeError, ValueError, ZeroDivisionError):
                        errors.append("14-unit-economics.json: cash values cannot be reconciled")
                valid_refs = sources | assumption_ids | metric_ids | claims
                for ref in economics.get("source_or_assumption_ids", []):
                    if ref not in valid_refs:
                        errors.append(f"14-unit-economics.json: unresolved evidence reference {ref}")
                for result in economics.get("decision_threshold_results", []):
                    try:
                        actual = float(result["actual"]) if result.get("actual") is not None else None
                        threshold = float(result["threshold"])
                        operator = result["operator"]
                        expected_pass = actual is not None and ((operator == ">=" and actual >= threshold) or (operator == "<=" and actual <= threshold))
                        if operator not in {">=", "<="} or result.get("pass") is not expected_pass:
                            errors.append(f"14-unit-economics.json: threshold result does not reconcile for {result.get('metric', 'unknown')}")
                    except (KeyError, TypeError, ValueError):
                        errors.append(f"14-unit-economics.json: invalid threshold result for {result.get('metric', 'unknown')}")
                    if result.get("pass") is False:
                        warnings.append(f"14-unit-economics.json: failed decision threshold {result.get('metric', 'unknown')}")
        except (json.JSONDecodeError, AttributeError) as exc:
            errors.append(f"14-unit-economics.json: invalid JSON structure: {exc}")

    cfo_plan_path = official / "15-cfo-operating-plan.json"
    if cfo_plan_path.exists():
        try:
            cfo_plan = json.loads(cfo_plan_path.read_text(encoding="utf-8"))
            required_sections = {"starting_cash", "collection_lag_periods", "periods", "summary", "source_or_assumption_ids"}
            missing_sections = required_sections - set(cfo_plan)
            if missing_sections:
                errors.append(f"15-cfo-operating-plan.json: missing sections {', '.join(sorted(missing_sections))}")
            else:
                plan_rows = cfo_plan["periods"]
                if not isinstance(plan_rows, list) or not plan_rows:
                    errors.append("15-cfo-operating-plan.json: periods must be a non-empty list")
                else:
                    prior_cash = float(cfo_plan["starting_cash"])
                    cumulative_revenue = cumulative_collections = 0.0
                    for index, row in enumerate(plan_rows, 1):
                        try:
                            if int(row["period"]) != index:
                                errors.append("15-cfo-operating-plan.json: periods must be sequential from 1")
                            revenue = float(row["recognized_revenue"])
                            collections = float(row["cash_collections"])
                            variable_cost = float(row["variable_cost"])
                            fixed_cost = float(row["fixed_cost"])
                            acquisition = float(row["acquisition_spend"])
                            one_time = float(row["one_time_cost"])
                            expected_operating = revenue - variable_cost - fixed_cost - acquisition - one_time
                            expected_cash_flow = collections - variable_cost - fixed_cost - acquisition - one_time
                            if not close_enough(float(row["operating_result"]), expected_operating):
                                errors.append(f"15-cfo-operating-plan.json: period {index} operating result does not reconcile")
                            if not close_enough(float(row["net_cash_flow"]), expected_cash_flow):
                                errors.append(f"15-cfo-operating-plan.json: period {index} net cash flow does not reconcile")
                            expected_ending_cash = prior_cash + expected_cash_flow
                            if not close_enough(float(row["ending_cash"]), expected_ending_cash):
                                errors.append(f"15-cfo-operating-plan.json: period {index} ending cash does not reconcile")
                            cumulative_revenue += revenue
                            cumulative_collections += collections
                            if not close_enough(float(row["accounts_receivable"]), cumulative_revenue - cumulative_collections):
                                errors.append(f"15-cfo-operating-plan.json: period {index} accounts receivable does not reconcile")
                            prior_cash = float(row["ending_cash"])
                        except (KeyError, TypeError, ValueError):
                            errors.append(f"15-cfo-operating-plan.json: period {index} has invalid numeric fields")
                    try:
                        summary = cfo_plan["summary"]
                        if not close_enough(float(summary["recognized_revenue"]), cumulative_revenue):
                            errors.append("15-cfo-operating-plan.json: summary recognized revenue does not reconcile")
                        if not close_enough(float(summary["cash_collections"]), cumulative_collections):
                            errors.append("15-cfo-operating-plan.json: summary cash collections does not reconcile")
                        if not close_enough(float(summary["ending_cash"]), prior_cash):
                            errors.append("15-cfo-operating-plan.json: summary ending cash does not reconcile")
                        expected_trough = min(float(row["ending_cash"]) for row in plan_rows)
                        if not close_enough(float(summary["cash_trough"]), expected_trough):
                            errors.append("15-cfo-operating-plan.json: cash trough does not reconcile")
                    except (KeyError, TypeError, ValueError):
                        errors.append("15-cfo-operating-plan.json: summary values cannot be reconciled")
                valid_refs = sources | assumption_ids | metric_ids | claims
                for ref in cfo_plan.get("source_or_assumption_ids", []):
                    if ref not in valid_refs:
                        errors.append(f"15-cfo-operating-plan.json: unresolved evidence reference {ref}")
                for result in cfo_plan.get("decision_threshold_results", []):
                    try:
                        actual = float(result["actual"]) if result.get("actual") is not None else None
                        threshold = float(result["threshold"])
                        expected_pass = actual is not None and result["operator"] == ">=" and actual >= threshold
                        if result.get("pass") is not expected_pass:
                            errors.append(f"15-cfo-operating-plan.json: threshold result does not reconcile for {result.get('metric', 'unknown')}")
                    except (KeyError, TypeError, ValueError):
                        errors.append(f"15-cfo-operating-plan.json: invalid threshold result for {result.get('metric', 'unknown')}")
                    if result.get("pass") is False:
                        warnings.append(f"15-cfo-operating-plan.json: failed decision threshold {result.get('metric', 'unknown')}")
        except (json.JSONDecodeError, AttributeError) as exc:
            errors.append(f"15-cfo-operating-plan.json: invalid JSON structure: {exc}")

    counts = {name: len(rows) for name, rows in tables.items()}
    counts.update({"claims": len(claims), "sources": len(sources)})
    if option_path.exists():
        counts["options"] = option_count
    if integration_path.exists():
        counts["integrations"] = integration_count
    if idea_path.exists():
        counts["ideas"] = idea_count
    if engineering_level:
        counts["engineering_level"] = engineering_level
    if economics_path.exists():
        counts["unit_economics"] = 1
    if cfo_plan_path.exists():
        counts["cfo_operating_plan"] = 1
    return errors, warnings, counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failure")
    args = parser.parse_args()
    errors, warnings, counts = audit(args.project.expanduser().resolve())
    result = {"errors": errors, "warnings": warnings, "counts": counts, "ready": not errors and (not args.strict or not warnings)}
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for item in warnings:
            print(f"WARNING: {item}")
        for item in errors:
            print(f"ERROR: {item}")
        print(f"Audit complete: {len(errors)} error(s), {len(warnings)} warning(s), counts={counts}")
    raise SystemExit(0 if result["ready"] else 1)


if __name__ == "__main__":
    main()
