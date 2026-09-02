#!/usr/bin/env python3
"""CaseKit command line: create, inspect, sync, validate, and render a case workspace."""

import argparse
import csv
import hashlib
import importlib.util
import json
import platform
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ORCHESTRATOR = ROOT / "skills" / "casekit-orchestrator" / "scripts"
VALIDATOR = ROOT / "skills" / "casekit-validator" / "scripts"
RESEARCH = ROOT / "skills" / "casekit-research" / "scripts"
DECK = ROOT / "skills" / "casekit-deck" / "scripts"
SPREADSHEET = ROOT / "skills" / "casekit-finance" / "scripts" / "spreadsheet_sync.py"

OFFICIAL_FILES = (
    "00-DASHBOARD.md", "00-brief.md", "00-case-profile.md", "01-evidence-ledger.csv", "02-assumptions.csv",
    "03-metric-tree.csv", "04-decision-log.csv", "05-risk-register.csv", "06-workstream-status.md",
    "07-final-integrated-case.md", "08-premises.csv", "09-experiments.csv", "10-team-charter.md",
    "11-rubric-scorecard.csv", "12-deck-spec.json", "13-submission-checklist.md", "16-vision-growth-plan.md",
    "data-import-map.json", "engineering-delivery-plan.md", "idea-backlog.csv", "integration-contract.csv",
    "option-portfolio.csv", "qna-bank.csv", "research-backlog.csv", "engineering",
)


def workspace_dir(project, clean_name, legacy_name):
    """Use the clean team layout when present, otherwise retain legacy workspaces."""
    clean = project / clean_name
    return clean if clean.is_dir() else project / legacy_name


def official_dir(project):
    clean = project / "03-OFFICIAL"
    return clean if clean.is_dir() else project


def run(command):
    result = subprocess.run(command, check=False)
    if result.returncode:
        raise SystemExit(result.returncode)


def copy_input(source, destination, label):
    if not source:
        return None
    source = Path(source).expanduser().resolve()
    if not source.is_file():
        raise SystemExit(f"{label} does not exist or is not a file: {source}")
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / source.name
    if target.exists():
        raise SystemExit(f"Refusing to overwrite imported input: {target}")
    shutil.copy2(source, target)
    return target


def extract_pdf(target, inputs):
    if importlib.util.find_spec("pypdf") is None:
        print("PDF copied. Install pypdf then rerun an AI intake to extract native PDF text.")
        return
    from pypdf import PdfReader
    reader = PdfReader(str(target))
    extracted = "\n\n".join(page.extract_text() or "" for page in reader.pages)
    text_path = inputs / "extracted" / f"{target.stem}.md"
    text_path.parent.mkdir(parents=True, exist_ok=True)
    text_path.write_text(f"# Extracted: {target.name}\n\n{extracted}\n", encoding="utf-8")
    print(f"Extracted {len(reader.pages)} PDF page(s) -> {text_path}")


def write_clean_layout_docs(destination, team):
    (destination / "README.md").write_text(
        "# Case workspace\n\n"
        "This workspace uses the clean team layout.\n\n"
        "| Folder | Purpose |\n|---|---|\n"
        "| `01-INPUTS/` | Original brief, rubric, deck, Excel, and raw data |\n"
        "| `02-TEAM/` | Personal draft folders; create one folder per teammate |\n"
        "| `03-OFFICIAL/` | Approved evidence, numbers, decisions, and deck only |\n\n"
        "Start with `00-START-HERE.md`.\n",
        encoding="utf-8",
    )
    (destination / "00-START-HERE.md").write_text(
        "# Start here\n\n"
        "1. Put official files in `01-INPUTS/`.\n"
        "2. Each teammate works only in `02-TEAM/<name>/`.\n"
        "3. Promote team-approved work into `03-OFFICIAL/`.\n"
        "4. Before deck freeze run `python3 /path/to/casekit/casekit.py validate . --strict`.\n\n"
        "A draft is not official merely because an AI wrote it.\n",
        encoding="utf-8",
    )
    (destination / "AGENTS.md").write_text(
        "# AI working rules\n\n"
        "- Read `README.md` and `00-START-HERE.md` first.\n"
        "- Do not overwrite `01-INPUTS/`.\n"
        "- Work in the requested `02-TEAM/<name>/` folder by default.\n"
        "- Do not edit `03-OFFICIAL/` unless the user explicitly approves a promotion.\n"
        "- Label unknown numbers as assumptions; do not present a draft as a fact.\n",
        encoding="utf-8",
    )
    team_root = destination / "02-TEAM"
    team_root.mkdir(exist_ok=True)
    (team_root / "README.md").write_text(
        "# Team drafts\n\nEach person works only in their own folder.\n\n"
        "- `01-RESEARCH/`: sources and notes\n- `02-DRAFTS/`: work in progress\n- `03-READY/`: recommendation ready for review\n",
        encoding="utf-8",
    )
    for name in team:
        member = team_root / name
        for folder in ("01-RESEARCH", "02-DRAFTS", "03-READY"):
            path = member / folder
            path.mkdir(parents=True, exist_ok=True)
            (path / ".gitkeep").write_text("\n", encoding="utf-8")
        (member / "README.md").write_text(
            f"# {name} workspace\n\nNo role is assigned by this template. Keep personal work in this folder.\n",
            encoding="utf-8",
        )


