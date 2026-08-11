#!/usr/bin/env python3
"""CaseKit command line: create, inspect, sync, validate, and render a case workspace."""

import argparse
import csv
import importlib.util
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ORCHESTRATOR = ROOT / "skills" / "casekit-orchestrator" / "scripts"
VALIDATOR = ROOT / "skills" / "casekit-validator" / "scripts"
DECK = ROOT / "skills" / "casekit-deck" / "scripts"
SPREADSHEET = ROOT / "skills" / "casekit-finance" / "scripts" / "spreadsheet_sync.py"
OFFICIAL_FILES = (
    "00-brief.md", "00-case-profile.md", "01-evidence-ledger.csv", "02-assumptions.csv",
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
        "This workspace uses the optional clean team layout.\n\n"
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
    official.mkdir()
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
    if team and args.layout != "clean":
        raise SystemExit("--team requires --layout clean")
    run([sys.executable, str(ORCHESTRATOR / "new_case.py"), str(destination)])
    if args.layout == "clean":
        apply_clean_layout(destination, team)
    run([sys.executable, str(ROOT / "install.py"), "--scope", "project", "--project-root", str(destination)])
    inputs = workspace_dir(destination, "01-INPUTS", "inputs")
    imported = {}
    for label, source in (("brief", args.brief), ("rubric", args.rubric), ("deck", args.deck), ("data", args.data)):
        target = copy_input(source, inputs, label)
        if target:
            imported[label] = str(target.relative_to(destination))
            if target.suffix.lower() == ".pdf":
                extract_pdf(target, inputs)
    profile = official_dir(destination) / "00-case-profile.md"
    text = profile.read_text(encoding="utf-8")
    text = text.replace("- Case type: auto", f"- Case type: {args.case_type}")
    text = text.replace("- Working language: Thai", f"- Working language: {args.language}")
    text = text.replace("- Input manifest: []", "- Input manifest: " + json.dumps(imported, ensure_ascii=False))
    profile.write_text(text, encoding="utf-8")
    print(f"CaseKit workspace ready: {destination}")
    print("Open this folder as an Obsidian vault, then start with " + ("00-START-HERE.md." if args.layout == "clean" else "README-START-HERE.md."))


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
    evidence = nonblank_rows(official / "01-evidence-ledger.csv")
    assumptions = nonblank_rows(official / "02-assumptions.csv")
    metrics = nonblank_rows(official / "03-metric-tree.csv")
    deck_path = official / "12-deck-spec.json"
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    doctor = sub.add_parser("doctor", help="Check the local CaseKit runtime")
    doctor.add_argument("--strict", action="store_true")
    doctor.set_defaults(func=cmd_doctor)
    init = sub.add_parser("init", help="Create an Obsidian-ready case workspace")
    init.add_argument("destination")
    init.add_argument("--brief")
    init.add_argument("--rubric")
    init.add_argument("--deck")
    init.add_argument("--data")
    init.add_argument("--case-type", default="auto")
    init.add_argument("--language", default="Thai")
    init.add_argument("--layout", choices=("legacy", "clean"), default="legacy", help="legacy for simple/single-user work; clean for a controlled team workspace")
    init.add_argument("--team", help="Optional comma-separated teammate folder names; used only with --layout clean")
    init.set_defaults(func=cmd_init)
    ingest = sub.add_parser("ingest", help="Copy an input into a case workspace and extract native PDF text")
    ingest.add_argument("project")
    ingest.add_argument("--kind", required=True, choices=("brief", "rubric", "deck", "data", "notes"))
    ingest.add_argument("--file", required=True)
    ingest.set_defaults(func=cmd_ingest)
    status = sub.add_parser("status", help="Show generic workspace progress and the next useful step")
    status.add_argument("project")
    status.set_defaults(func=cmd_status)
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
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
