#!/usr/bin/env python3
"""Inspect Excel/CSV data, discover Named Ranges, execute CFO sanity checks, and sync values into CaseKit's metric tree."""

import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def number(value, context):
    if isinstance(value, bool) or value is None:
        raise ValueError(f"{context}: expected numeric value, got {value!r}")
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).replace(",", "").replace("$", "").replace("%", "").strip())
    except ValueError as exc:
        raise ValueError(f"{context}: expected numeric value, got {value!r}") from exc


def format_number(value):
    if value.is_integer():
        return str(int(value))
    return f"{value:.12f}".rstrip("0").rstrip(".")


def clean_coord(coord):
    """Normalize Excel coordinates like '$C$10' or '$C$10:$C$15' to 'C10'."""
    if ":" in coord:
        coord = coord.split(":")[0]
    return coord.replace("$", "").strip()


def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.reader(handle, delimiter="\t" if path.suffix.lower() == ".tsv" else ","))
    return {"CSV": rows}


def read_xlsx(path, values_only=False):
    try:
        from openpyxl import load_workbook
    except ImportError as exc:
        raise SystemExit("openpyxl is required for .xlsx. Run: python -m pip install -r requirements.txt") from exc
    book = load_workbook(path, data_only=values_only, read_only=True)
    result = {}
    for sheet in book.worksheets:
        result[sheet.title] = [[cell.value for cell in row] for row in sheet.iter_rows()]
    return result


def workbook(path, values_only=False):
    suffix = path.suffix.lower()
    if suffix in {".csv", ".tsv"}:
        return read_csv(path)
    if suffix == ".xlsx":
        return read_xlsx(path, values_only)
    raise ValueError("Supported spreadsheet formats: .xlsx, .csv, .tsv")


def get_named_ranges(path):
    """Discover all defined Named Ranges in an Excel workbook with cached values and formulas."""
    if path.suffix.lower() != ".xlsx":
        return {}
    try:
        from openpyxl import load_workbook
    except ImportError as exc:
        raise SystemExit("openpyxl is required for .xlsx. Run: python -m pip install -r requirements.txt") from exc
    formula_book = load_workbook(path, data_only=False)
    value_book = load_workbook(path, data_only=True)
    named_map = {}
    for name, defn in formula_book.defined_names.items():
        for sheet_name, coord in defn.destinations:
            coord_fixed = clean_coord(coord)
            if sheet_name not in formula_book.sheetnames:
                continue
            formula = formula_book[sheet_name][coord_fixed].value
            value = value_book[sheet_name][coord_fixed].value
            if isinstance(formula, str) and formula.startswith("=") and value is None:
                raise ValueError(
                    f"Named range '{name}' ({sheet_name}!{coord_fixed}) has a formula without a cached result. "
                    f"Recalculate and save the workbook in Excel first."
                )
            named_map[name] = {
                "name": name,
                "sheet": sheet_name,
                "cell": coord_fixed,
                "value": value,
                "formula": formula if isinstance(formula, str) and formula.startswith("=") else None,
            }
    return named_map


def named_range_value(path, name):
    ranges = get_named_ranges(path)
    if name not in ranges:
        available = ", ".join(sorted(ranges.keys())) if ranges else "none"
        raise ValueError(f"Named range '{name}' not found in workbook {path}. Available named ranges: {available}")
    item = ranges[name]
    return item["value"], item["formula"], item["sheet"], item["cell"]


def cell_value(path, sheet_name, cell):
    if path.suffix.lower() != ".xlsx":
        raise ValueError("Cell mappings require .xlsx inputs; import CSV values into the metric tree directly.")
    try:
        from openpyxl import load_workbook
    except ImportError as exc:
        raise SystemExit("openpyxl is required for .xlsx. Run: python -m pip install -r requirements.txt") from exc
    formula_book = load_workbook(path, data_only=False, read_only=True)
    value_book = load_workbook(path, data_only=True, read_only=True)
    if sheet_name not in formula_book.sheetnames:
        raise ValueError(f"Sheet not found: {sheet_name}")
    coord_clean = clean_coord(cell)
    formula = formula_book[sheet_name][coord_clean].value
    value = value_book[sheet_name][coord_clean].value
    if isinstance(formula, str) and formula.startswith("=") and value is None:
        raise ValueError(f"{sheet_name}!{coord_clean} has a formula without a cached result. Recalculate and save the workbook in Excel first.")
    return value, formula