def apply_clean_layout(destination, team):
    inputs = destination / "inputs"
    if inputs.exists():
        inputs.rename(destination / "01-INPUTS")
    inbox = destination / "00-INBOX"
    if inbox.exists():
        inbox.rename(destination / "02-TEAM")
    official = destination / "03-OFFICIAL"
    official.mkdir(exist_ok=True)
    for name in OFFICIAL_FILES:
        source = destination / name
        if source.exists():
            source.rename(official / name)
    for name in ("README-START-HERE.md", "TEAM-WORKFLOW.md"):
        source = destination / name
        if source.exists():
            source.unlink()
    write_clean_layout_docs(destination, team)


def parse_team(value):
    if not value:
        return []
    names = [name.strip() for name in value.split(",") if name.strip()]
    if len(names) != len(set(names)):
        raise SystemExit("--team contains duplicate names")
    if any("/" in name or "\\" in name or name in {".", ".."} for name in names):
        raise SystemExit("--team names cannot contain path separators")
    return names


def cmd_doctor(args):
    required = {"pptx": "python-pptx", "openpyxl": "openpyxl", "pypdf": "pypdf"}
    missing = [package for module, package in required.items() if importlib.util.find_spec(module) is None]
    print(f"Python: {sys.version.split()[0]} ({sys.executable})")
    print(f"Platform: {platform.system()} {platform.release()}")
    if sys.version_info < (3, 10):
        print("ERROR: Python 3.10 or later is required.")
        raise SystemExit(1)
    if missing:
        print("Missing optional runtime packages: " + ", ".join(missing))
        print(f"Install them with: {sys.executable} -m pip install -r {ROOT / 'requirements.txt'}")
        if args.strict:
            raise SystemExit(1)
    else:
        print("Runtime ready: deck rendering, PDF ingestion, and Excel/CSV sync are available.")


def cmd_init(args):
    destination = Path(args.destination).expanduser().resolve()
    if destination.exists():
        raise SystemExit(f"Refusing to overwrite existing path: {destination}")
    team = parse_team(args.team)
    if team and args.layout != "clean" and args.preset != "full-deep-drill":
        raise SystemExit("--team requires --layout clean or --preset full-deep-drill")

    cmd = [sys.executable, str(ORCHESTRATOR / "new_case.py"), str(destination)]
    if args.preset:
        cmd.extend(["--preset", args.preset])
    run(cmd)

    obsidian_template = ROOT / "templates" / "obsidian-config" / ".obsidian"
    if obsidian_template.exists() and not (destination / ".obsidian").exists():
        shutil.copytree(obsidian_template, destination / ".obsidian")

    if args.preset == "full-deep-drill" and team:
        write_clean_layout_docs(destination, team)
    elif not args.preset and args.layout == "clean":
        apply_clean_layout(destination, team)

    run([sys.executable, str(ROOT / "install.py"), "--scope", "project", "--project-root", str(destination)])
    inputs = workspace_dir(destination, "01-INPUTS", "inputs")
    inputs.mkdir(parents=True, exist_ok=True)
    (inputs / "archive").mkdir(exist_ok=True)

    imported = {}
    for label, source in (("brief", args.brief), ("rubric", args.rubric), ("deck", args.deck), ("data", args.data)):
        target = copy_input(source, inputs, label)
        if target:
            imported[label] = str(target.relative_to(destination))
            if target.suffix.lower() == ".pdf":
                extract_pdf(target, inputs)

    profile = official_dir(destination) / "00-case-profile.md"
    if profile.exists():
        text = profile.read_text(encoding="utf-8")
        text = text.replace("- Case type: auto", f"- Case type: {args.case_type}")
        text = text.replace("- Working language: Thai", f"- Working language: {args.language}")
        text = text.replace("- Input manifest: []", "- Input manifest: " + json.dumps(imported, ensure_ascii=False))
        profile.write_text(text, encoding="utf-8")

    print(f"CaseKit workspace ready: {destination}" + (f" (preset: {args.preset})" if args.preset else ""))
    print("Open this folder as an Obsidian vault, then start with " + ("00-START-HERE.md." if (args.layout == "clean" or args.preset == "full-deep-drill") else "README-START-HERE.md."))


