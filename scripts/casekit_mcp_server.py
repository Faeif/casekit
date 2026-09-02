#!/usr/bin/env python3
"""CaseKit Model Context Protocol (MCP) Server Wrapper.

Exposes core CaseKit commands and ledgers to AI coding agents via
standard JSON-RPC 2.0 over stdio transport.
"""

import io
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "skills" / "casekit-validator" / "scripts"))
sys.path.insert(0, str(ROOT / "skills" / "casekit-research" / "scripts"))
sys.path.insert(0, str(ROOT / "skills" / "casekit-finance" / "scripts"))
sys.path.insert(0, str(ROOT / "scripts"))

from audit_case import audit
from archive_source import archive_source, archive_all_sources
from spreadsheet_sync import markdown_report as inspect_wb, sync as sync_wb


TOOLS = [
    {
        "name": "casekit_status",
        "description": "Retrieve workspace health, ledger row counts, layout, and recommended next actions.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Absolute path to CaseKit project directory"}
            },
            "required": ["project"],
        },
    },
    {
        "name": "casekit_validate",
        "description": "Run cross-ledger integrity audit, number drift detection, and schema verification.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Absolute path to CaseKit project directory"},
                "strict": {"type": "boolean", "description": "Treat warnings as errors", "default": False},
            },
            "required": ["project"],
        },
    },
    {
        "name": "casekit_check",
        "description": "Run fast diagnostic health check combining ledger counts, monotonicity, and drift detection.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Absolute path to CaseKit project directory"},
                "strict": {"type": "boolean", "description": "Treat warnings as errors", "default": False},
            },
            "required": ["project"],
        },
    },
    {
        "name": "casekit_add_claim",
        "description": "Add an evidence claim to 01-evidence-ledger.csv with auto-incremented CLM-xxx/SRC-xxx IDs and auto-snapshot.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Absolute path to CaseKit project"},
                "claim": {"type": "string", "description": "Factual statement backed by source"},
                "url": {"type": "string", "description": "Source URL"},
                "publisher": {"type": "string", "description": "Publisher or institution name"},
                "title": {"type": "string", "description": "Document or report title"},
                "page_or_section": {"type": "string", "default": "N/A"},
                "quality": {"type": "string", "enum": ["low", "medium", "high"], "default": "high"},
                "recency": {"type": "string", "enum": ["low", "medium", "high"], "default": "high"},
                "relevance": {"type": "string", "enum": ["low", "medium", "high"], "default": "high"},
                "status": {"type": "string", "enum": ["verified", "partially-verified", "unverified", "superseded"], "default": "verified"},
                "source_type": {"type": "string", "default": "primary"},
                "owner": {"type": "string", "default": "Research"},
                "interpretation": {"type": "string", "default": "Direct empirical evidence"},
                "archive": {"type": "boolean", "default": True},
            },
            "required": ["project", "claim", "url", "publisher", "title"],
        },
    },
    {
        "name": "casekit_add_assumption",
        "description": "Add a modeled assumption to 02-assumptions.csv with strict low <= base <= high monotonicity verification.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Absolute path to CaseKit project"},
                "variable": {"type": "string", "description": "Variable identifier"},
                "unit": {"type": "string", "description": "Unit of measurement (e.g. THB, %, rate)"},
                "low": {"type": "number", "description": "Conservative downside scenario"},
                "base": {"type": "number", "description": "Expected base scenario"},
                "high": {"type": "number", "description": "Optimistic upside scenario"},
                "basis": {"type": "string", "enum": ["primary-research", "secondary-research", "analogy", "derived", "management-target", "team-judgment"], "default": "analogy"},
                "source_ids": {"type": "string", "default": ""},
                "confidence": {"type": "string", "enum": ["low", "medium", "high"], "default": "medium"},
                "sensitivity": {"type": "string", "enum": ["low", "medium", "high"], "default": "high"},
                "validation_method": {"type": "string", "default": "Pilot validation"},
                "owner": {"type": "string", "default": "Finance"},
            },
            "required": ["project", "variable", "unit", "low", "base", "high"],
        },
    },
    {
        "name": "casekit_add_decision",
        "description": "Add a strategic decision to 04-decision-log.csv linked to evidence and assumption references.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Absolute path to CaseKit project"},
                "decision": {"type": "string", "description": "Strategic decision statement"},
                "date": {"type": "string", "description": "YYYY-MM-DD date"},
                "alternatives": {"type": "string", "default": "Status quo workaround"},
                "criteria": {"type": "string", "default": "Speed, cost, unit economics"},
                "rationale": {"type": "string", "default": "Optimal trade-off"},
                "refs": {"type": "string", "default": ""},
                "owner": {"type": "string", "default": "Strategy"},
                "status": {"type": "string", "enum": ["proposed", "approved", "rejected", "superseded", "revisit"], "default": "approved"},
            },
            "required": ["project", "decision"],
        },
    },
    {
        "name": "casekit_render_deck",
        "description": "Render 16:9 widescreen PowerPoint presentation from 12-deck-spec.json.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Absolute path to CaseKit project"},
                "output_path": {"type": "string", "description": "Target .pptx output path (optional)"},
            },
            "required": ["project"],
        },
    },
    {
        "name": "casekit_sync_spreadsheet",
        "description": "Sync financial model Named Ranges and cell values to metric tree with CFO sanity gates.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Absolute path to CaseKit project"},
                "mapping_file": {"type": "string", "description": "Path to data-import-map.json"},
                "apply": {"type": "boolean", "default": False, "description": "Apply values directly to 03-metric-tree.csv"},
                "report": {"type": "string", "description": "Path to write Markdown sync report (optional)"},
            },
            "required": ["project", "mapping_file"],
        },
    },
    {
        "name": "casekit_inspect_spreadsheet",
        "description": "Inspect Excel workbook named ranges, formulas, and venture CFO health gates.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to .xlsx workbook"},
                "output_path": {"type": "string", "description": "Path to write inspection report (optional)"},
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "casekit_archive_source",
        "description": "Download and cache offline text/PDF snapshot of an evidence URL with SHA-256 integrity hash.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Absolute path to CaseKit project"},
                "source_id": {"type": "string", "description": "Source ID (e.g. SRC-001)"},
                "url": {"type": "string", "description": "Source URL"},
                "title": {"type": "string", "default": ""},
                "publisher": {"type": "string", "default": ""},
                "force": {"type": "boolean", "default": False},
            },
            "required": ["project", "source_id", "url"],
        },
    },
    {
        "name": "casekit_generate_prototype",
        "description": "Generate a single-file, minimalist interactive HTML/Tailwind prototype for live demonstrations.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Absolute path to CaseKit project"},
                "output_path": {"type": "string", "description": "Target HTML output path (optional)"},
                "theme": {"type": "string", "description": "Theme palette (default: indigo)", "default": "indigo"},
            },
            "required": ["project"],
        },
    },
]