def run_cfo_sanity_checks(metrics_dict):
    """Run algorithmic venture CFO sanity checks on discovered financial metrics."""
    checks = []
    
    # 1. Gross Margin Check
    margin_keys = ["Gross_Margin_Base", "Gross_Margin_Pct", "Gross_Margin", "Hardware_Gross_Margin_Base"]
    for k in margin_keys:
        if k in metrics_dict and isinstance(metrics_dict[k], (int, float)):
            val = float(metrics_dict[k])
            if val < 0.0:
                checks.append({
                    "gate": "Gross Margin Floor",
                    "status": "FAIL",
                    "metric": k,
                    "value": val,
                    "message": f"Critical: Negative gross margin ({val:.1%}). The business loses money on direct delivery.",
                })
            elif val < 0.40 and "Hardware" not in k and "Retail" not in k:
                checks.append({
                    "gate": "Gross Margin Floor",
                    "status": "WARN",
                    "metric": k,
                    "value": val,
                    "message": f"Gross margin ({val:.1%}) is below 40.0% venture benchmark for software/platform models.",
                })
            elif val < 0.15:
                checks.append({
                    "gate": "Gross Margin Floor",
                    "status": "WARN",
                    "metric": k,
                    "value": val,
                    "message": f"Gross margin ({val:.1%}) is below 15.0% threshold for retail/hardware operations.",
                })
            else:
                checks.append({
                    "gate": "Gross Margin Floor",
                    "status": "PASS",
                    "metric": k,
                    "value": val,
                    "message": f"Gross margin is healthy at {val:.1%}.",
                })
            break

    # 2. Cash Runway & Insolvency Check
    runway_keys = ["Cash_Runway_Months_Base", "Cash_Runway_Months", "Runway_Months"]
    for k in runway_keys:
        if k in metrics_dict and isinstance(metrics_dict[k], (int, float)):
            val = float(metrics_dict[k])
            if val < 6.0:
                checks.append({
                    "gate": "Cash Runway Horizon",
                    "status": "WARN",
                    "metric": k,
                    "value": val,
                    "message": f"Critical cash runway alert: {val:.1f} months remaining (< 6.0m minimum venture safety hurdle).",
                })
            else:
                checks.append({
                    "gate": "Cash Runway Horizon",
                    "status": "PASS",
                    "metric": k,
                    "value": val,
                    "message": f"Cash runway is adequate at {val:.1f} months.",
                })
            break

    cash_keys = ["Ending_Cash_Base", "Cash_Trough_Base", "Ending_Cash"]
    for k in cash_keys:
        if k in metrics_dict and isinstance(metrics_dict[k], (int, float)):
            val = float(metrics_dict[k])
            if val < 0.0:
                checks.append({
                    "gate": "Cash Solvency",
                    "status": "FAIL",
                    "metric": k,
                    "value": val,
                    "message": f"Projected cash insolvency: Ending cash balance drops to ${val:,.0f}.",
                })
            else:
                checks.append({
                    "gate": "Cash Solvency",
                    "status": "PASS",
                    "metric": k,
                    "value": val,
                    "message": f"Positive cash position maintained (${val:,.0f}).",
                })
            break

    # 3. Payback Period Check
    payback_keys = ["CAC_Payback_Months_Base", "CAC_Payback_Months", "Payback_Months_Base", "Payback_Months"]
    for k in payback_keys:
        if k in metrics_dict and isinstance(metrics_dict[k], (int, float)):
            val = float(metrics_dict[k])
            if val > 18.0:
                checks.append({
                    "gate": "CAC Payback Horizon",
                    "status": "WARN",
                    "metric": k,
                    "value": val,
                    "message": f"CAC payback period ({val:.1f} months) exceeds the 18-month venture capital hurdle.",
                })
            elif val <= 0.0:
                checks.append({
                    "gate": "CAC Payback Horizon",
                    "status": "WARN",
                    "metric": k,
                    "value": val,
                    "message": f"CAC payback is undefined or not achieved within modeled periods.",
                })
            else:
                checks.append({
                    "gate": "CAC Payback Horizon",
                    "status": "PASS",
                    "metric": k,
                    "value": val,
                    "message": f"CAC payback period is rapid at {val:.1f} months.",
                })
            break

    # 4. LTV:CAC Ratio Check
    ltv_keys = ["LTV_to_CAC_Base", "LTV_to_CAC", "LTV_CAC_Ratio"]
    for k in ltv_keys:
        if k in metrics_dict and isinstance(metrics_dict[k], (int, float)):
            val = float(metrics_dict[k])
            if val < 1.0:
                checks.append({
                    "gate": "Unit Value Creation (LTV:CAC)",
                    "status": "FAIL",
                    "metric": k,
                    "value": val,
                    "message": f"Value destruction: LTV:CAC ratio ({val:.2f}x) is below 1.0x (CAC exceeds lifetime customer value).",
                })
            elif val < 3.0:
                checks.append({
                    "gate": "Unit Value Creation (LTV:CAC)",
                    "status": "WARN",
                    "metric": k,
                    "value": val,
                    "message": f"LTV:CAC ratio ({val:.2f}x) is below the 3.0x venture target benchmark.",
                })
            else:
                checks.append({
                    "gate": "Unit Value Creation (LTV:CAC)",
                    "status": "PASS",
                    "metric": k,
                    "value": val,
                    "message": f"LTV:CAC ratio is strong at {val:.2f}x.",
                })
            break

    return checks