def cmd_ingest(args):
    project = Path(args.project).expanduser().resolve()
    if not project.is_dir():
        raise SystemExit(f"Project directory does not exist: {project}")
    target = copy_input(args.file, workspace_dir(project, "01-INPUTS", "inputs"), args.kind)
    print(f"Imported {args.kind}: {target}")
    if target.suffix.lower() == ".pdf":
        extract_pdf(target, workspace_dir(project, "01-INPUTS", "inputs"))


def nonblank_rows(path):
    if not path.exists():
        return 0
    if path.suffix.lower() != ".csv":
        return int(path.stat().st_size > 0)
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return sum(1 for row in csv.DictReader(handle) if any((value or "").strip() for value in row.values()))


def cmd_status(args):
    project = Path(args.project).expanduser().resolve()
    if not project.is_dir():
        raise SystemExit(f"Project directory does not exist: {project}")
    inputs = workspace_dir(project, "01-INPUTS", "inputs")
    official = official_dir(project)
    input_files = [path for path in inputs.rglob("*") if path.is_file() and path.name != "README.md"] if inputs.exists() else []
    def find_file(name):
        direct = official / name
        if direct.exists():
            return direct
        matches = [p for p in official.rglob(name) if p.is_file()]
        return matches[0] if matches else direct

    evidence = nonblank_rows(find_file("01-evidence-ledger.csv"))
    assumptions = nonblank_rows(find_file("02-assumptions.csv"))
    metrics = nonblank_rows(find_file("03-metric-tree.csv"))
    deck_path = find_file("12-deck-spec.json")
    slides = 0
    if deck_path.exists():
        try:
            slides = len(json.loads(deck_path.read_text(encoding="utf-8")).get("slides", []))
        except (json.JSONDecodeError, AttributeError):
            pass
    print(f"Workspace: {project}")
    print(f"Layout: {'clean team' if official != project else 'legacy'}")
    print(f"Inputs: {len(input_files)} | Evidence: {evidence} | Assumptions: {assumptions} | Metrics: {metrics} | Deck slides: {slides}")
    if not input_files:
        print("Next: add the official brief/rubric/deck/data to the inputs folder.")
    elif evidence == 0:
        print("Next: use casekit-orchestrator and casekit-research to frame the case and capture evidence.")
    elif metrics == 0:
        print("Next: define the outcome metric and driver tree before making a deck.")
    elif slides == 0:
        print("Next: create the deck only after the strategy and model are ready.")
    else:
        print("Next: run validate --strict before deck freeze, then render.")


def next_id_for(prefix, existing_list):
    nums = [int(m.group(1)) for x in existing_list if (m := re.search(rf"{prefix}-(\d+)", x))]
    max_num = max(nums, default=0)
    return f"{prefix}-{max_num + 1:03d}"


