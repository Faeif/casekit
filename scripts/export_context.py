#!/usr/bin/env python3
"""Export provider-neutral CaseKit instructions for AI clients without skill discovery."""

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"


def skill_files(skill):
    files = [skill / "SKILL.md"]
    for folder in ("references", "assets"):
        location = skill / folder
        if location.exists():
            files.extend(sorted(path for path in location.rglob("*") if path.is_file() and path.suffix.lower() in {".md", ".csv", ".json", ".txt"}))
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill", action="append", dest="skills", help="Skill folder name; repeat to include multiple skills")
    parser.add_argument("--all", action="store_true", help="Include every CaseKit skill")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    available = {path.name: path for path in SKILLS.glob("casekit-*") if path.is_dir()}
    names = sorted(available) if args.all else (args.skills or ["casekit-orchestrator"])
    unknown = [name for name in names if name not in available]
    if unknown:
        raise SystemExit(f"Unknown skill(s): {', '.join(unknown)}")

    parts = [
        "# CaseKit portable context bundle\n",
        "Use the following CaseKit files as authoritative task instructions. Match the user's language. Keep one shared set of Claim, Source, Assumption, Metric, Premise, Experiment, Decision, and Risk IDs. Treat scripts as deterministic helpers when the client can execute them; otherwise reproduce their logic transparently.\n",
    ]
    for name in names:
        parts.append(f"\n## Skill package: {name}\n")
        for path in skill_files(available[name]):
            relative = path.relative_to(ROOT).as_posix()
            parts.append(f"\n<casekit-file path=\"{relative}\">\n")
            parts.append(path.read_text(encoding="utf-8-sig").rstrip() + "\n")
            parts.append("</casekit-file>\n")
        scripts = sorted((available[name] / "scripts").glob("*")) if (available[name] / "scripts").exists() else []
        if scripts:
            parts.append("\nDeterministic helper scripts available in the repository:\n")
            parts.extend(f"- {path.relative_to(ROOT).as_posix()}\n" for path in scripts if path.is_file())

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("".join(parts), encoding="utf-8")
    print(f"Exported {len(names)} skill(s) -> {args.output.resolve()}")


if __name__ == "__main__":
    main()