def markdown_report(path):
    raw = workbook(path, values_only=False)
    values = workbook(path, values_only=True) if path.suffix.lower() == ".xlsx" else raw
    lines = [f"# Spreadsheet inspection: {path.name}", "", f"- Path: `{path}`", "- Values from formulas use Excel's last saved calculation cache.", ""]
    
    # Named Ranges Discovery Section
    if path.suffix.lower() == ".xlsx":
        named_map = get_named_ranges(path)
        lines.extend([
            "## Defined Named Ranges",
            "",
            f"Discovered **{len(named_map)}** defined name(s) in workbook:",
            "",
            "| Named Range | Location | Cached Value | Formula |",
            "|---|---|---|---|",
        ])
        metrics_for_checks = {}
        for name in sorted(named_map.keys()):
            item = named_map[name]
            val_display = str(item["value"]) if item["value"] is not None else "*empty*"
            formula_display = f"`{item['formula']}`" if item["formula"] else "*(constant)*"
            lines.append(f"| `{name}` | `{item['sheet']}!{item['cell']}` | **{val_display}** | {formula_display} |")
            if item["value"] is not None and isinstance(item["value"], (int, float)):
                metrics_for_checks[name] = float(item["value"])
        lines.append("")
        
        # CFO Sanity Checks Section
        cfo_results = run_cfo_sanity_checks(metrics_for_checks)
        if cfo_results:
            lines.extend([
                "## CFO Sanity Checks & Financial Health Gates",
                "",
                "| Gate | Status | Metric | Value | Verdict |",
                "|---|---|---|---|---|",
            ])
            for chk in cfo_results:
                badge = "✅ PASS" if chk["status"] == "PASS" else ("⚠️ WARN" if chk["status"] == "WARN" else "❌ FAIL")
                val_fmt = f"{chk['value']:,.2f}" if isinstance(chk['value'], float) else str(chk['value'])
                lines.append(f"| {chk['gate']} | {badge} | `{chk['metric']}` | {val_fmt} | {chk['message']} |")
            lines.append("")

    for name, rows in raw.items():
        nonempty = [row for row in rows if any(value not in (None, "") for value in row)]
        formulas = sum(1 for row in rows for value in row if isinstance(value, str) and value.startswith("="))
        lines.extend([f"## Sheet: {name}", "", f"- Non-empty rows: {len(nonempty)}", f"- Formula cells: {formulas}", "", "### Preview", ""])
        preview = values[name][: min(12, len(values[name]))]
        for row in preview:
            lines.append(" | ".join("" if value is None else str(value) for value in row[:12]))
        lines.append("")
    return "\n".join(lines)


def read_metric_tree(path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader)


