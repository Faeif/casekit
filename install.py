#!/usr/bin/env python3
"""Install CaseKit transactionally for Agent Skills-compatible AI clients."""

import argparse
import importlib.util
import json
import shutil
import tempfile
from pathlib import Path


PLATFORMS = (
    "universal",
    "agents",
    "codex",
    "claude",
    "gemini",
    "antigravity",
    "legacy-codex",
    "legacy-gemini",
    "legacy-antigravity",
)


def remove_tree(path):
    if path.exists():
        shutil.rmtree(path)


def unique_paths(paths):
    result = []
    for path in paths:
        resolved = path.expanduser().resolve()
        if resolved not in result:
            result.append(resolved)
    return result


def resolve_targets(platform, scope, project_root, custom_target=None):
    """Return native discovery directories without depending on client binaries."""
    if custom_target is not None:
        return unique_paths([custom_target])

    home = Path.home()
    project_root = project_root.expanduser().resolve()
    if scope == "project":
        standard = project_root / ".agents" / "skills"
        mapping = {
            "universal": [standard, project_root / ".claude" / "skills"],
            "agents": [standard],
            "codex": [standard],
            "claude": [project_root / ".claude" / "skills"],
            "gemini": [standard],
            "antigravity": [standard],
            "legacy-codex": [project_root / ".codex" / "skills"],
            "legacy-gemini": [project_root / ".gemini" / "skills"],
            "legacy-antigravity": [project_root / ".agent" / "skills"],
        }
    else:
        standard = home / ".agents" / "skills"
        mapping = {
            "universal": [standard, home / ".claude" / "skills", home / ".gemini" / "config" / "skills"],
            "agents": [standard],
            "codex": [standard],
            "claude": [home / ".claude" / "skills"],
            "gemini": [standard],
            "antigravity": [home / ".gemini" / "config" / "skills"],
            "legacy-codex": [home / ".codex" / "skills"],
            "legacy-gemini": [home / ".gemini" / "skills"],
            "legacy-antigravity": [home / ".gemini" / "config" / "skills"],
        }
    return unique_paths(mapping[platform])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platform", choices=PLATFORMS, default="universal", help="AI client adapter (default: universal)")
    parser.add_argument("--scope", choices=("user", "project"), default="user", help="Install globally for the user or into a project (default: user)")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root used with --scope project (default: current directory)")
    parser.add_argument("--target", type=Path, help="Custom skills directory; overrides platform and scope discovery")
    parser.add_argument("--force", action="store_true", help="Replace existing CaseKit skills after all targets stage successfully")
    parser.add_argument("--dry-run", action="store_true", help="Show the complete install plan without changing files")
    parser.add_argument("--list-targets", action="store_true", help="Print resolved discovery directories and exit")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    source_root = root / "skills"
    manifest = json.loads((root / "casekit.json").read_text(encoding="utf-8"))
    names = manifest.get("skills", [])
    if not names:
        raise SystemExit("Manifest contains no skills")
    sources = [source_root / name for name in names]
    missing = [str(path) for path in sources if not (path / "SKILL.md").exists()]
    if missing:
        raise SystemExit(f"Refusing partial install; missing valid skill folders: {', '.join(missing)}")

    targets = resolve_targets(args.platform, args.scope, args.project_root, args.target)
    if args.list_targets:
        for target in targets:
            print(target)
        return

    conflicts = [target / source.name for target in targets for source in sources if (target / source.name).exists()]
    if conflicts and not args.force:
        joined = "\n- ".join(str(path) for path in conflicts)
        raise SystemExit(f"Refusing to overwrite existing skills:\n- {joined}\nRe-run with --force after reviewing them.")
    if args.dry_run:
        for target in targets:
            for source in sources:
                action = "replace" if (target / source.name).exists() else "install"
                print(f"Would {action} {source.name} -> {target / source.name}")
        return

    workspaces = []
    installed, backed_up = [], []
    try:
        for target in targets:
            target.mkdir(parents=True, exist_ok=True)
            stage = Path(tempfile.mkdtemp(prefix=".casekit-stage-", dir=target))
            backup = Path(tempfile.mkdtemp(prefix=".casekit-backup-", dir=target))
            workspaces.append((target, stage, backup))
            for source in sources:
                staged = stage / source.name
                shutil.copytree(source, staged)
                if not (staged / "SKILL.md").exists():
                    raise RuntimeError(f"Staging validation failed for {source.name} in {target}")

        for target, stage, backup in workspaces:
            for source in sources:
                destination = target / source.name
                if destination.exists():
                    saved = backup / source.name
                    destination.rename(saved)
                    backed_up.append((saved, destination))
                (stage / source.name).rename(destination)
                installed.append(destination)
    except Exception:
        for destination in reversed(installed):
            remove_tree(destination)
        for saved, destination in reversed(backed_up):
            if saved.exists():
                saved.rename(destination)
        raise
    finally:
        for _, stage, _ in workspaces:
            remove_tree(stage)

    for _, _, backup in workspaces:
        remove_tree(backup)
    for destination in installed:
        print(f"Installed {destination.name} -> {destination}")
    print(f"CaseKit {manifest.get('version')} installed transactionally to {len(targets)} discovery path(s). Restart or reload the AI client.")
    if importlib.util.find_spec("pptx") is None:
        print("Optional deck dependency is missing. From the CaseKit repository run: python3 -m pip install -r requirements.txt")


if __name__ == "__main__":
    main()
