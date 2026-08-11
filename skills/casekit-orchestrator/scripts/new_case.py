#!/usr/bin/env python3
"""Create a fresh CaseKit project workspace from the bundled template."""

import argparse
import shutil
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path, help="New project directory")
    args = parser.parse_args()

    destination = args.destination.expanduser().resolve()
    template = Path(__file__).resolve().parent.parent / "assets" / "project-template"
    if destination.exists():
        raise SystemExit(f"Refusing to overwrite existing path: {destination}")
    shutil.copytree(template, destination)
    print(f"Created CaseKit project: {destination}")


if __name__ == "__main__":
    main()