def write_metric_tree(path, fields, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def official_dir(project):
    clean = project / "03-OFFICIAL"
    return clean if clean.is_dir() else project


def sync(project, mapping_path, apply):
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    mappings = mapping.get("mappings")
    if not isinstance(mappings, list) or not mappings:
        raise ValueError("Mapping must contain a non-empty 'mappings' list")
    metric_path = official_dir(project) / "03-metric-tree.csv"
    fields, rows = read_metric_tree(metric_path)
    required = {"metric_id", "low", "base", "high"}
    if not required <= set(fields):
        raise ValueError("03-metric-tree.csv is missing required scenario columns")
    by_id = {row.get("metric_id"): row for row in rows}
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mapping": str(mapping_path),
        "updates": [],
        "warnings": [],
        "cfo_sanity_checks": [],
    }
    synced_metrics = {}
    for item in mappings:
        for key in ("metric_id", "scenario", "file"):
            if key not in item:
                raise ValueError(f"Mapping item missing '{key}'")
        scenario = item["scenario"]
        if scenario not in {"low", "base", "high"}:
            raise ValueError(f"Unsupported scenario '{scenario}'")
        metric_id = item["metric_id"]
        if metric_id not in by_id:
            raise ValueError(f"Mapping references unknown metric {metric_id}")
        source = (project / item["file"]).resolve()
        if not source.is_file():
            raise ValueError(f"Mapped spreadsheet does not exist: {source}")
            
        if "named_range" in item:
            named_range_name = item["named_range"]
            value, formula, sheet_name, cell_coord = named_range_value(source, named_range_name)
            cell_ref = f"{sheet_name}!{cell_coord}"
            target_metric_label = named_range_name
        elif "sheet" in item and "cell" in item:
            sheet_name = item["sheet"]
            cell_coord = item["cell"]
            value, formula = cell_value(source, sheet_name, cell_coord)
            cell_ref = f"{sheet_name}!{cell_coord}"
            target_metric_label = metric_id
        else:
            raise ValueError(f"Mapping item must contain 'named_range' or 'sheet' and 'cell': {item}")
            
        parsed = number(value, f"{source.name}:{cell_ref}")
        old = by_id[metric_id].get(scenario, "")
        report["updates"].append({
            "metric_id": metric_id,
            "scenario": scenario,
            "old": old,
            "new": parsed,
            "file": item["file"],
            "cell": cell_ref,
            "named_range": item.get("named_range"),
            "formula": formula if isinstance(formula, str) and formula.startswith("=") else None
        })
        by_id[metric_id][scenario] = format_number(parsed)
        if scenario == "base":
            synced_metrics[target_metric_label] = parsed

    # Run CFO sanity checks on synced metrics
    cfo_checks = run_cfo_sanity_checks(synced_metrics)
    report["cfo_sanity_checks"] = cfo_checks
    for chk in cfo_checks:
        if chk["status"] in ("WARN", "FAIL"):
            report["warnings"].append(f"[{chk['status']}] {chk['gate']}: {chk['message']}")

    if apply:
        write_metric_tree(metric_path, fields, rows)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    inspect = sub.add_parser("inspect", help="Inspect spreadsheet sheets, named ranges, and run CFO sanity checks")
    inspect.add_argument("file", type=Path)
    inspect.add_argument("--output", type=Path)
    sync_parser = sub.add_parser("sync", help="Synchronize mapped values into metric tree")
    sync_parser.add_argument("project", type=Path)
    sync_parser.add_argument("mapping", type=Path)
    sync_parser.add_argument("--apply", action="store_true")
    sync_parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if args.command == "inspect":
        report = markdown_report(args.file.expanduser().resolve())
        if args.output:
            output = args.output.expanduser().resolve()
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(report, encoding="utf-8")
            print(f"Wrote workbook inspection -> {output}")
        else:
            print(report)
        return
    report = sync(args.project.expanduser().resolve(), args.mapping.expanduser().resolve(), args.apply)
    if args.report:
        args.report.expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
        args.report.expanduser().resolve().write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not args.apply:
        print("Preview only. Run again with --apply to update 03-metric-tree.csv.")


if __name__ == "__main__":
    main()
