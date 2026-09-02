#!/usr/bin/env python3
"""Auto-archival snapshot engine for CaseKit research sources."""

import argparse
import csv
import hashlib
import io
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


def get_archive_dir(project: Path) -> Path:
    project = project.expanduser().resolve()
    if (project / "01-INPUTS").is_dir():
        archive = project / "01-INPUTS" / "archive"
    elif (project / "inputs").is_dir():
        archive = project / "inputs" / "archive"
    elif (project / "03-OFFICIAL").is_dir():
        archive = project / "01-INPUTS" / "archive"
    else:
        archive = project / "inputs" / "archive"
    archive.mkdir(parents=True, exist_ok=True)
    return archive


def sanitize_name(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "_", value or "")
    return cleaned.strip("_") or "doc"


def archive_source(
    project: Path,
    source_id: str,
    url: str,
    title: str = "",
    publisher: str = "",
    accessed_date: str = "",
    force: bool = False,
    timeout: float = 8.0,
) -> dict:
    project = Path(project).expanduser().resolve()
    archive_dir = get_archive_dir(project)
    parsed = urlparse(url)
    domain = sanitize_name(parsed.netloc or "source")
    slug_base = title or (Path(parsed.path).stem if parsed.path else "doc")
    slug = sanitize_name(slug_base)[:40]
    filename = f"{source_id}_{domain}_{slug}.md"
    snapshot_path = archive_dir / filename

    if snapshot_path.exists() and not force:
        content = snapshot_path.read_text(encoding="utf-8")
        hash_match = re.search(r"content_hash_sha256:\s*([a-f0-9]{64})", content)
        existing_hash = hash_match.group(1) if hash_match else hashlib.sha256(content.encode("utf-8")).hexdigest()
        return {
            "snapshot_path": str(snapshot_path),
            "status": "existing",
            "source_id": source_id,
            "url": url,
            "content_hash_sha256": existing_hash,
        }

    accessed = accessed_date or date.today().isoformat()
    http_status = 200
    status = "archived"
    body = ""
    error_msg = None

    if parsed.scheme in {"http", "https"} and parsed.netloc:
        try:
            req = Request(url, headers={"User-Agent": "CaseKit-Archive/1.0"})
            with urlopen(req, timeout=timeout) as response:
                http_status = getattr(response, "status", 200)
                payload = response.read()
                content_type = response.headers.get("Content-Type", "").lower()
                if "application/pdf" in content_type or url.lower().endswith(".pdf"):
                    try:
                        from pypdf import PdfReader
                        reader = PdfReader(io.BytesIO(payload))
                        extracted_pages = [page.extract_text() or "" for page in reader.pages]
                        body = "\n\n".join(extracted_pages).strip() or f"Extracted {len(reader.pages)} PDF pages (no selectable text)."
                    except Exception:
                        body = f"Binary PDF document ({len(payload)} bytes)."
                else:
                    try:
                        body = payload.decode("utf-8")
                    except UnicodeDecodeError:
                        body = payload.decode("latin-1", errors="replace")
                payload_hash = hashlib.sha256(payload).hexdigest()
        except HTTPError as exc:
            http_status = exc.code
            status = "fetch-failed"
            error_msg = f"HTTP {exc.code}: {exc.reason}"
            body = f"Snapshot fetch failed: {error_msg}\nURL: {url}"
            payload_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()
        except (URLError, TimeoutError, Exception) as exc:
            http_status = 0
            status = "fetch-failed"
            error_msg = str(exc)
            body = f"Snapshot fetch failed: {error_msg}\nURL: {url}"
            payload_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()
    else:
        status = "offline-snapshot"
        body = f"Offline / synthetic source snapshot.\nTitle: {title}\nPublisher: {publisher}\nURL: {url}"
        payload_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()

    header = (
        f"---\n"
        f"source_id: {source_id}\n"
        f"url: {url}\n"
        f"title: {title or 'N/A'}\n"
        f"publisher: {publisher or 'N/A'}\n"
        f"accessed_date: {accessed}\n"
        f"http_status: {http_status}\n"
        f"content_hash_sha256: {payload_hash}\n"
        f"archived_by: casekit-archive/1.0\n"
        f"---\n\n"
        f"# Source Content Snapshot\n\n"
        f"{body}\n"
    )

    snapshot_path.write_text(header, encoding="utf-8")
    result = {
        "snapshot_path": str(snapshot_path),
        "status": status,
        "source_id": source_id,
        "url": url,
        "content_hash_sha256": payload_hash,
    }
    if error_msg:
        result["error"] = error_msg
    return result


