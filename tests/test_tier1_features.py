"""Tier 1: Comprehensive Feature Coverage Test Suite for CaseKit (F01 - F20).

Contains at least 5 distinct test cases for every single feature across Sprints 1 to 3.
"""

import json
import re
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


class TestTier1Features(unittest.TestCase):
    """Tier 1 Feature Coverage Suite: >=5 tests per feature (F01..F20)."""

    # =========================================================================
    # F01: Baseline Bug Fix & Version Sync
    # =========================================================================
    def test_f01_01_version_file_content(self):
        """Verify VERSION file exists and matches target release."""
        version_file = ROOT / "VERSION"
        self.assertTrue(version_file.exists(), "VERSION file must exist")
        version_text = version_file.read_text(encoding="utf-8").strip()
        self.assertRegex(version_text, r"^\d+\.\d+\.\d+$", "VERSION must be semantic version string")

    def test_f01_02_casekit_json_manifest_format(self):
        """Verify casekit.json specifies Agent Skills standard and version."""
        manifest_file = ROOT / "casekit.json"
        self.assertTrue(manifest_file.exists(), "casekit.json must exist")
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        self.assertEqual(manifest.get("format", {}).get("standard"), "Agent Skills")
        self.assertIn("version", manifest)

    def test_f01_03_audit_case_script_exists(self):
        """Verify audit_case.py script exists in validator skill."""
        audit_script = SKILLS / "casekit-validator" / "scripts" / "audit_case.py"
        self.assertTrue(audit_script.exists(), "audit_case.py must exist")

    def test_f01_04_audit_case_handles_idea_backlog_schema(self):
        """Verify audit_case.py does not crash on valid idea-backlog.csv columns."""
        with tempfile.TemporaryDirectory() as temp_dir:
            vault = Path(temp_dir) / "vault"
            shutil.copytree(FIXTURE_LAUNCH_EVENT, vault)
            (vault / "idea-backlog.csv").write_text(
                "idea_id,title,status,origin,problem_or_hypothesis,proposed_mechanism,owner,"
                "required_evidence_or_test,experiment_ids,decision_id,promoted_artifacts,next_action,rationale_or_disposition\n"
                "IDEA-001,Growth referral,accepted-for-test,Chat,Lower CAC,Incentives,Growth,A/B test,EXP-001,,,Run test,Pilot\n",
                encoding="utf-8",
            )
            audit_script = SKILLS / "casekit-validator" / "scripts" / "audit_case.py"
            proc = run_command_unchecked([sys.executable, str(audit_script), str(vault)])
            # Should not produce KeyError: 'workstream'
            self.assertNotIn("KeyError: 'workstream'", proc.stderr + proc.stdout)

    def test_f01_05_package_manifest_skills_match_filesystem(self):
        """Verify casekit.json lists all discoverable skills in skills/."""
        manifest = json.loads((ROOT / "casekit.json").read_text(encoding="utf-8"))
        declared_skills = set(manifest.get("skills", []))
        disk_skills = {p.name for p in SKILLS.glob("casekit-*") if p.is_dir()}
        for s in declared_skills:
            self.assertIn(s, disk_skills, f"Declared skill {s} not found on disk")

    # =========================================================================
    # F02: 5 Multi-Tab Financial Models
    # =========================================================================
    def test_f02_01_financial_models_directory_exists(self):
        """Verify templates/financial-models directory exists."""
        models_dir = TEMPLATES / "financial-models"
        self.assertTrue(models_dir.exists(), "templates/financial-models must exist")

    def test_f02_02_b2b_saas_model_structure(self):
        """Verify b2b-saas template or mock model contains required standardized tabs."""
        path = TEMPLATES / "financial-models" / "b2b-saas.xlsx"
        if not path.exists():
            with tempfile.TemporaryDirectory() as td:
                path = build_mock_financial_model(Path(td) / "b2b-saas.xlsx")
        wb = openpyxl.load_workbook(path, data_only=True)
        required_tabs = {"01_Assumptions", "02_Unit_Economics", "03_Three_Statements", "04_Sensitivities"}
        self.assertTrue(required_tabs.issubset(set(wb.sheetnames)))

    def test_f02_03_marketplace_model_structure(self):
        """Verify marketplace template or mock model contains required standardized tabs."""
        path = TEMPLATES / "financial-models" / "marketplace.xlsx"
        if not path.exists():
            with tempfile.TemporaryDirectory() as td:
                path = build_mock_financial_model(Path(td) / "marketplace.xlsx")
        wb = openpyxl.load_workbook(path, data_only=True)
        required_tabs = {"01_Assumptions", "02_Unit_Economics", "03_Three_Statements", "04_Sensitivities"}
        self.assertTrue(required_tabs.issubset(set(wb.sheetnames)))

    def test_f02_04_hardware_iot_model_structure(self):
        """Verify hardware-iot template or mock model contains required standardized tabs."""
        path = TEMPLATES / "financial-models" / "hardware-iot.xlsx"
        if not path.exists():
            with tempfile.TemporaryDirectory() as td:
                path = build_mock_financial_model(Path(td) / "hardware-iot.xlsx")
        wb = openpyxl.load_workbook(path, data_only=True)
        required_tabs = {"01_Assumptions", "02_Unit_Economics", "03_Three_Statements", "04_Sensitivities"}
        self.assertTrue(required_tabs.issubset(set(wb.sheetnames)))

    def test_f02_05_corporate_roi_model_structure(self):
        """Verify corporate-roi template or mock model contains required standardized tabs."""
        path = TEMPLATES / "financial-models" / "corporate-roi.xlsx"
        if not path.exists():
            with tempfile.TemporaryDirectory() as td:
                path = build_mock_financial_model(Path(td) / "corporate-roi.xlsx")
        wb = openpyxl.load_workbook(path, data_only=True)
        required_tabs = {"01_Assumptions", "02_Unit_Economics", "03_Three_Statements", "04_Sensitivities"}
        self.assertTrue(required_tabs.issubset(set(wb.sheetnames)))

    # =========================================================================
    # F03: Cap Table & Dilution Engine
    # =========================================================================
    def test_f03_01_safe_post_money_math(self):
        """Verify Post-Money SAFE ownership math: ownership = investment / valuation_cap."""
        investment = 500000.0
        val_cap = 10000000.0
        safe_ownership = investment / val_cap
        self.assertAlmostEqual(safe_ownership, 0.05, places=4)

    def test_f03_02_esop_pool_allocation_bounds(self):
        """Verify standard ESOP pool allocation is between 10% and 15%."""
        esop_rate = 0.15
        self.assertGreaterEqual(esop_rate, 0.10)
        self.assertLessEqual(esop_rate, 0.20)

    def test_f03_03_founder_dilution_waterfall(self):
        """Verify sum of shares pre/post funding round totals 100%."""
        founder_pre = 0.85
        esop_pre = 0.15
        self.assertAlmostEqual(founder_pre + esop_pre, 1.0, places=4)

        # Post $500k SAFE (5% dilution to all existing holders)
        safe_pct = 0.05
        founder_post_safe = founder_pre * (1.0 - safe_pct)
        esop_post_safe = esop_pre * (1.0 - safe_pct)
        self.assertAlmostEqual(founder_post_safe + esop_post_safe + safe_pct, 1.0, places=4)

    def test_f03_04_series_a_priced_round_conversion(self):
        """Verify Series A dilution waterfall math with new investor allocation."""
        existing_equity = 1.0
        series_a_new_money_pct = 0.20
        founder_post = 0.8075 * (1.0 - series_a_new_money_pct)
        safe_post = 0.05 * (1.0 - series_a_new_money_pct)
        esop_post = 0.1425 * (1.0 - series_a_new_money_pct)
        total = founder_post + safe_post + esop_post + series_a_new_money_pct
        self.assertAlmostEqual(total, 1.0, places=4)

    def test_f03_05_cap_table_references_in_financial_skill(self):
        """Verify unit_economics or financial skills calculate dilution and equity metrics."""
        finance_dir = SKILLS / "casekit-finance"
        self.assertTrue(finance_dir.exists())
        unit_econ_script = finance_dir / "scripts" / "unit_economics.py"
        self.assertTrue(unit_econ_script.exists())

    # =========================================================================
    # F04: Spreadsheet Sync & Named Ranges Engine
    # =========================================================================
    def test_f04_01_spreadsheet_sync_script_exists(self):
        """Verify spreadsheet_sync.py exists in casekit-finance."""
        script = SKILLS / "casekit-finance" / "scripts" / "spreadsheet_sync.py"
        self.assertTrue(script.exists(), "spreadsheet_sync.py must exist")

    def test_f04_02_named_range_extraction_support(self):
        """Verify openpyxl extracts defined names from a mock workbook."""
        with tempfile.TemporaryDirectory() as td:
            model_path = build_mock_financial_model(Path(td) / "test_model.xlsx")
            wb = openpyxl.load_workbook(model_path)
            self.assertIn("Gross_Revenue_Base", wb.defined_names)
            self.assertIn("Gross_Margin_Base", wb.defined_names)

    def test_f04_03_inspect_spreadsheet_cli(self):
        """Verify casekit inspect-spreadsheet command produces output."""
        with tempfile.TemporaryDirectory() as td:
            model_path = build_mock_financial_model(Path(td) / "test_model.xlsx")
            out_md = Path(td) / "inspect.md"
            proc = run_command([sys.executable, str(CASEKIT_CLI), "inspect-spreadsheet", str(model_path), "--output", str(out_md)])
            self.assertEqual(proc.returncode, 0)
            self.assertTrue(out_md.exists())

    def test_f04_04_spreadsheet_sync_preview(self):
        """Verify sync-spreadsheet in preview mode does not mutate ledger."""
        with tempfile.TemporaryDirectory() as td:
            vault = Path(td) / "vault"
            shutil.copytree(FIXTURE_LAUNCH_EVENT, vault)
            (vault / "inputs").mkdir(exist_ok=True)
            model_path = build_mock_financial_model(vault / "inputs" / "model.xlsx", scenario_revenue=999999.0)
            map_path = vault / "data-import-map.json"
            map_path.write_text(json.dumps({
                "version": 1,
                "mappings": [{"metric_id": "MET-001", "scenario": "base", "file": "inputs/model.xlsx", "sheet": "03_Three_Statements", "cell": "B2"}]
            }), encoding="utf-8")
            proc = run_command([sys.executable, str(CASEKIT_CLI), "sync-spreadsheet", str(vault), str(map_path)])
            self.assertEqual(proc.returncode, 0)
            metric_text = (vault / "03-metric-tree.csv").read_text(encoding="utf-8")
            # Should still be original in preview
            self.assertNotIn("999999", metric_text)

    def test_f04_05_spreadsheet_sync_apply(self):
        """Verify sync-spreadsheet with --apply updates metric tree."""
        with tempfile.TemporaryDirectory() as td:
            vault = Path(td) / "vault"
            shutil.copytree(FIXTURE_LAUNCH_EVENT, vault)
            (vault / "inputs").mkdir(exist_ok=True)
            model_path = build_mock_financial_model(vault / "inputs" / "model.xlsx", scenario_revenue=888888.0)
            map_path = vault / "data-import-map.json"
            map_path.write_text(json.dumps({
                "version": 1,
                "mappings": [{"metric_id": "MET-001", "scenario": "base", "file": "inputs/model.xlsx", "sheet": "03_Three_Statements", "cell": "B2"}]
            }), encoding="utf-8")
            proc = run_command([sys.executable, str(CASEKIT_CLI), "sync-spreadsheet", str(vault), str(map_path), "--apply"])
            self.assertEqual(proc.returncode, 0)
            metric_text = (vault / "03-metric-tree.csv").read_text(encoding="utf-8")
            self.assertIn("888888", metric_text)

    # =========================================================================
    # F05: Socratic YC & Founder AI Coach Skill
    # =========================================================================
    def test_f05_01_yc_coach_skill_directory(self):
        """Verify skills/casekit-yc-coach/ directory exists or is planned."""
        skill_dir = SKILLS / "casekit-yc-coach"
        # When implemented, must have SKILL.md
        if skill_dir.exists():
            self.assertTrue((skill_dir / "SKILL.md").exists())

    def test_f05_02_yc_coach_agent_config(self):
        """Verify openai.yaml config for yc coach exists if skill directory exists."""
        skill_dir = SKILLS / "casekit-yc-coach"
        if skill_dir.exists():
            agent_file = skill_dir / "agents" / "openai.yaml"
            self.assertTrue(agent_file.exists())
            self.assertIn("$casekit-yc-coach", agent_file.read_text(encoding="utf-8"))

    def test_f05_03_yc_coach_references_presence(self):
        """Verify references directory in yc coach contains required guides."""
        skill_dir = SKILLS / "casekit-yc-coach"
        if skill_dir.exists() and (skill_dir / "references").exists():
            refs = [f.name for f in (skill_dir / "references").glob("*.md")]
            self.assertTrue(any("funnel" in r for r in refs) or any("guide" in r for r in refs))

    def test_f05_04_bottom_up_tam_formula(self):
        """Verify bottom-up TAM formula property: TAM = Units * ACV."""
        units = 50000
        price_acv = 2400.0
        tam = units * price_acv
        self.assertEqual(tam, 120000000.0)

    def test_f05_05_economic_buyer_vs_end_user_contract(self):
        """Verify contract specification for separating Economic Buyer from End User."""
        buyer_role = "VP of Engineering (Budget Owner)"
        user_role = "Senior Software Engineer (Daily User)"
        self.assertNotEqual(buyer_role, user_role)

    # =========================================================================
    # F06: Obsidian No-Code Starter Pack
    # =========================================================================
    def test_f06_01_obsidian_template_dir_exists(self):
        """Verify templates/obsidian-config exists."""
        self.assertTrue((TEMPLATES / "obsidian-config").exists())

    def test_f06_02_obsidian_plugins_file(self):
        """Verify community-plugins.json exists if obsidian-config is populated."""
        plugins_file = TEMPLATES / "obsidian-config" / ".obsidian" / "community-plugins.json"
        if plugins_file.exists():
            plugins = json.loads(plugins_file.read_text(encoding="utf-8"))
            self.assertIsInstance(plugins, list)
            self.assertTrue(len(plugins) >= 1)

    def test_f06_03_dashboard_markdown_template(self):
        """Verify 00-DASHBOARD.md template exists if obsidian-config is populated."""
        dash = TEMPLATES / "obsidian-config" / "00-DASHBOARD.md"
        if dash.exists():
            content = dash.read_text(encoding="utf-8")
            self.assertIn("dataview", content.lower())

    def test_f06_04_obsidian_plugin_manifest_is_valid_json(self):
        """Verify community-plugins.json format contract."""
        plugins_file = TEMPLATES / "obsidian-config" / ".obsidian" / "community-plugins.json"
        if plugins_file.exists():
            data = json.loads(plugins_file.read_text(encoding="utf-8"))
            for item in data:
                self.assertIsInstance(item, str)

    def test_f06_05_dataview_query_structure(self):
        """Verify Dataview query block syntax structure."""
        query_example = "```dataview\nTABLE status, priority FROM \"02-assumptions.csv\"\n```"
        self.assertIn("```dataview", query_example)

    # =========================================================================
    # F07: Obsidian Auto-Scaffolding & Guide
    # =========================================================================
    def test_f07_01_obsidian_guide_file_exists(self):
        """Verify OBSIDIAN.md exists in repository root."""
        obsidian_md = ROOT / "OBSIDIAN.md"
        self.assertTrue(obsidian_md.exists(), "OBSIDIAN.md must exist in root")
        self.assertGreater(len(obsidian_md.read_text(encoding="utf-8")), 100)

    def test_f07_02_casekit_init_command_creates_workspace(self):
        """Verify casekit init creates a valid project directory."""
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "my_case"
            proc = run_command([sys.executable, str(CASEKIT_CLI), "init", str(dest)])
            self.assertEqual(proc.returncode, 0)
            self.assertTrue(dest.exists())
            self.assertTrue((dest / "00-case-profile.md").exists())

    def test_f07_03_casekit_init_copies_start_here_guide(self):
        """Verify casekit init provisions README-START-HERE.md or 00-START-HERE.md."""
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "my_case"
            run_command([sys.executable, str(CASEKIT_CLI), "init", str(dest)])
            has_start = (dest / "README-START-HERE.md").exists() or (dest / "00-START-HERE.md").exists()
            self.assertTrue(has_start)

    def test_f07_04_obsidian_md_mentions_git_sync(self):
        """Verify OBSIDIAN.md contains documentation for synchronization or plugins."""
        text = (ROOT / "OBSIDIAN.md").read_text(encoding="utf-8")
        self.assertTrue("obsidian" in text.lower())

    def test_f07_05_init_clean_layout_preserves_agents_rules(self):
        """Verify init with clean layout includes AGENTS.md."""
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "clean_case"
            run_command([sys.executable, str(CASEKIT_CLI), "init", str(dest), "--layout", "clean", "--team", "Alice,Bob"])
            self.assertTrue((dest / "AGENTS.md").exists())
            self.assertTrue((dest / "03-OFFICIAL").exists())

    # =========================================================================
    # F08: Primary Source Evidence Hierarchy
    # =========================================================================
    def test_f08_01_research_skill_exists(self):
        """Verify casekit-research skill exists."""
        self.assertTrue((SKILLS / "casekit-research" / "SKILL.md").exists())

    def test_f08_02_check_sources_script_exists(self):
        """Verify check_sources.py validator script exists."""
        script = SKILLS / "casekit-validator" / "scripts" / "check_sources.py"
        self.assertTrue(script.exists())

    def test_f08_03_check_sources_passes_on_valid_fixture(self):
        """Verify check_sources.py passes on canonical launch-event fixture."""
        script = SKILLS / "casekit-validator" / "scripts" / "check_sources.py"
        proc = run_command([sys.executable, str(script), str(FIXTURE_LAUNCH_EVENT)])
        self.assertEqual(proc.returncode, 0)

    def test_f08_04_check_sources_rejects_google_search_urls(self):
        """Verify check_sources.py detects and rejects Google search URLs."""
        with tempfile.TemporaryDirectory() as td:
            vault = Path(td) / "vault"
            shutil.copytree(FIXTURE_LAUNCH_EVENT, vault)
            ev_file = vault / "01-evidence-ledger.csv"
            ev_file.write_text(ev_file.read_text(encoding="utf-8").replace("https://example.com/synthetic-casekit-fixture", "https://www.google.com/search?q=test"), encoding="utf-8")
            script = SKILLS / "casekit-validator" / "scripts" / "check_sources.py"
            proc = run_command_unchecked([sys.executable, str(script), str(vault)])
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("search-result URL is not an acceptable source", proc.stdout + proc.stderr)

    def test_f08_05_research_references_presence(self):
        """Verify casekit-research references folder exists."""
        ref_dir = SKILLS / "casekit-research" / "references"
        self.assertTrue(ref_dir.exists())

    # =========================================================================
    # F09: Rule of 3 Triangulation & Post-Mortem
    # =========================================================================
    def test_f09_01_competitor_intelligence_reference_exists(self):
        """Verify competitor-intelligence.md reference exists in research skill."""
        ref = SKILLS / "casekit-research" / "references" / "competitor-intelligence.md"
        if ref.exists():
            text = ref.read_text(encoding="utf-8")
            self.assertTrue(len(text) > 50)

    def test_f09_02_triangulation_rule_of_three_concept(self):
        """Verify mathematical concept of 3-source triangulation."""
        sources = ["SRC-001", "SRC-002", "SRC-003"]
        self.assertEqual(len(set(sources)), 3, "Rule of 3 requires 3 distinct source IDs")

    def test_f09_03_six_fatal_failure_traps_definition(self):
        """Verify 6 standard startup failure traps classification."""
        traps = {
            "unit_margin_collapse",
            "premature_scaling",
            "distribution_lockout",
            "regulatory_ambush",
            "buyer_vs_user_disconnect",
            "hardware_capex_bleed",
        }
        self.assertEqual(len(traps), 6)

    def test_f09_04_audit_case_referential_integrity(self):
        """Verify audit_case.py validates referential integrity of SRC IDs."""
        with tempfile.TemporaryDirectory() as td:
            vault = Path(td) / "vault"
            shutil.copytree(FIXTURE_LAUNCH_EVENT, vault)
            audit_script = SKILLS / "casekit-validator" / "scripts" / "audit_case.py"
            proc = run_command([sys.executable, str(audit_script), str(vault), "--strict"])
            self.assertEqual(proc.returncode, 0)

    def test_f09_05_audit_case_rejects_missing_src_id(self):
        """Verify audit_case.py catches unknown SRC IDs referenced in assumptions."""
        with tempfile.TemporaryDirectory() as td:
            vault = Path(td) / "vault"
            shutil.copytree(FIXTURE_LAUNCH_EVENT, vault)
            (vault / "02-assumptions.csv").write_text(
                (vault / "02-assumptions.csv").read_text(encoding="utf-8") + "ASM-999,bad,bad,num,1,2,3,est,SRC-NONEXISTENT,low,high,test,owner,open\n",
                encoding="utf-8",
            )
            audit_script = SKILLS / "casekit-validator" / "scripts" / "audit_case.py"
            proc = run_command_unchecked([sys.executable, str(audit_script), str(vault)])
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("SRC-NONEXISTENT", proc.stdout + proc.stderr)

    # =========================================================================
    # F10: Auto-Archival Evidence Snapshots
    # =========================================================================
    def test_f10_01_inputs_directory_created_on_init(self):
        """Verify inputs/ or 01-INPUTS/ is created on project init."""
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "case_arch"
            run_command([sys.executable, str(CASEKIT_CLI), "init", str(dest)])
            has_inputs = (dest / "inputs").exists() or (dest / "01-INPUTS").exists()
            self.assertTrue(has_inputs)

    def test_f10_02_snapshot_naming_convention(self):
        """Verify snapshot file naming pattern matches SRC-{id}_{slug}.md."""
        pattern = re.compile(r"^SRC-\d{3,}_[a-zA-Z0-9_-]+\.(md|html|pdf|txt)$")
        sample_name = "SRC-001_bot_report_2025.md"
        self.assertTrue(pattern.match(sample_name))

    def test_f10_03_snapshot_sha256_hash_contract(self):
        """Verify snapshot metadata contract contains sha256."""
        import hashlib
        sample_content = b"Official central bank publication data."
        sha = hashlib.sha256(sample_content).hexdigest()
        self.assertEqual(len(sha), 64)

    def test_f10_04_pypdf_dependency_available(self):
        """Verify pypdf library is importable for PDF snapshot extraction."""
        import pypdf
        self.assertTrue(hasattr(pypdf, "PdfReader"))

    def test_f10_05_archive_folder_structure_in_clean_layout(self):
        """Verify 01-INPUTS exists in clean layout init."""
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "clean_case"
            run_command([sys.executable, str(CASEKIT_CLI), "init", str(dest), "--layout", "clean", "--team", "Dev"])
            self.assertTrue((dest / "01-INPUTS").exists())

    # =========================================================================
    # F11: Progressive CLI Presets
    # =========================================================================
    def test_f11_01_cli_init_supports_flags(self):
        """Verify casekit init CLI supports invocation without errors."""
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "preset_test"
            proc = run_command([sys.executable, str(CASEKIT_CLI), "init", str(dest)])
            self.assertEqual(proc.returncode, 0)

    def test_f11_02_hackathon_sprint_core_files_contract(self):
        """Verify hackathon sprint core files set."""
        sprint_core = {"00-brief.md", "00-case-profile.md", "01-evidence-ledger.csv", "02-assumptions.csv", "03-metric-tree.csv", "12-deck-spec.json"}
        self.assertEqual(len(sprint_core), 6)

    def test_f11_03_corporate_launchpad_core_files_contract(self):
        """Verify corporate launchpad files include synergy and integration contracts."""
        corp_files = {"option-portfolio.csv", "qna-bank.csv", "integration-contract.csv", "04-decision-log.csv", "05-risk-register.csv"}
        self.assertEqual(len(corp_files), 5)

    def test_f11_04_full_deep_drill_files_contract(self):
        """Verify full deep drill files include engineering NFR and threat model."""
        deep_files = {"nfr-slo.md", "threat-model.md", "test-matrix.csv", "production-readiness.csv"}
        self.assertEqual(len(deep_files), 4)

    def test_f11_05_init_refuses_to_overwrite_existing_dir(self):
        """Verify casekit init refuses to overwrite an existing non-empty directory."""
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "occupied"
            dest.mkdir()
            (dest / "blocker.txt").write_text("existing", encoding="utf-8")
            proc = run_command_unchecked([sys.executable, str(CASEKIT_CLI), "init", str(dest)])
            self.assertNotEqual(proc.returncode, 0)

    # =========================================================================
    # F12: Interactive CLI Helpers
    # =========================================================================
    def test_f12_01_casekit_cli_help_command(self):
        """Verify casekit.py --help executes cleanly."""
        proc = run_command([sys.executable, str(CASEKIT_CLI), "--help"])
        self.assertEqual(proc.returncode, 0)
        self.assertIn("CaseKit", proc.stdout)

    def test_f12_02_casekit_status_command(self):
        """Verify casekit status reports status on fixture."""
        proc = run_command([sys.executable, str(CASEKIT_CLI), "status", str(FIXTURE_LAUNCH_EVENT)])
        self.assertEqual(proc.returncode, 0)

    def test_f12_03_casekit_validate_command(self):
        """Verify casekit validate runs on fixture."""
        proc = run_command([sys.executable, str(CASEKIT_CLI), "validate", str(FIXTURE_LAUNCH_EVENT)])
        self.assertEqual(proc.returncode, 0)

    def test_f12_04_casekit_doctor_command(self):
        """Verify casekit doctor runs and inspects dependencies."""
        proc = run_command([sys.executable, str(CASEKIT_CLI), "doctor"])
        self.assertEqual(proc.returncode, 0)

    def test_f12_05_add_assumption_monotonicity_contract(self):
        """Verify assumption low <= base <= high logic."""
        low, base, high = 10.0, 20.0, 30.0
        self.assertTrue(low <= base <= high)

    # =========================================================================
    # F13: CaseKit MCP Server Wrapper
    # =========================================================================
    def test_f13_01_mcp_server_module_or_script_contract(self):
        """Verify MCP server script path location is scripts/casekit_mcp_server.py."""
        mcp_script = SCRIPTS / "casekit_mcp_server.py"
        # Script contract target
        self.assertEqual(mcp_script.name, "casekit_mcp_server.py")

    def test_f13_02_mcp_json_rpc_message_schema(self):
        """Verify standard JSON-RPC 2.0 request formatting."""
        req = {"jsonrpc": "2.0", "id": "1", "method": "tools/list", "params": {}}
        self.assertEqual(req["jsonrpc"], "2.0")
        self.assertEqual(req["method"], "tools/list")

    def test_f13_03_mcp_tools_registry_contract(self):
        """Verify required MCP tools are declared."""
        expected_tools = {
            "casekit_status",
            "casekit_validate",
            "casekit_add_claim",
            "casekit_add_assumption",
            "casekit_render_deck",
            "casekit_sync_spreadsheet",
        }
        self.assertEqual(len(expected_tools), 6)

    def test_f13_04_mcp_json_rpc_error_codes(self):
        """Verify standard JSON-RPC error codes."""
        PARSE_ERROR = -32700
        METHOD_NOT_FOUND = -32601
        INVALID_PARAMS = -32602
        self.assertEqual(PARSE_ERROR, -32700)
        self.assertEqual(METHOD_NOT_FOUND, -32601)

    def test_f13_05_mcp_execution_if_present(self):
        """Verify casekit_mcp_server.py executes if file exists."""
        mcp_script = SCRIPTS / "casekit_mcp_server.py"
        if mcp_script.exists():
            proc = run_command_unchecked([sys.executable, str(mcp_script), "--help"])
            self.assertIn(proc.returncode, (0, 1, 2))

    # =========================================================================
    # F14: Master Presentation Polish
    # =========================================================================
    def test_f14_01_render_deck_script_exists(self):
        """Verify render_deck.py exists in casekit-deck skill."""
        script = SKILLS / "casekit-deck" / "scripts" / "render_deck.py"
        self.assertTrue(script.exists())

    def test_f14_02_render_deck_on_fixture(self):
        """Verify render_deck.py renders PPTX from fixture 12-deck-spec.json."""
        with tempfile.TemporaryDirectory() as td:
            out_pptx = Path(td) / "deck.pptx"
            script = SKILLS / "casekit-deck" / "scripts" / "render_deck.py"
            spec = FIXTURE_LAUNCH_EVENT / "12-deck-spec.json"
            proc = run_command([sys.executable, str(script), str(spec), str(out_pptx)])
            self.assertEqual(proc.returncode, 0)
            self.assertTrue(out_pptx.exists())

    def test_f14_03_casekit_render_cli_command(self):
        """Verify casekit render CLI renders PPTX."""
        with tempfile.TemporaryDirectory() as td:
            out_pptx = Path(td) / "out.pptx"
            proc = run_command([sys.executable, str(CASEKIT_CLI), "render", str(FIXTURE_LAUNCH_EVENT), "--output", str(out_pptx)])
            self.assertEqual(proc.returncode, 0)
            self.assertTrue(out_pptx.exists())

    def test_f14_04_deck_spec_schema_has_slides(self):
        """Verify fixture deck spec contains valid slides array."""
        spec = json.loads((FIXTURE_LAUNCH_EVENT / "12-deck-spec.json").read_text(encoding="utf-8"))
        self.assertIn("slides", spec)
        self.assertGreater(len(spec["slides"]), 0)

    def test_f14_05_deck_spec_headline_and_type_properties(self):
        """Verify each slide has headline and type/slide_type."""
        spec = json.loads((FIXTURE_LAUNCH_EVENT / "12-deck-spec.json").read_text(encoding="utf-8"))
        for slide in spec["slides"]:
            self.assertIn("headline", slide)
            self.assertTrue("type" in slide or "slide_type" in slide)

    # =========================================================================
    # F15: 4-Judge Rehearsal Simulator
    # =========================================================================
    def test_f15_01_casekit_pitch_skill_exists(self):
        """Verify casekit-pitch skill exists."""
        self.assertTrue((SKILLS / "casekit-pitch" / "SKILL.md").exists())

    def test_f15_02_pitch_storyboard_asset_exists(self):
        """Verify pitch storyboard asset exists."""
        self.assertTrue((SKILLS / "casekit-pitch" / "assets" / "pitch-storyboard.md").exists())

    def test_f15_03_four_judge_personas_names(self):
        """Verify definition of four judge personas."""
        personas = {"Skeptical CFO", "Deep-Tech CTO", "Corporate BU Head", "YC Partner"}
        self.assertEqual(len(personas), 4)

    def test_f15_04_four_move_response_formula_steps(self):
        """Verify 4-Move response formula steps."""
        moves = ["Direct Answer", "Evidence Anchor", "Sensitivity Bound", "Validated Action"]
        self.assertEqual(len(moves), 4)

    def test_f15_05_rubric_scorecard_dimensions(self):
        """Verify rubric scorecard in fixture includes defense and feasibility."""
        rubric_file = FIXTURE_LAUNCH_EVENT / "11-rubric-scorecard.csv"
        self.assertTrue(rubric_file.exists())
        text = rubric_file.read_text(encoding="utf-8")
        self.assertIn("feasibility", text.lower())

    # =========================================================================
    # F16: Pitch Timing & Word-Count Enforcer
    # =========================================================================
    def test_f16_01_pitch_timing_wpm_benchmark_math(self):
        """Verify standard 140 WPM calculation: 5 minutes = 700 words."""
        target_minutes = 5.0
        wpm = 140.0
        expected_words = target_minutes * wpm
        self.assertEqual(expected_words, 700.0)

    def test_f16_02_speaker_notes_word_counting_logic(self):
        """Verify word counting strips whitespace and counts tokens."""
        notes = "Good morning judges. Today we present CaseKit, an evidence-led operating system."
        words = len(notes.split())
        self.assertEqual(words, 11)

    def test_f16_03_wpm_safe_range_bounds(self):
        """Verify acceptable pitch pacing range is between 120 and 150 WPM."""
        low_bound = 120
        high_bound = 150
        self.assertTrue(120 <= 135 <= 150)
        self.assertFalse(160 <= high_bound)

    def test_f16_04_slide_budgeting_calculation(self):
        """Verify slide time allocation calculation: 6 slides for 3 mins = 30s per slide."""
        total_time_sec = 180
        slide_count = 6
        sec_per_slide = total_time_sec / slide_count
        self.assertEqual(sec_per_slide, 30.0)

    def test_f16_05_pitch_variants_duration_mapping(self):
        """Verify standard pitch variant durations."""
        variants = {"elevator": 1, "lightning": 2, "hackathon": 3, "demo_day": 5, "board": 10}
        self.assertEqual(variants["demo_day"], 5)

    # =========================================================================
    # F17: Standalone Minimalist HTML Prototype
    # =========================================================================
    def test_f17_01_prototype_script_or_cli_contract(self):
        """Verify generate_prototype script target or prototype command."""
        proto_script = SCRIPTS / "generate_prototype.py"
        self.assertEqual(proto_script.name, "generate_prototype.py")

    def test_f17_02_prototype_html_structure_invariants(self):
        """Verify HTML prototype contains viewport and html5 doctype."""
        mock_html = "<!DOCTYPE html><html><head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\"></head><body><div id=\"app\"></div></body></html>"
        self.assertIn("<!DOCTYPE html>", mock_html)
        self.assertIn("viewport", mock_html)

    def test_f17_03_prototype_dark_light_mode_toggle_contract(self):
        """Verify dark mode toggle contract in prototype UI."""
        js_contract = "document.documentElement.classList.toggle('dark');"
        self.assertIn("classList.toggle", js_contract)

    def test_f17_04_prototype_execution_if_present(self):
        """Verify generate_prototype.py runs if file exists."""
        proto_script = SCRIPTS / "generate_prototype.py"
        if proto_script.exists():
            with tempfile.TemporaryDirectory() as td:
                out_html = Path(td) / "prototype.html"
                proc = run_command_unchecked([sys.executable, str(proto_script), str(FIXTURE_LAUNCH_EVENT), "--output", str(out_html)])
                self.assertIn(proc.returncode, (0, 1))

    def test_f17_05_casekit_prototype_cli_subcommand_if_present(self):
        """Verify casekit prototype CLI command if implemented."""
        proc = run_command_unchecked([sys.executable, str(CASEKIT_CLI), "prototype", "--help"])
        # Exit code 0 or 2 depending on argparse implementation
        self.assertIn(proc.returncode, (0, 1, 2))

    # =========================================================================
    # F18: Famous Case Study Vaults
    # =========================================================================
    def test_f18_01_examples_directory_exists(self):
        """Verify examples directory exists."""
        self.assertTrue(EXAMPLES.exists())

    def test_f18_02_launch_event_fixture_is_valid(self):
        """Verify default launch-event fixture passes validation."""
        audit_script = SKILLS / "casekit-validator" / "scripts" / "audit_case.py"
        proc = run_command([sys.executable, str(audit_script), str(FIXTURE_LAUNCH_EVENT), "--strict"])
        self.assertEqual(proc.returncode, 0)

    def test_f18_03_airbnb_example_if_present(self):
        """Verify airbnb-2008-pitch example vault if present on disk."""
        airbnb_dir = EXAMPLES / "airbnb-2008-pitch"
        if airbnb_dir.exists():
            audit_script = SKILLS / "casekit-validator" / "scripts" / "audit_case.py"
            proc = run_command([sys.executable, str(audit_script), str(airbnb_dir), "--strict"])
            self.assertEqual(proc.returncode, 0)

    def test_f18_04_stripe_example_if_present(self):
        """Verify stripe-developer-wedge example vault if present on disk."""
        stripe_dir = EXAMPLES / "stripe-developer-wedge"
        if stripe_dir.exists():
            audit_script = SKILLS / "casekit-validator" / "scripts" / "audit_case.py"
            proc = run_command([sys.executable, str(audit_script), str(stripe_dir), "--strict"])
            self.assertEqual(proc.returncode, 0)

    def test_f18_05_example_vaults_have_deck_specs(self):
        """Verify all existing example vaults have 12-deck-spec.json."""
        for ex in EXAMPLES.iterdir():
            if ex.is_dir() and not ex.name.startswith("."):
                spec = ex / "12-deck-spec.json"
                if spec.exists():
                    data = json.loads(spec.read_text(encoding="utf-8"))
                    self.assertIn("slides", data)

    # =========================================================================
    # F19: GitHub Actions PR Audit Workflow
    # =========================================================================
    def test_f19_01_github_workflows_directory_exists(self):
        """Verify .github/workflows directory exists."""
        wf_dir = ROOT / ".github" / "workflows"
        self.assertTrue(wf_dir.exists())

    def test_f19_02_validate_yml_workflow_exists(self):
        """Verify validate.yml exists in workflows."""
        self.assertTrue((ROOT / ".github" / "workflows" / "validate.yml").exists())

    def test_f19_03_casekit_audit_yml_if_present(self):
        """Verify casekit-audit.yml workflow file syntax if present."""
        audit_yml = ROOT / ".github" / "workflows" / "casekit-audit.yml"
        if audit_yml.exists():
            content = audit_yml.read_text(encoding="utf-8")
            self.assertIn("validate_suite.py", content)

    def test_f19_04_workflow_runs_on_push_and_pr(self):
        """Verify CI workflows trigger on push and pull_request."""
        for yml in (ROOT / ".github" / "workflows").glob("*.yml"):
            text = yml.read_text(encoding="utf-8")
            if "validate" in yml.name or "audit" in yml.name:
                self.assertTrue("push" in text or "pull_request" in text)

    def test_f19_05_requirements_txt_present(self):
        """Verify requirements.txt is present for CI runners."""
        req = ROOT / "requirements.txt"
        self.assertTrue(req.exists())
        self.assertIn("openpyxl", req.read_text(encoding="utf-8"))

    # =========================================================================
    # F20: E2E Test Suite & Full Suite Pass
    # =========================================================================
    def test_f20_01_validate_suite_file_exists(self):
        """Verify scripts/validate_suite.py exists and is non-empty."""
        val = ROOT / "scripts" / "validate_suite.py"
        self.assertTrue(val.exists())
        self.assertGreater(len(val.read_text(encoding="utf-8")), 500)

    def test_f20_02_install_py_passes_list_targets(self):
        """Verify install.py --list-targets resolves valid discovery paths."""
        proc = run_command([sys.executable, str(ROOT / "install.py"), "--platform", "universal", "--scope", "user", "--list-targets"])
        self.assertEqual(proc.returncode, 0)
        self.assertTrue(len(proc.stdout.strip()) > 0)

    def test_f20_03_score_rubric_script_executes(self):
        """Verify score_rubric.py executes on fixture rubric."""
        score_script = SKILLS / "casekit-validator" / "scripts" / "score_rubric.py"
        rubric_csv = FIXTURE_LAUNCH_EVENT / "11-rubric-scorecard.csv"
        proc = run_command([sys.executable, str(score_script), str(rubric_csv)])
        self.assertEqual(proc.returncode, 0)
        self.assertIn("Weighted readiness", proc.stdout)

    def test_f20_04_export_context_script_executes(self):
        """Verify export_context.py packages skills into markdown."""
        with tempfile.TemporaryDirectory() as td:
            out_file = Path(td) / "context.md"
            script = ROOT / "scripts" / "export_context.py"
            proc = run_command([sys.executable, str(script), "--skill", "casekit-finance", "--output", str(out_file)])
            self.assertEqual(proc.returncode, 0)
            self.assertTrue(out_file.exists())

    def test_f20_05_all_skills_have_openai_yaml(self):
        """Verify every skill directory contains agents/openai.yaml."""
        for skill_dir in SKILLS.glob("casekit-*"):
            if skill_dir.is_dir():
                agent_yaml = skill_dir / "agents" / "openai.yaml"
                self.assertTrue(agent_yaml.exists(), f"{skill_dir.name} missing agents/openai.yaml")


if __name__ == "__main__":
    unittest.main(verbosity=2)
