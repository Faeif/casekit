#!/usr/bin/env python3
"""Create a fresh CaseKit project workspace from presets or the bundled template."""

import argparse
import json
import shutil
import sys
from pathlib import Path


SPRINT_FILES = (
    "00-START-HERE.md", "00-brief.md", "00-case-profile.md", "01-evidence-ledger.csv",
    "02-assumptions.csv", "03-metric-tree.csv", "12-deck-spec.json", "00-DASHBOARD.md",
)

CORPORATE_FILES = SPRINT_FILES + (
    "04-decision-log.csv", "05-risk-register.csv", "06-workstream-status.md",
    "11-rubric-scorecard.csv", "option-portfolio.csv", "qna-bank.csv",
    "integration-contract.csv",
)


def scaffold_preset(destination: Path, preset: str, template: Path):
    destination.mkdir(parents=True, exist_ok=True)
    obsidian_src = template / ".obsidian"
    if obsidian_src.exists():
        shutil.copytree(obsidian_src, destination / ".obsidian", dirs_exist_ok=True)

    if preset == "hackathon-sprint":
        for fname in SPRINT_FILES:
            src = template / fname
            if src.exists():
                shutil.copy2(src, destination / fname)
        inputs_dir = destination / "inputs"
        inputs_dir.mkdir(exist_ok=True)
        (inputs_dir / "README.md").write_text("# Inputs\n\nPlace raw hackathon brief, rubric, and data here.\n", encoding="utf-8")
        (inputs_dir / "archive").mkdir(exist_ok=True)
        (destination / "00-START-HERE.md").write_text(
            "# Hackathon Sprint Start Here\n\n"
            "1. Fill in `00-brief.md` and `00-case-profile.md`.\n"
            "2. Capture verified primary evidence in `01-evidence-ledger.csv`.\n"
            "3. Model uncertain assumptions in `02-assumptions.csv`.\n"
            "4. Construct the North Star metric tree in `03-metric-tree.csv`.\n"
            "5. Build the presentation deck spec in `12-deck-spec.json`.\n",
            encoding="utf-8",
        )

    elif preset == "corporate-launchpad":
        for fname in CORPORATE_FILES:
            src = template / fname
            if src.exists():
                shutil.copy2(src, destination / fname)
        eng_dir = destination / "engineering"
        eng_dir.mkdir(exist_ok=True)
        if (template / "engineering" / "architecture.md").exists():
            shutil.copy2(template / "engineering" / "architecture.md", eng_dir / "architecture.md")
        inputs_dir = destination / "inputs"
        inputs_dir.mkdir(exist_ok=True)
        (inputs_dir / "README.md").write_text("# Inputs\n\nPlace corporate brief, rubric, legacy contracts, and data here.\n", encoding="utf-8")
        (inputs_dir / "archive").mkdir(exist_ok=True)
        (destination / "00-START-HERE.md").write_text(
            "# Corporate Launchpad Start Here\n\n"
            "1. Define case profile and strategic goals in `00-case-profile.md`.\n"
            "2. Score options portfolio in `option-portfolio.csv`.\n"
            "3. Log enterprise integration contracts in `integration-contract.csv`.\n"
            "4. Log risk register and mitigation in `05-risk-register.csv`.\n"
            "5. Prepare executive Q&A responses in `qna-bank.csv`.\n",
            encoding="utf-8",
        )

    elif preset == "full-deep-drill":
        shutil.copytree(template, destination, dirs_exist_ok=True)
        # Setup clean 3-tier layout
        inputs = destination / "01-INPUTS"
        if not inputs.exists():
            (destination / "inputs").rename(inputs) if (destination / "inputs").exists() else inputs.mkdir(exist_ok=True)
        (inputs / "archive").mkdir(exist_ok=True)

        team = destination / "02-TEAM"
        if not team.exists():
            (destination / "00-INBOX").rename(team) if (destination / "00-INBOX").exists() else team.mkdir(exist_ok=True)
        (team / "README.md").write_text("# Team drafts\n\nEach person works only in their own folder.\n", encoding="utf-8")

        official = destination / "03-OFFICIAL"
        official.mkdir(exist_ok=True)
        official_files = (
            "00-brief.md", "00-case-profile.md", "01-evidence-ledger.csv", "02-assumptions.csv",
            "03-metric-tree.csv", "04-decision-log.csv", "05-risk-register.csv", "06-workstream-status.md",
            "07-final-integrated-case.md", "08-premises.csv", "09-experiments.csv", "10-team-charter.md",
            "11-rubric-scorecard.csv", "12-deck-spec.json", "13-submission-checklist.md", "16-vision-growth-plan.md",
            "data-import-map.json", "engineering-delivery-plan.md", "idea-backlog.csv", "integration-contract.csv",
            "option-portfolio.csv", "qna-bank.csv", "research-backlog.csv", "engineering",
        )
        for name in official_files:
            source = destination / name
            if source.exists():
                source.rename(official / name)

        for name in ("README-START-HERE.md", "TEAM-WORKFLOW.md"):
            source = destination / name
            if source.exists():
                source.unlink()

        (destination / "README.md").write_text(
            "# Case workspace (Full Deep Drill)\n\n"
            "| Folder | Purpose |\n|---|---|\n"
            "| `01-INPUTS/` | Original brief, rubric, deck, Excel, and raw data |\n"
            "| `02-TEAM/` | Personal draft folders; create one folder per teammate |\n"
            "| `03-OFFICIAL/` | Approved evidence, numbers, decisions, and deck only |\n\n",
            encoding="utf-8",
        )
        (destination / "00-START-HERE.md").write_text(
            "# Start here (Full Deep Drill)\n\n"
            "1. Put official files in `01-INPUTS/`.\n"
            "2. Each teammate works only in `02-TEAM/<name>/`.\n"
            "3. Promote team-approved work into `03-OFFICIAL/`.\n"
            "4. Before deck freeze run `python3 casekit.py validate . --strict`.\n",
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
    else:
        # Default full copy
        shutil.copytree(template, destination, dirs_exist_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path, help="New project directory")
    parser.add_argument(
        "--preset",
        choices=("hackathon-sprint", "corporate-launchpad", "full-deep-drill"),
        help="Progressive project preset",
    )
    args = parser.parse_args()

    destination = args.destination.expanduser().resolve()
    template = Path(__file__).resolve().parent.parent / "assets" / "project-template"
    if destination.exists():
        raise SystemExit(f"Refusing to overwrite existing path: {destination}")
    scaffold_preset(destination, args.preset, template)
    print(f"Created CaseKit project: {destination}" + (f" (preset: {args.preset})" if args.preset else ""))


if __name__ == "__main__":
    main()