def archive_all_sources(project: Path, force: bool = False, timeout: float = 8.0) -> list[dict]:
    project = Path(project).expanduser().resolve()
    official = project / "03-OFFICIAL"
    path = (official if official.is_dir() else project) / "01-evidence-ledger.csv"
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    results = []
    seen_sources = set()
    for row in rows:
        source_id = (row.get("source_id") or "").strip()
        url = (row.get("url") or "").strip()
        if not source_id or not url or source_id in seen_sources:
            continue
        seen_sources.add(source_id)
        title = (row.get("title") or "").strip()
        publisher = (row.get("publisher") or "").strip()
        accessed = (row.get("accessed_date") or "").strip()
        res = archive_source(
            project=project,
            source_id=source_id,
            url=url,
            title=title,
            publisher=publisher,
            accessed_date=accessed,
            force=force,
            timeout=timeout,
        )
        results.append(res)
    return results


def verify_archive(project: Path) -> tuple[list[str], list[str]]:
    project = Path(project).expanduser().resolve()
    archive_dir = get_archive_dir(project)
    official = project / "03-OFFICIAL"
    path = (official if official.is_dir() else project) / "01-evidence-ledger.csv"
    errors, warnings = [], []
    if not path.exists():
        return errors, warnings
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    for line, row in enumerate(rows, 2):
        source_id = (row.get("source_id") or "").strip()
        if not source_id:
            continue
        matches = list(archive_dir.glob(f"{source_id}_*.md"))
        if not matches:
            warnings.append(f"01-evidence-ledger.csv:{line}: missing offline archive snapshot for {source_id}")
        else:
            snapshot_file = matches[0]
            content = snapshot_file.read_text(encoding="utf-8")
            hash_match = re.search(r"content_hash_sha256:\s*([a-f0-9]{64})", content)
            if not hash_match:
                errors.append(f"{snapshot_file.name}: missing or invalid content_hash_sha256")
    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path, help="Path to CaseKit project")
    parser.add_argument("--source-id", help="Specific source ID to archive")
    parser.add_argument("--url", help="Specific URL to archive")
    parser.add_argument("--title", default="", help="Source title")
    parser.add_argument("--publisher", default="", help="Source publisher")
    parser.add_argument("--force", action="store_true", help="Overwrite existing snapshots")
    parser.add_argument("--verify", action="store_true", help="Verify existing archive snapshots")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    project = args.project.expanduser().resolve()
    if args.verify:
        errors, warnings = verify_archive(project)
        for w in warnings:
            print(f"WARNING: {w}")
        for e in errors:
            print(f"ERROR: {e}")
        print(f"Archive verification complete: {len(errors)} error(s), {len(warnings)} warning(s)")
        sys.exit(1 if errors else 0)

    if args.source_id and args.url:
        res = archive_source(
            project=project,
            source_id=args.source_id,
            url=args.url,
            title=args.title,
            publisher=args.publisher,
            force=args.force,
        )
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(f"Archived {res['source_id']} -> {res['snapshot_path']} (status: {res['status']})")
    else:
        results = archive_all_sources(project, force=args.force)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"Archived {len(results)} source(s) into {get_archive_dir(project)}")


if __name__ == "__main__":
    main()
