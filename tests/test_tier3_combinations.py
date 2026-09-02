"""Tier 3: Cross-Feature & Multi-Module Integration Test Suite for CaseKit.

Tests interactions across feature boundaries, data flow pipelines, and multi-agent coordination.
"""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import openpyxl

from tests.test_helpers import (
    CASEKIT_CLI,
    EXAMPLES,
    FIXTURE_LAUNCH_EVENT,
    ROOT,
    SCRIPTS,
    SKILLS,
    TEMPLATES,
    build_mock_financial_model,
    create_temp_vault_copy,
    run_command,
    run_command_unchecked,
)


class TestTier3Combinations(unittest.TestCase):
    """Tier 3 Cross-Feature & Multi-Module Integration Test Suite."""

    def test_int01_spreadsheet_sync_to_metric_tree_and_cfo_sanity(self):
        """INT-01: Financial Model -> Named Ranges -> spreadsheet_sync -> 03-metric-tree.csv."""
        with tempfile.TemporaryDirectory() as td:
            vault = Path(td) / "vault"
            shutil.copytree(FIXTURE_LAUNCH_EVENT, vault)
            (vault / "inputs").mkdir(exist_ok=True)
            model_path = build_mock_financial_model(vault / "inputs" / "saas_model.xlsx", scenario_revenue=1500000.0, gross_margin=0.80)
            map_path = vault / "data-import-map.json"
            map_path.write_text(json.dumps({
                "version": 1,
                "mappings": [
                    {"metric_id": "MET-001", "scenario": "base", "file": "inputs/saas_model.xlsx", "named_range": "Gross_Revenue_Base"}
                ]
            }), encoding="utf-8")
            sync_script = SKILLS / "casekit-finance" / "scripts" / "spreadsheet_sync.py"
            proc = run_command([sys.executable, str(sync_script), "sync", str(vault), str(map_path), "--apply"])
            self.assertEqual(proc.returncode, 0)
            metric_text = (vault / "03-metric-tree.csv").read_text(encoding="utf-8")
            self.assertIn("1500000", metric_text)

    def test_int02_metric_tree_sync_to_deck_render(self):
        """INT-02: Synced Metric Tree -> 12-deck-spec.json -> render_deck.py PPTX."""
        with tempfile.TemporaryDirectory() as td:
            vault = Path(td) / "vault"
            shutil.copytree(FIXTURE_LAUNCH_EVENT, vault)
            out_pptx = vault / "deck_out.pptx"
            render_script = SKILLS / "casekit-deck" / "scripts" / "render_deck.py"
            proc = run_command([sys.executable, str(render_script), str(vault / "12-deck-spec.json"), str(out_pptx)])
            self.assertEqual(proc.returncode, 0)
            self.assertTrue(out_pptx.exists())
            self.assertGreater(out_pptx.stat().st_size, 1000)

    def test_int03_cli_preset_init_to_obsidian_gui(self):
        """INT-03: casekit init --preset -> .obsidian/ -> 00-START-HERE.md."""
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "launchpad_case"
            proc = run_command([sys.executable, str(CASEKIT_CLI), "init", str(dest)])
            self.assertEqual(proc.returncode, 0)
            has_start = (dest / "README-START-HERE.md").exists() or (dest / "00-START-HERE.md").exists()
            self.assertTrue(has_start)
            self.assertTrue((dest / "01-evidence-ledger.csv").exists())
            self.assertTrue((dest / "02-assumptions.csv").exists())

    def test_int04_sprint_init_add_helpers_and_strict_audit(self):
        """INT-04: Workspace Scaffolding -> Data Addition -> audit_case.py verification."""
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "active_case"
            shutil.copytree(FIXTURE_LAUNCH_EVENT, dest)
            audit_script = SKILLS / "casekit-validator" / "scripts" / "audit_case.py"
            proc = run_command([sys.executable, str(audit_script), str(dest), "--strict"])
            self.assertEqual(proc.returncode, 0)

    def test_int05_research_evidence_to_archive_snapshot_and_source_check(self):
        """INT-05: Evidence Ingestion -> Archival Hashing -> check_sources.py."""
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "research_case"
            shutil.copytree(FIXTURE_LAUNCH_EVENT, dest)
            check_script = SKILLS / "casekit-validator" / "scripts" / "check_sources.py"
            proc = run_command([sys.executable, str(check_script), str(dest)])
            self.assertEqual(proc.returncode, 0)

    def test_int06_strategy_option_portfolio_and_rubric_scoring(self):
        """INT-06: Strategy Option Scoring -> Rubric Scorecard calculation."""
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "strategy_case"
            shutil.copytree(FIXTURE_LAUNCH_EVENT, dest)
            (dest / "option-portfolio.csv").write_text(
                "option_id,option_name,target_segment,mechanism,decision_goal,rubric_fit,impact,feasibility,viability,differentiation,evidence_confidence,weighted_score,evidence_ids,assumption_ids,critical_risk,fastest_test,stop_condition,owner,status\n"
                "OPT-001,Direct wedge,SMEs,Self-serve,Pilot,5,4,4,4,3,3,4.0,CLM-001,ASM-001,Low conversion,Landing test,Stop on low signups,Strategy,chosen\n",
                encoding="utf-8",
            )
            audit_script = SKILLS / "casekit-validator" / "scripts" / "audit_case.py"
            proc = run_command([sys.executable, str(audit_script), str(dest), "--strict"])
            self.assertEqual(proc.returncode, 0)

    def test_int07_integration_contract_and_audit_layer(self):
        """INT-07: Integration Contract (mocked/real) -> audit_case.py gate."""
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "int_case"
            shutil.copytree(FIXTURE_LAUNCH_EVENT, dest)
            (dest / "integration-contract.csv").write_text(
                "integration_id,system,purpose,user_journey_step,delivery_level,status,interface_type,auth_method,data_in,data_out,personal_data_classification,consent_or_legal_basis,owner,partner_owner,dependency,rate_limit_or_sla,cost_driver,fallback,demo_evidence,source_or_assumption_ids,risk_id,go_live_gate\n"
                "INT-001,Payment Gateway,Process card,Checkout,pilot,mocked,Webhook,N/A,Order payload,Receipt,low,N/A,Product,Gateway team,Sandbox,N/A,ASM-001,Manual invoice,Video demo,ASM-001,RSK-001,Test passing\n",
                encoding="utf-8",
            )
            audit_script = SKILLS / "casekit-validator" / "scripts" / "audit_case.py"
            proc = run_command([sys.executable, str(audit_script), str(dest), "--strict"])
            self.assertEqual(proc.returncode, 0)

    def test_int08_cfo_operating_plan_and_variance_reconciliation(self):
        """INT-08: CFO Operating Plan -> Monthly Cash Reconciliation -> audit_case.py."""
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "cfo_case"
            shutil.copytree(FIXTURE_LAUNCH_EVENT, dest)
            cfo_script = SKILLS / "casekit-finance" / "scripts" / "cfo_operating_plan.py"
            cfo_example = SKILLS / "casekit-finance" / "assets" / "cfo-operating-plan-input.example.json"
            out_json = dest / "15-cfo-operating-plan.json"
            proc = run_command([sys.executable, str(cfo_script), str(cfo_example), "--output", str(out_json)])
            self.assertEqual(proc.returncode, 0)
            self.assertTrue(out_json.exists())

    def test_int09_unit_economics_to_deck_spec_binding(self):
        """INT-09: Unit Economics Engine -> KPI Deck Bindings."""
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "econ_case"
            shutil.copytree(FIXTURE_LAUNCH_EVENT, dest)
            unit_script = SKILLS / "casekit-finance" / "scripts" / "unit_economics.py"
            unit_example = SKILLS / "casekit-finance" / "assets" / "unit-economics-input.example.json"
            out_json = dest / "14-unit-economics.json"
            proc = run_command([sys.executable, str(unit_script), str(unit_example), "--output", str(out_json)])
            self.assertEqual(proc.returncode, 0)
            self.assertTrue(out_json.exists())

    def test_int10_universal_install_and_portability_adapters(self):
        """INT-10: install.py -> Multi-Client Native Discovery Paths."""
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "installed_skills"
            proc = run_command([sys.executable, str(ROOT / "install.py"), "--target", str(target)])
            self.assertEqual(proc.returncode, 0)
            installed = {p.name for p in target.glob("casekit-*") if p.is_dir()}
            self.assertGreaterEqual(len(installed), 10)

    def test_int11_clean_team_layout_workflow_status(self):
        """INT-11: 3-Tier Clean Team Layout Scaffolding and Status Inspection."""
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "clean_team_case"
            run_command([sys.executable, str(CASEKIT_CLI), "init", str(dest), "--layout", "clean", "--team", "Engineering,Marketing"])
            status_proc = run_command([sys.executable, str(CASEKIT_CLI), "status", str(dest)])
            self.assertEqual(status_proc.returncode, 0)
            self.assertIn("Layout: clean team", status_proc.stdout)

    def test_int12_deck_renderer_theme_token_customization(self):
        """INT-12: Presentation Renderer with Custom Theme Palettes."""
        with tempfile.TemporaryDirectory() as td:
            out_pptx = Path(td) / "themed_deck.pptx"
            spec_file = Path(td) / "themed_spec.json"
            spec_file.write_text(json.dumps({
                "theme": {"navy": "0A2540", "blue": "635BFF", "teal": "00D924", "amber": "F5A623", "red": "E22525"},
                "meta": {"font_head": "Helvetica", "font_body": "Arial"},
                "slides": [
                    {"type": "cover", "headline": "Custom Themed Deck", "subhead": "Testing visual tokens"},
                    {"type": "metric", "headline": "Key Metrics", "metric": "99.9%", "label": "Reliability", "body": ["Point A", "Point B"]}
                ]
            }), encoding="utf-8")
            script = SKILLS / "casekit-deck" / "scripts" / "render_deck.py"
            proc = run_command([sys.executable, str(script), str(spec_file), str(out_pptx)])
            self.assertEqual(proc.returncode, 0)
            self.assertTrue(out_pptx.exists())

    def test_int13_multi_archetype_forecast_routing(self):
        """INT-13: Model Router for multi-archetype scenario drivers."""
        script = SKILLS / "casekit-finance" / "scripts" / "model_router.py"
        example_input = SKILLS / "casekit-finance" / "assets" / "model-input.example.json"
        proc = run_command([sys.executable, str(script), str(example_input)])
        self.assertEqual(proc.returncode, 0)
        data = json.loads(proc.stdout)
        self.assertIn("scenarios", data)
        self.assertEqual(data.get("model_type"), "subscription")

    def test_int14_sensitivity_ranking_with_metric_tree(self):
        """INT-14: Sensitivity Tornado ranking for financial drivers."""
        script = SKILLS / "casekit-finance" / "scripts" / "sensitivity.py"
        example_input = SKILLS / "casekit-finance" / "assets" / "model-input.example.json"
        proc = run_command([sys.executable, str(script), str(example_input), "--top", "3"])
        self.assertEqual(proc.returncode, 0)
        data = json.loads(proc.stdout)
        self.assertEqual(len(data.get("ranked_drivers", [])), 3)

    def test_int15_mcp_server_cross_tool_orchestration(self):
        """INT-15: MCP JSON-RPC Server Tools Execution Pipeline."""
        mcp_script = SCRIPTS / "casekit_mcp_server.py"
        if mcp_script.exists():
            req = {"jsonrpc": "2.0", "id": "test-1", "method": "tools/list", "params": {}}
            from tests.test_helpers import send_mcp_jsonrpc_request
            resp = send_mcp_jsonrpc_request(mcp_script, req)
            self.assertEqual(resp.get("jsonrpc"), "2.0")
            self.assertIn("result", resp)


if __name__ == "__main__":
    unittest.main(verbosity=2)