import contextlib


def handle_tool_call(name: str, arguments: dict) -> dict:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        try:
            if name == "casekit_status":
                project = Path(arguments["project"]).expanduser().resolve()
                official = project / "03-OFFICIAL" if (project / "03-OFFICIAL").is_dir() else project
                errors, warnings, counts = audit(project)
                deck_file = official / "12-deck-spec.json"
                slides = 0
                if deck_file.exists():
                    try:
                        slides = len(json.loads(deck_file.read_text(encoding="utf-8")).get("slides", []))
                    except Exception:
                        pass
                payload = {
                    "project": str(project),
                    "layout": "clean team" if official != project else "legacy",
                    "counts": counts,
                    "slides": slides,
                    "ready": not errors,
                    "errors_count": len(errors),
                    "warnings_count": len(warnings),
                }
                return {"content": [{"type": "text", "text": json.dumps(payload, indent=2)}]}

            elif name == "casekit_validate":
                project = Path(arguments["project"]).expanduser().resolve()
                strict = arguments.get("strict", False)
                errors, warnings, counts = audit(project)
                ready = not errors and (not strict or not warnings)
                payload = {
                    "project": str(project),
                    "ready": ready,
                    "errors": errors,
                    "warnings": warnings,
                    "counts": counts,
                }
                return {"content": [{"type": "text", "text": json.dumps(payload, indent=2)}]}

            elif name == "casekit_check":
                project = Path(arguments["project"]).expanduser().resolve()
                strict = arguments.get("strict", False)
                errors, warnings, counts = audit(project)
                ready = not errors and (not strict or not warnings)
                payload = {
                    "project": str(project),
                    "status": "PASSED" if ready else "FAILED",
                    "ready": ready,
                    "counts": counts,
                    "errors": errors,
                    "warnings": warnings,
                }
                return {"content": [{"type": "text", "text": json.dumps(payload, indent=2)}]}

            elif name == "casekit_add_claim":
                project = Path(arguments["project"]).expanduser().resolve()
                import casekit
                class DummyArgs:
                    pass
                args = DummyArgs()
                args.project = str(project)
                args.claim = arguments["claim"]
                args.url = arguments["url"]
                args.publisher = arguments["publisher"]
                args.title = arguments["title"]
                args.page = arguments.get("page_or_section", "N/A")
                args.page_or_section = args.page
                args.quality = arguments.get("quality", "high")
                args.recency = arguments.get("recency", "high")
                args.relevance = arguments.get("relevance", "high")
                args.status = arguments.get("status", "verified")
                args.source_type = arguments.get("source_type", "primary")
                args.owner = arguments.get("owner", "Research")
                args.interpretation = arguments.get("interpretation", "Direct empirical evidence")
                args.archive = arguments.get("archive", True)
                args.accessed_date = None
                args.published_date = None
                args.verbatim_support = ""
                res = casekit.cmd_add_claim(args)
                return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}

            elif name == "casekit_add_assumption":
                project = Path(arguments["project"]).expanduser().resolve()
                import casekit
                class DummyArgs:
                    pass
                args = DummyArgs()
                args.project = str(project)
                args.variable = arguments["variable"]
                args.unit = arguments["unit"]
                args.low = arguments["low"]
                args.base = arguments["base"]
                args.high = arguments["high"]
                args.basis = arguments.get("basis", "analogy")
                args.source_ids = arguments.get("source_ids", "")
                args.confidence = arguments.get("confidence", "medium")
                args.sensitivity = arguments.get("sensitivity", "high")
                args.validation_method = arguments.get("validation_method", "Pilot validation")
                args.definition = arguments.get("definition", "")
                args.owner = arguments.get("owner", "Finance")
                args.status = arguments.get("status", "open")
                res = casekit.cmd_add_assumption(args)
                return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}

            elif name == "casekit_add_decision":
                project = Path(arguments["project"]).expanduser().resolve()
                import casekit
                class DummyArgs:
                    pass
                args = DummyArgs()
                args.project = str(project)
                args.decision = arguments["decision"]
                args.date = arguments.get("date")
                args.alternatives = arguments.get("alternatives", "Status quo workaround")
                args.criteria = arguments.get("criteria", "Speed, cost, unit economics")
                args.rationale = arguments.get("rationale", "Optimal trade-off")
                args.refs = arguments.get("refs", "")
                args.owner = arguments.get("owner", "Strategy")
                args.status = arguments.get("status", "approved")
                res = casekit.cmd_add_decision(args)
                return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}

            elif name == "casekit_render_deck":
                project = Path(arguments["project"]).expanduser().resolve()
                official = project / "03-OFFICIAL" if (project / "03-OFFICIAL").is_dir() else project
                spec = official / "12-deck-spec.json"
                out = Path(arguments["output_path"]).expanduser().resolve() if arguments.get("output_path") else project / "outputs" / "submission.pptx"
                out.parent.mkdir(parents=True, exist_ok=True)
                res = subprocess.run([sys.executable, str(ROOT / "skills" / "casekit-deck" / "scripts" / "render_deck.py"), str(spec), str(out)], capture_output=True, text=True)
                if res.returncode != 0:
                    return {"isError": True, "content": [{"type": "text", "text": f"Deck render error: {res.stderr or res.stdout}"}]}
                return {"content": [{"type": "text", "text": json.dumps({"output_file": str(out), "status": "rendered"}, indent=2)}]}

            elif name == "casekit_sync_spreadsheet":
                project = Path(arguments["project"]).expanduser().resolve()
                mapping_file = Path(arguments["mapping_file"]).expanduser().resolve()
                apply_flag = arguments.get("apply", False)
                report_path = Path(arguments["report"]).expanduser().resolve() if arguments.get("report") else None
                report_dict = sync_wb(project, mapping_file, apply=apply_flag)
                if report_path:
                    report_path.parent.mkdir(parents=True, exist_ok=True)
                    report_path.write_text(json.dumps(report_dict, ensure_ascii=False, indent=2), encoding="utf-8")
                return {"content": [{"type": "text", "text": json.dumps(report_dict, indent=2)}]}

            elif name == "casekit_inspect_spreadsheet":
                file_path = Path(arguments["file_path"]).expanduser().resolve()
                output_path = Path(arguments["output_path"]).expanduser().resolve() if arguments.get("output_path") else None
                report_text = inspect_wb(file_path)
                if output_path:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_text(report_text, encoding="utf-8")
                return {"content": [{"type": "text", "text": report_text}]}

            elif name == "casekit_archive_source":
                project = Path(arguments["project"]).expanduser().resolve()
                res = archive_source(
                    project=project,
                    source_id=arguments["source_id"],
                    url=arguments["url"],
                    title=arguments.get("title", ""),
                    publisher=arguments.get("publisher", ""),
                    force=arguments.get("force", False),
                )
                return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}

            elif name == "casekit_generate_prototype":
                from generate_prototype import generate_prototype
                project = Path(arguments["project"]).expanduser().resolve()
                out_path = Path(arguments["output_path"]).expanduser().resolve() if arguments.get("output_path") else None
                theme = arguments.get("theme", "indigo")
                res_path = generate_prototype(project, out_path, theme=theme)
                return {"content": [{"type": "text", "text": json.dumps({"prototype_file": str(res_path), "status": "generated"}, indent=2)}]}

            else:
                return {"isError": True, "content": [{"type": "text", "text": f"Unknown tool: {name}"}]}

        except (Exception, SystemExit) as exc:
            return {"isError": True, "content": [{"type": "text", "text": f"Error executing tool {name}: {exc}"}]}


def run_server():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception:
            continue

        method = req.get("method")
        msg_id = req.get("id")

        if method == "initialize":
            resp = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}, "resources": {}},
                    "serverInfo": {"name": "casekit-mcp-server", "version": "1.1.0"},
                },
            }
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        elif method == "notifications/initialized":
            # No response required for notification
            pass

        elif method == "ping":
            resp = {"jsonrpc": "2.0", "id": msg_id, "result": {}}
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        elif method == "tools/list":
            resp = {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS}}
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        elif method == "tools/call":
            params = req.get("params", {})
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            call_res = handle_tool_call(tool_name, arguments)
            resp = {"jsonrpc": "2.0", "id": msg_id, "result": call_res}
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        elif method == "resources/list":
            resp = {"jsonrpc": "2.0", "id": msg_id, "result": {"resources": []}}
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        elif msg_id is not None:
            resp = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("--help", "-h", "help"):
        print("CaseKit Model Context Protocol (MCP) Server. Communicates via JSON-RPC 2.0 over stdio.")
        sys.exit(0)
    run_server()
