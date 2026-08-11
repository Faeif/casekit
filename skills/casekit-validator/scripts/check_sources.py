#!/usr/bin/env python3
"""Check evidence-ledger source metadata, with optional live URL verification."""

import argparse
import csv
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
    parser.add_argument("--timeout", type=float, default=8.0)
    args = parser.parse_args()
    project = args.project.expanduser().resolve()
    official = project / "03-OFFICIAL"
    path = (official if official.is_dir() else project) / "01-evidence-ledger.csv"
    errors, warnings = [], []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    for line, row in enumerate(rows, 2):
        if not any((value or "").strip() for value in row.values()):
            continue
        url = (row.get("url") or "").strip()
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