def cmd_add_claim(args):
    project = Path(args.project).expanduser().resolve()
    if not project.is_dir():
        raise SystemExit(f"Project directory does not exist: {project}")
    official = official_dir(project)
    path = official / "01-evidence-ledger.csv"
    if not path.exists():
        path = project / "01-evidence-ledger.csv"
    if not path.exists():
        raise SystemExit(f"Evidence ledger not found: {path}")

    existing_claims = []
    existing_sources = []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or [
            "claim_id", "claim", "source_id", "source_type", "publisher", "title",
            "url", "published_date", "accessed_date", "page_or_section",
            "verbatim_support", "interpretation", "quality", "recency",
            "relevance", "status", "owner",
        ]
        for row in reader:
            if row.get("claim_id"):
                existing_claims.append(row["claim_id"].strip())
            if row.get("source_id"):
                existing_sources.append(row["source_id"].strip())

    claim_id = next_id_for("CLM", existing_claims)
    source_id = next_id_for("SRC", existing_sources)
    accessed = getattr(args, "accessed_date", None) or date.today().isoformat()
    published = getattr(args, "published_date", None) or accessed

    new_row = {
        "claim_id": claim_id,
        "claim": args.claim,
        "source_id": source_id,
        "source_type": getattr(args, "source_type", "primary") or "primary",
        "publisher": args.publisher,
        "title": args.title,
        "url": args.url,
        "published_date": published,
        "accessed_date": accessed,
        "page_or_section": getattr(args, "page", None) or getattr(args, "page_or_section", None) or "N/A",
        "verbatim_support": getattr(args, "verbatim_support", "") or args.claim,
        "interpretation": getattr(args, "interpretation", "") or "Direct empirical evidence",
        "quality": args.quality,
        "recency": args.recency,
        "relevance": args.relevance,
        "status": args.status,
        "owner": getattr(args, "owner", "Research") or "Research",
    }

    for k in new_row:
        if k not in fields:
            fields.append(k)

    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writerow(new_row)

    archive_res = None
    if getattr(args, "archive", True) and args.url:
        try:
            sys.path.insert(0, str(RESEARCH))
            from archive_source import archive_source
            archive_res = archive_source(
                project=project,
                source_id=source_id,
                url=args.url,
                title=args.title,
                publisher=args.publisher,
                accessed_date=accessed,
            )
        except Exception:
            pass

    print(f"Added claim {claim_id} ({source_id}) to {path.name}")
    if archive_res and archive_res.get("snapshot_path"):
        print(f"Archived snapshot -> {archive_res['snapshot_path']}")
    return {"claim_id": claim_id, "source_id": source_id, "status": "added"}


def cmd_add_assumption(args):
    project = Path(args.project).expanduser().resolve()
    if not project.is_dir():
        raise SystemExit(f"Project directory does not exist: {project}")
    official = official_dir(project)
    path = official / "02-assumptions.csv"
    if not path.exists():
        path = project / "02-assumptions.csv"
    if not path.exists():
        raise SystemExit(f"Assumptions ledger not found: {path}")

    try:
        low = float(args.low)
        base = float(args.base)
        high = float(args.high)
    except (ValueError, TypeError):
        raise SystemExit("Error: low, base, and high must be valid numbers")

    if not (low <= base <= high):
        raise SystemExit(f"Error: expected low <= base <= high (got low={low}, base={base}, high={high})")

    existing_asms = []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or [
            "assumption_id", "variable", "definition", "unit", "low", "base", "high",
            "basis", "source_ids", "confidence", "sensitivity", "validation_method",
            "owner", "status",
        ]
        for row in reader:
            if row.get("assumption_id"):
                existing_asms.append(row["assumption_id"].strip())

    asm_id = next_id_for("ASM", existing_asms)
    new_row = {
        "assumption_id": asm_id,
        "variable": args.variable,
        "definition": getattr(args, "definition", "") or args.variable,
        "unit": args.unit,
        "low": str(low),
        "base": str(base),
        "high": str(high),
        "basis": args.basis,
        "source_ids": getattr(args, "source_ids", "") or "",
        "confidence": args.confidence,
        "sensitivity": args.sensitivity,
        "validation_method": getattr(args, "validation_method", "") or "Pilot validation",
        "owner": getattr(args, "owner", "Finance") or "Finance",
        "status": getattr(args, "status", "open") or "open",
    }

    for k in new_row:
        if k not in fields:
            fields.append(k)

    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writerow(new_row)

    print(f"Added assumption {asm_id} ({args.variable}) to {path.name}")
    return {"assumption_id": asm_id, "status": "added"}


