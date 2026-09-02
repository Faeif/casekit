#!/usr/bin/env python3
"""Check evidence-ledger source metadata, with optional live URL and offline archive verification."""

import argparse
import csv
import hashlib
import re
import sys
from datetime import date
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


SEARCH_HOSTS = {"google.com", "www.google.com", "bing.com", "www.bing.com"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--online", action="store_true")
    parser.add_argument("--check-archive", action="store_true", help="Verify offline archive snapshots and SHA-256 hashes")
    parser.add_argument("--archive", action="store_true", help="Archive un-cached sources during check")
    parser.add_argument("--timeout", type=float, default=8.0)
    args = parser.parse_args()
    project = args.project.expanduser().resolve()
    official = project / "03-OFFICIAL"
    path = (official if official.is_dir() else project) / "01-evidence-ledger.csv"
    archive_dir = (project / "01-INPUTS" / "archive") if (project / "01-INPUTS").is_dir() else (project / "inputs" / "archive")
    errors, warnings = [], []

    if not path.exists():
        print(f"Evidence ledger not found: {path}")
        raise SystemExit(1)

    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))

    for line, row in enumerate(rows, 2):
        if not any((value or "").strip() for value in row.values()):
            continue
        url = (row.get("url") or "").strip()
        source_id = (row.get("source_id") or "").strip()
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            errors.append(f"line {line}: invalid URL {url!r}")
            continue
        if parsed.hostname in SEARCH_HOSTS:
            errors.append(f"line {line}: search-result URL is not an acceptable source")
        for field in ("publisher", "title", "accessed_date", "page_or_section", "interpretation"):
            if not (row.get(field) or "").strip():
                errors.append(f"line {line}: missing {field}")
        try:
            if date.fromisoformat((row.get("accessed_date") or "").strip()) > date.today():
                errors.append(f"line {line}: accessed_date is in the future")
        except ValueError:
            errors.append(f"line {line}: accessed_date must be YYYY-MM-DD")

        if args.check_archive and source_id:
            matches = list(archive_dir.glob(f"{source_id}_*.md")) if archive_dir.is_dir() else []
            if not matches:
                warnings.append(f"line {line}: missing offline archive snapshot for {source_id}")
            else:
                snapshot = matches[0]
                text = snapshot.read_text(encoding="utf-8")
                hash_match = re.search(r"content_hash_sha256:\s*([a-f0-9]{64})", text)
                if not hash_match:
                    errors.append(f"line {line}: archive snapshot {snapshot.name} missing valid content_hash_sha256")

        if args.archive and source_id and parsed.scheme in {"http", "https"}:
            try:
                from skills.casekit_research.scripts.archive_source import archive_source  # type: ignore
            except ImportError:
                root = Path(__file__).resolve().parent.parent.parent.parent
                sys.path.insert(0, str(root))
                from skills.casekit_research.scripts.archive_source import archive_source  # type: ignore
            archive_source(
                project=project,
                source_id=source_id,
                url=url,
                title=row.get("title", ""),
                publisher=row.get("publisher", ""),
                accessed_date=row.get("accessed_date", ""),
            )

        if args.online:
            try:
                request = Request(url, method="HEAD", headers={"User-Agent": "CaseKit-SourceCheck/1.0"})
                with urlopen(request, timeout=args.timeout) as response:
                    if response.status >= 400:
                        warnings.append(f"line {line}: HTTP {response.status} for {url}")
            except HTTPError as exc:
                warnings.append(f"line {line}: HTTP {exc.code} for {url}")
            except (URLError, TimeoutError) as exc:
                warnings.append(f"line {line}: unreachable during check: {url} ({exc})")

    for item in warnings:
        print(f"WARNING: {item}")
    for item in errors:
        print(f"ERROR: {item}")
    print(f"Source check complete: {len(errors)} error(s), {len(warnings)} warning(s)")
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
