#!/usr/bin/env python3
"""CaseKit command line: create, inspect, sync, validate, and render a case workspace."""

import argparse
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


def extract_pdf(target, project):
    if importlib.util.find_spec("pypdf") is None:
        print("PDF copied. Install pypdf then rerun an AI intake to extract native PDF text.")
        return
    from pypdf import PdfReader
    reader = PdfReader(str(target))
    extracted = "\n\n".join(page.extract_text() or "" for page in reader.pages)
    text_path = project / "inputs" / "extracted" / f"{target.stem}.md"
    text_path.parent.mkdir(parents=True, exist_ok=True)
    text_path.write_text(f"# Extracted: {target.name}\n\n{extracted}\n", encoding="utf-8")
    print(f"Extracted {len(reader.pages)} PDF page(s) -> {text_path}")


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
    run([sys.executable, str(ORCHESTRATOR / "new_case.py"), str(destination)])
    run([sys.executable, str(ROOT / "install.py"), "--scope", "project", "--project-root", str(destination)])
    inputs = workspace_dir(destination, "01-INPUTS", "inputs")
    imported = {}
    for label, source in (("brief", args.brief), ("rubric", args.rubric), ("deck", args.deck), ("data", args.data)):
        target = copy_input(source, inputs, label)
        if target:
            imported[label] = str(target.relative_to(destination))
            if target.suffix.lower() == ".pdf":
                extract_pdf(target, destination)
    profile = destination / "00-case-profile.md"
    text = profile.read_text(encoding="utf-8")
    text = text.replace("- Case type: auto", f"- Case type: {args.case_type}")
    text = text.replace("- Working language: Thai", f"- Working language: {args.language}")
    text = text.replace("- Input manifest: []", "- Input manifest: " + json.dumps(imported, ensure_ascii=False))
    profile.write_text(text, encoding="utf-8")
    print(f"CaseKit workspace ready: {destination}")
    print("Open this folder as an Obsidian vault, then start with README-START-HERE.md.")


def cmd_ingest(args):
    project = Path(args.project).expanduser().resolve()
    if not project.is_dir():
        raise SystemExit(f"Project directory does not exist: {project}")
    target = copy_input(args.file, workspace_dir(project, "01-INPUTS", "inputs"), args.kind)
    print(f"Imported {args.kind}: {target}")
    if target.suffix.lower() == ".pdf":
        extract_pdf(target, project)


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
    init.set_defaults(func=cmd_init)
    ingest = sub.add_parser("ingest", help="Copy an input into a case workspace and extract native PDF text")
    ingest.add_argument("project")
    ingest.add_argument("--kind", required=True, choices=("brief", "rubric", "deck", "data", "notes"))
    ingest.add_argument("--file", required=True)
    ingest.set_defaults(func=cmd_ingest)
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