def cmd_add_decision(args):
    project = Path(args.project).expanduser().resolve()
    if not project.is_dir():
        raise SystemExit(f"Project directory does not exist: {project}")
    official = official_dir(project)
    path = official / "04-decision-log.csv"
    if not path.exists():
        path = project / "04-decision-log.csv"
    if not path.exists():
        raise SystemExit(f"Decision log not found: {path}")

    dec_date = getattr(args, "date", None) or date.today().isoformat()
    try:
        date.fromisoformat(dec_date)
    except ValueError:
        raise SystemExit(f"Error: date must be YYYY-MM-DD (got: {dec_date})")

    existing_decs = []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or [
            "decision_id", "date", "decision", "alternatives", "criteria",
            "rationale", "evidence_and_assumption_ids", "owner", "status",
        ]
        for row in reader:
            if row.get("decision_id"):
                existing_decs.append(row["decision_id"].strip())

    dec_id = next_id_for("DEC", existing_decs)
    refs = getattr(args, "refs", "") or getattr(args, "evidence_and_assumption_ids", "") or ""

    new_row = {
        "decision_id": dec_id,
        "date": dec_date,
        "decision": args.decision,
        "alternatives": getattr(args, "alternatives", "") or "Status quo workaround",
        "criteria": getattr(args, "criteria", "") or "Speed, cost, unit economics",
        "rationale": getattr(args, "rationale", "") or "Optimal risk-adjusted decision",
        "evidence_and_assumption_ids": refs,
        "owner": getattr(args, "owner", "Strategy") or "Strategy",
        "status": getattr(args, "status", "approved") or "approved",
    }

    for k in new_row:
        if k not in fields:
            fields.append(k)

    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writerow(new_row)

    print(f"Added decision {dec_id} to {path.name}")
    return {"decision_id": dec_id, "status": "added"}


def cmd_check(args):
    project = Path(args.project).expanduser().resolve()
    if not project.is_dir():
        raise SystemExit(f"Project directory does not exist: {project}")

    sys.path.insert(0, str(VALIDATOR))
    from audit_case import audit
    errors, warnings, counts = audit(project)

    official = official_dir(project)
    has_tier3 = (project / "03-OFFICIAL").is_dir()
    has_corp = (official / "04-decision-log.csv").exists()
    if has_tier3:
        preset_name = "full-deep-drill"
        layout_name = "clean team (3-tier)"
    elif has_corp:
        preset_name = "corporate-launchpad"
        layout_name = "standard corporate"
    else:
        preset_name = "hackathon-sprint"
        layout_name = "minimal sprint"

    print(f"CaseKit Diagnostic Report: {project}")
    print(f"Preset: {preset_name} | Layout: {layout_name}")
    print("-" * 65)
    print(f"Evidence Ledger:  {counts.get('claims', 0)} claims across {counts.get('sources', 0)} sources")
    print(f"Assumptions:      {counts.get('assumptions', 0)} assumptions (all low <= base <= high)")
    print(f"Metric Tree:      {counts.get('metrics', 0)} metrics tracked")
    if "options" in counts:
        print(f"Option Portfolio: {counts['options']} strategic options")
    if "integrations" in counts:
        print(f"Integrations:     {counts['integrations']} system contracts")
    if "ideas" in counts:
        print(f"Idea Backlog:     {counts['ideas']} ideas")
    print("-" * 65)

    if warnings:
        for warn in warnings:
            print(f"WARNING: {warn}")
    if errors:
        for err in errors:
            print(f"ERROR: {err}")

    ready = not errors and (not args.strict or not warnings)
    status_str = "PASSED" if ready else "FAILED"
    print(f"Audit Status:     {status_str} ({len(errors)} error(s), {len(warnings)} warning(s))")

    if ready:
        print("Next Action:      Run `python3 casekit.py render .` to export presentation deck.")
        sys.exit(0)
    else:
        print("Next Action:      Resolve errors before freezing deck.")
        sys.exit(1)


def cmd_archive(args):
    project = Path(args.project).expanduser().resolve()
    sys.path.insert(0, str(RESEARCH))
    from archive_source import archive_source, archive_all_sources, verify_archive

    if args.verify:
        errors, warnings = verify_archive(project)
        for w in warnings:
            print(f"WARNING: {w}")
        for e in errors:
            print(f"ERROR: {e}")
        print(f"Archive integrity: {len(errors)} error(s), {len(warnings)} warning(s)")
        sys.exit(1 if errors else 0)

    if args.source_id and args.url:
        res = archive_source(
            project=project,
            source_id=args.source_id,
            url=args.url,
            title=getattr(args, "title", ""),
            publisher=getattr(args, "publisher", ""),
            force=args.force,
        )
        print(f"Archived {res['source_id']} -> {res['snapshot_path']} (status: {res['status']})")
    else:
        results = archive_all_sources(project, force=args.force)
        print(f"Archived {len(results)} source(s) for {project}")


def cmd_sync_spreadsheet(args):
    project = Path(args.project).expanduser().resolve()
    command = [sys.executable, str(SPREADSHEET), "sync", str(project), str(Path(args.mapping).expanduser().resolve())]
    if args.apply:
        command.append("--apply")
    if args.report:
        command.extend(["--report", str(Path(args.report).expanduser().resolve())])
    run(command)


def cmd_inspect_spreadsheet(args):
    command = [sys.executable, str(SPREADSHEET), "inspect", str(Path(args.file).expanduser().resolve())]
    if args.output:
        command.extend(["--output", str(Path(args.output).expanduser().resolve())])
    run(command)


def cmd_validate(args):
    command = [sys.executable, str(VALIDATOR / "audit_case.py"), str(Path(args.project).expanduser().resolve())]
    if args.strict:
        command.append("--strict")
    run(command)


def cmd_render(args):
    project = Path(args.project).expanduser().resolve()
    spec = official_dir(project) / "12-deck-spec.json"
    output = Path(args.output).expanduser().resolve() if args.output else project / "outputs" / "submission.pptx"
    run([sys.executable, str(DECK / "render_deck.py"), str(spec), str(output)])


def cmd_prototype(args):
    project = Path(args.project).expanduser().resolve()
    proto_script = ROOT / "scripts" / "generate_prototype.py"
    output = Path(args.output).expanduser().resolve() if args.output else project / "outputs" / "prototype.html"
    cmd = [sys.executable, str(proto_script), str(project), "--output", str(output)]
    if getattr(args, "theme", None):
        cmd.extend(["--theme", args.theme])
    run(cmd)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    doctor = sub.add_parser("doctor", help="Check the local CaseKit runtime")
    doctor.add_argument("--strict", action="store_true")
    doctor.set_defaults(func=cmd_doctor)

    init = sub.add_parser("init", help="Create an Obsidian-ready case workspace")
    init.add_argument("destination")
    init.add_argument("--preset", choices=("hackathon-sprint", "corporate-launchpad", "full-deep-drill"), help="Progressive preset")
    init.add_argument("--brief")
    init.add_argument("--rubric")
    init.add_argument("--deck")
    init.add_argument("--data")
    init.add_argument("--case-type", default="auto")
    init.add_argument("--language", default="Thai")
    init.add_argument("--layout", choices=("legacy", "clean"), default="legacy", help="legacy for simple work; clean for controlled team workspace")
    init.add_argument("--team", help="Optional comma-separated teammate folder names; used with clean layout")
    init.set_defaults(func=cmd_init)

    ingest = sub.add_parser("ingest", help="Copy an input into a case workspace and extract native PDF text")
    ingest.add_argument("project")
    ingest.add_argument("--kind", required=True, choices=("brief", "rubric", "deck", "data", "notes"))
    ingest.add_argument("--file", required=True)
    ingest.set_defaults(func=cmd_ingest)

    status = sub.add_parser("status", help="Show generic workspace progress and the next useful step")
    status.add_argument("project")
    status.set_defaults(func=cmd_status)

    check = sub.add_parser("check", help="Fast workspace health diagnostic")
    check.add_argument("project")
    check.add_argument("--strict", action="store_true")
    check.set_defaults(func=cmd_check)

    archive = sub.add_parser("archive", help="Cache offline snapshots of evidence sources")
    archive.add_argument("project")
    archive.add_argument("--source-id")
    archive.add_argument("--url")
    archive.add_argument("--title", default="")
    archive.add_argument("--publisher", default="")
    archive.add_argument("--force", action="store_true")
    archive.add_argument("--verify", action="store_true")
    archive.set_defaults(func=cmd_archive)

    # Interactive add helpers
    add_parser = sub.add_parser("add", help="Add entries to case ledgers")
    add_sub = add_parser.add_subparsers(dest="entity", required=True)

    add_claim_p = add_sub.add_parser("claim", help="Add an evidence claim to 01-evidence-ledger.csv")
    add_claim_p.add_argument("project")
    add_claim_p.add_argument("--claim", required=True, help="Claim statement")
    add_claim_p.add_argument("--url", required=True, help="Source URL")
    add_claim_p.add_argument("--publisher", required=True, help="Publisher name")
    add_claim_p.add_argument("--title", required=True, help="Source title")
    add_claim_p.add_argument("--page", help="Page or section")
    add_claim_p.add_argument("--page-or-section", help="Page or section")
    add_claim_p.add_argument("--quality", choices=("low", "medium", "high"), default="high")
    add_claim_p.add_argument("--recency", choices=("low", "medium", "high"), default="high")
    add_claim_p.add_argument("--relevance", choices=("low", "medium", "high"), default="high")
    add_claim_p.add_argument("--status", choices=("verified", "partially-verified", "unverified", "superseded"), default="verified")
    add_claim_p.add_argument("--source-type", default="primary")
    add_claim_p.add_argument("--owner", default="Research")
    add_claim_p.add_argument("--interpretation", default="")
    add_claim_p.add_argument("--accessed-date")
    add_claim_p.add_argument("--published-date")
    add_claim_p.add_argument("--verbatim-support", default="")
    add_claim_p.add_argument("--no-archive", dest="archive", action="store_false", help="Skip offline snapshot")
    add_claim_p.set_defaults(func=cmd_add_claim, archive=True)

    add_asm_p = add_sub.add_parser("assumption", help="Add a modeled assumption to 02-assumptions.csv")
    add_asm_p.add_argument("project")
    add_asm_p.add_argument("--variable", required=True, help="Variable name")
    add_asm_p.add_argument("--unit", required=True, help="Unit of measurement")
    add_asm_p.add_argument("--low", required=True, type=float, help="Low scenario value")
    add_asm_p.add_argument("--base", required=True, type=float, help="Base scenario value")
    add_asm_p.add_argument("--high", required=True, type=float, help="High scenario value")
    add_asm_p.add_argument("--basis", choices=("primary-research", "secondary-research", "analogy", "derived", "management-target", "team-judgment"), default="analogy")
    add_asm_p.add_argument("--source-ids", default="")
    add_asm_p.add_argument("--confidence", choices=("low", "medium", "high"), default="medium")
    add_asm_p.add_argument("--sensitivity", choices=("low", "medium", "high"), default="high")
    add_asm_p.add_argument("--validation-method", default="Pilot validation")
    add_asm_p.add_argument("--definition", default="")
    add_asm_p.add_argument("--owner", default="Finance")
    add_asm_p.add_argument("--status", choices=("open", "validated", "rejected", "superseded"), default="open")
    add_asm_p.set_defaults(func=cmd_add_assumption)

    add_dec_p = add_sub.add_parser("decision", help="Add a strategic decision to 04-decision-log.csv")
    add_dec_p.add_argument("project")
    add_dec_p.add_argument("--decision", required=True, help="Strategic decision statement")
    add_dec_p.add_argument("--date", help="Decision date YYYY-MM-DD")
    add_dec_p.add_argument("--alternatives", default="Status quo workaround")
    add_dec_p.add_argument("--criteria", default="Speed, cost, unit economics")
    add_dec_p.add_argument("--rationale", default="Optimal risk-adjusted decision")
    add_dec_p.add_argument("--refs", default="")
    add_dec_p.add_argument("--evidence-and-assumption-ids", dest="refs")
    add_dec_p.add_argument("--owner", default="Strategy")
    add_dec_p.add_argument("--status", choices=("proposed", "approved", "rejected", "superseded", "revisit"), default="approved")
    add_dec_p.set_defaults(func=cmd_add_decision)

    inspect = sub.add_parser("inspect-spreadsheet", help="Create an AI-readable workbook report")
    inspect.add_argument("file")
    inspect.add_argument("--output")
    inspect.set_defaults(func=cmd_inspect_spreadsheet)

    sync = sub.add_parser("sync-spreadsheet", help="Preview or apply spreadsheet values to the metric tree")
    sync.add_argument("project")
    sync.add_argument("mapping")
    sync.add_argument("--apply", action="store_true")
    sync.add_argument("--report")
    sync.set_defaults(func=cmd_sync_spreadsheet)

    validate = sub.add_parser("validate", help="Audit a case workspace")
    validate.add_argument("project")
    validate.add_argument("--strict", action="store_true")
    validate.set_defaults(func=cmd_validate)

    render = sub.add_parser("render", help="Render a project deck specification to PowerPoint")
    render.add_argument("project")
    render.add_argument("--output")
    render.set_defaults(func=cmd_render)

    prototype = sub.add_parser("prototype", help="Generate an interactive standalone HTML/Tailwind demo prototype")
    prototype.add_argument("project")
    prototype.add_argument("--output", "-o")
    prototype.add_argument("--theme", default="indigo")
    prototype.set_defaults(func=cmd_prototype)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
