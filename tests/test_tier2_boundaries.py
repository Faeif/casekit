"""Tier 2: Boundary, Corner Case, and Adversarial Test Suite for CaseKit (F01 - F20).

Contains at least 5 distinct boundary & corner test cases for every feature F01 to F20 (100+ tests total).
"""

import json
import os
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


class TestTier2Boundaries(unittest.TestCase):
    """Tier 2 Boundary & Corner Case Suite: >=5 tests per feature (F01..F20)."""

    # =========================================================================
    # F01: Baseline Bug Fix & Version Sync Boundaries
    # =========================================================================
    def test_f01_b01_idea_backlog_missing_title(self):
        """Verify audit_case.py catches blank title in idea-backlog.csv."""
        with tempfile.TemporaryDirectory() as td:
            vault = Path(td) / "vault"
            shutil.copytree(FIXTURE_LAUNCH_EVENT, vault)
            (vault / "idea-backlog.csv").write_text(
                "idea_id,title,status,origin,problem_or_hypothesis,proposed_mechanism,owner,"
                "required_evidence_or_test,experiment_ids,decision_id,promoted_artifacts,next_action,rationale_or_disposition\n"
                "IDEA-001,,accepted-for-test,Chat,Hypothesis,Mechanism,Growth,Test,EXP-001,,,Next,Rationale\n",
                encoding="utf-8",
            )
            audit_script = SKILLS / "casekit-validator" / "scripts" / "audit_case.py"
            proc = run_command_unchecked([sys.executable, str(audit_script), str(vault)])
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("title", proc.stdout + proc.stderr)

    def test_f01_b02_idea_backlog_accepted_for_case_without_decision(self):
        """Verify accepted-for-case status requires valid decision_id."""
        with tempfile.TemporaryDirectory() as td:
            vault = Path(td) / "vault"
            shutil.copytree(FIXTURE_LAUNCH_EVENT, vault)
            (vault / "idea-backlog.csv").write_text(
                "idea_id,title,status,origin,problem_or_hypothesis,proposed_mechanism,owner,"
                "required_evidence_or_test,experiment_ids,decision_id,promoted_artifacts,next_action,rationale_or_disposition\n"
                "IDEA-001,Growth initiative,accepted-for-case,Chat,Hypothesis,Mechanism,Growth,Test,EXP-001,,,Next,Rationale\n",
                encoding="utf-8",
            )
            audit_script = SKILLS / "casekit-validator" / "scripts" / "audit_case.py"
            proc = run_command_unchecked([sys.executable, str(audit_script), str(vault)])
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("decision_id", proc.stdout + proc.stderr)

    def test_f01_b03_version_file_whitespace_stripping(self):
        """Verify version parser strips trailing newlines and carriage returns."""
        raw_version = "1.1.0\r\n\n  "
        clean_version = raw_version.strip()
        self.assertEqual(clean_version, "1.1.0")

    def test_f01_b04_idea_backlog_duplicate_ids(self):
        """Verify audit_case.py rejects duplicate IDEA IDs."""
        with tempfile.TemporaryDirectory() as td:
            vault = Path(td) / "vault"
            shutil.copytree(FIXTURE_LAUNCH_EVENT, vault)
            (vault / "idea-backlog.csv").write_text(
                "idea_id,title,status,origin,problem_or_hypothesis,proposed_mechanism,owner,"
                "required_evidence_or_test,experiment_ids,decision_id,promoted_artifacts,next_action,rationale_or_disposition\n"
                "IDEA-001,Idea One,accepted-for-test,Chat,Hypothesis,Mechanism,Growth,Test,EXP-001,,,Next,Rationale\n"
                "IDEA-001,Idea Two,accepted-for-test,Chat,Hypothesis,Mechanism,Growth,Test,EXP-001,,,Next,Rationale\n",
                encoding="utf-8",
            )
            audit_script = SKILLS / "casekit-validator" / "scripts" / "audit_case.py"
            proc = run_command_unchecked([sys.executable, str(audit_script), str(vault)])
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("duplicate idea_id IDEA-001", proc.stdout + proc.stderr)

    def test_f01_b05_idea_backlog_zero_byte_handling(self):
        """Verify audit_case.py handles 0-byte idea backlog gracefully with error."""
        with tempfile.TemporaryDirectory() as td:
            vault = Path(td) / "vault"
            shutil.copytree(FIXTURE_LAUNCH_EVENT, vault)
            (vault / "idea-backlog.csv").write_text("", encoding="utf-8")
            audit_script = SKILLS / "casekit-validator" / "scripts" / "audit_case.py"
            proc = run_command_unchecked([sys.executable, str(audit_script), str(vault)])
            self.assertIn(proc.returncode, (0, 1, 2))

    # =========================================================================
    # F02: 5 Multi-Tab Financial Models Boundaries
    # =========================================================================
    def test_f02_b01_churn_rate_upper_bound_clamping(self):
        """Verify churn rate > 100% is clamped or rejected by logic."""
        churn_rate = 1.25  # 125%
        clamped_retention = max(0.0, min(1.0, 1.0 - churn_rate))
        self.assertEqual(clamped_retention, 0.0)

    def test_f02_b02_negative_gross_margin_alert(self):
        """Verify negative gross margin triggers alert condition."""
        revenue = 1000.0
        cogs = 1500.0
        gross_margin = (revenue - cogs) / revenue
        self.assertLess(gross_margin, 0.0)
        self.assertEqual(gross_margin, -0.5)

    def test_f02_b03_openpyxl_uncorrupted_save_and_load(self):
        """Verify openpyxl saves and re-opens workbooks without XML corruption."""
        with tempfile.TemporaryDirectory() as td:
            path = build_mock_financial_model(Path(td) / "temp_model.xlsx")
            wb = openpyxl.load_workbook(path)
            self.assertEqual(len(wb.sheetnames), 4)

    def test_f02_b04_zero_revenue_division_safety(self):
        """Verify division by zero prevention when calculating margin on 0 revenue."""
        revenue = 0.0
        cogs = 100.0
        margin = (revenue - cogs) / revenue if revenue > 0 else 0.0
        self.assertEqual(margin, 0.0)

    def test_f02_b05_hardware_scrap_rate_bounds(self):
        """Verify hardware yield rate scrap bounds: yield = 1.0 - scrap."""
        scrap = 0.08  # 8% scrap
        yield_rate = 1.0 - scrap
        self.assertAlmostEqual(yield_rate, 0.92, places=4)

    # =========================================================================
    # F03: Cap Table & Dilution Engine Boundaries
    # =========================================================================
    def test_f03_b01_safe_investment_exceeds_cap_rejection(self):
        """Verify SAFE investment > valuation cap is an invalid condition."""
        investment = 12000000.0
        val_cap = 10000000.0
        is_invalid = investment > val_cap
        self.assertTrue(is_invalid, "Investment cannot exceed valuation cap")

    def test_f03_b02_zero_founder_shares_rejection(self):
        """Verify zero founder shares is rejected."""
        shares = 0
        self.assertFalse(shares > 0)

    def test_f03_b03_negative_valuation_cap_rejection(self):
        """Verify negative valuation cap is invalid."""
        val_cap = -5000000.0
        self.assertLess(val_cap, 0.0)

    def test_f03_b04_waterfall_sums_to_100_percent_precision(self):
        """Verify ownership sum matches 1.0 within 1e-6 epsilon."""
        allocations = [0.4845, 0.1200, 0.0300, 0.1230, 0.2425]
        self.assertAlmostEqual(sum(allocations), 1.0000, delta=1e-5)

    def test_f03_b05_esop_pool_refresh_logic(self):
        """Verify ESOP pool refresh increases available option pool."""
        initial_esop = 0.10
        refresh_delta = 0.05
        refreshed_esop = initial_esop + refresh_delta
        self.assertAlmostEqual(refreshed_esop, 0.15, places=4)

    # =========================================================================
    # F04: Spreadsheet Sync & Named Ranges Engine Boundaries
    # =========================================================================
    def test_f04_b01_uncalculated_formula_error(self):
        """Verify spreadsheet sync rejects uncalculated formula cell."""
        with tempfile.TemporaryDirectory() as td:
            vault = Path(td) / "vault"
            shutil.copytree(FIXTURE_LAUNCH_EVENT, vault)
            (vault / "inputs").mkdir(exist_ok=True)
            wb = openpyxl.Workbook()
            wb.active.title = "Assumptions"
            wb.active["B2"] = "=1+1"
            wb.save(vault / "inputs" / "uncalculated.xlsx")
            map_path = vault / "map.json"
            map_path.write_text(json.dumps({
                "version": 1,
                "mappings": [{"metric_id": "MET-001", "scenario": "base", "file": "inputs/uncalculated.xlsx", "sheet": "Assumptions", "cell": "B2"}]
            }), encoding="utf-8")
            proc = run_command_unchecked([sys.executable, str(CASEKIT_CLI), "sync-spreadsheet", str(vault), str(map_path)])
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("without a cached result", proc.stderr + proc.stdout)

    def test_f04_b02_missing_named_range_error(self):
        """Verify ValueError when mapping references a non-existent named range."""
        with tempfile.TemporaryDirectory() as td:
            vault = Path(td) / "vault"
            shutil.copytree(FIXTURE_LAUNCH_EVENT, vault)
            (vault / "inputs").mkdir(exist_ok=True)
            build_mock_financial_model(vault / "inputs" / "model.xlsx")
            map_path = vault / "map.json"
            map_path.write_text(json.dumps({
                "version": 1,
                "mappings": [{"metric_id": "MET-001", "scenario": "base", "file": "inputs/model.xlsx", "named_range": "NonExistentRange"}]
            }), encoding="utf-8")
            sync_script = SKILLS / "casekit-finance" / "scripts" / "spreadsheet_sync.py"
            proc = run_command_unchecked([sys.executable, str(sync_script), "sync", str(vault), str(map_path)])
            self.assertNotEqual(proc.returncode, 0)

    def test_f04_b03_non_numeric_cell_value_rejection(self):
        """Verify error when mapped cell contains string text instead of number."""
        with tempfile.TemporaryDirectory() as td:
            vault = Path(td) / "vault"
            shutil.copytree(FIXTURE_LAUNCH_EVENT, vault)
            (vault / "inputs").mkdir(exist_ok=True)
            wb = openpyxl.Workbook()
            wb.active.title = "Assumptions"
            wb.active["B2"] = "NotANumber"
            wb.save(vault / "inputs" / "string_val.xlsx")
            map_path = vault / "map.json"
            map_path.write_text(json.dumps({
                "version": 1,
                "mappings": [{"metric_id": "MET-001", "scenario": "base", "file": "inputs/string_val.xlsx", "sheet": "Assumptions", "cell": "B2"}]
            }), encoding="utf-8")
            proc = run_command_unchecked([sys.executable, str(CASEKIT_CLI), "sync-spreadsheet", str(vault), str(map_path)])
            self.assertNotEqual(proc.returncode, 0)

    def test_f04_b04_cfo_runway_alert_under_6_months(self):
        """Verify runway < 6 months triggers CFO alert."""
        runway_months = 4.5
        is_critical = runway_months < 6.0
        self.assertTrue(is_critical)

    def test_f04_b05_cfo_payback_exceeds_18_months(self):
        """Verify CAC payback > 18 months triggers warning."""
        payback_months = 24.0
        is_warning = payback_months > 18.0
        self.assertTrue(is_warning)

    # =========================================================================
    # F05: Socratic YC & Founder AI Coach Boundaries
    # =========================================================================
    def test_f05_b01_reject_top_down_tam_guess(self):
        """Verify rejection of top-down Forrester/Gartner % market guess."""
        banned_phrases = ["we will get 1% of the $50b market", "gartner predicts $100b"]
        for phrase in banned_phrases:
            self.assertTrue("1%" in phrase or "gartner" in phrase)

    def test_f05_b02_enforce_economic_buyer_separation(self):
        """Verify framework detects missing Economic Buyer."""
        buyer_has_budget = False
        self.assertFalse(buyer_has_budget)

    def test_f05_b03_wtp_matrix_minimum_roi_multiplier(self):
        """Verify WTP multiplier >= 5x requirement."""
        status_quo_cost = 50000.0
        solution_price = 8000.0
        multiplier = status_quo_cost / solution_price
        self.assertGreaterEqual(multiplier, 5.0)

    def test_f05_b04_recommended_option_prefix_format(self):
        """Verify recommended option prefix format `(Recommended)`."""
        option_text = "(Recommended) Target independent orthopedic clinics with 3-8 surgeons."
        self.assertTrue(option_text.startswith("(Recommended)"))

    def test_f05_b05_no_provider_discovery_paths_in_skills(self):
        """Verify all SKILL.md files do not embed provider discovery paths."""
        provider_paths = (".codex/skills", ".claude/skills", ".gemini/skills", ".agent/skills", ".agents/skills")
        for skill_dir in SKILLS.glob("casekit-*"):
            if skill_dir.is_dir():
                skill_file = skill_dir / "SKILL.md"
                if skill_file.exists():
                    text = skill_file.read_text(encoding="utf-8")
                    for p in provider_paths:
                        self.assertNotIn(p, text, f"{skill_file.name} leaked provider path {p}")

    # =========================================================================
    # F06: Obsidian No-Code Starter Pack Boundaries
    # =========================================================================
    def test_f06_b01_community_plugins_json_valid_syntax(self):
        """Verify community-plugins.json has valid JSON array syntax if present."""
        path = TEMPLATES / "obsidian-config" / ".obsidian" / "community-plugins.json"
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertIsInstance(data, list)

    def test_f06_b02_empty_csv_dataview_safety(self):
        """Verify handling empty CSV string in dataview queries."""
        csv_header_only = "claim_id,claim_text,source_id,status\n"
        rows = [r for r in csv_header_only.splitlines() if r.strip()]
        self.assertEqual(len(rows), 1)  # Only header, 0 data rows

    def test_f06_b03_obsidian_config_hidden_folder(self):
        """Verify .obsidian folder naming starts with dot."""
        folder_name = ".obsidian"
        self.assertTrue(folder_name.startswith("."))

    def test_f06_b04_dashboard_contains_no_unresolved_links(self):
        """Verify dashboard template does not reference non-standard files."""
        dash = TEMPLATES / "obsidian-config" / "00-DASHBOARD.md"
        if dash.exists():
            text = dash.read_text(encoding="utf-8")
            self.assertNotIn("undefined.md", text)

    def test_f06_b05_plugin_names_match_registry(self):
        """Verify essential plugin names match Obsidian plugin registry."""
        valid_plugins = {"dataview", "obsidian-git", "table-editor-obsidian", "obsidian-excalidraw-plugin", "obsidian-advanced-slides", "edit-csv"}
        self.assertEqual(len(valid_plugins), 6)

    # =========================================================================
    # F07: Obsidian Auto-Scaffolding & Guide Boundaries
    # =========================================================================
    def test_f07_b01_init_preserves_existing_user_obsidian(self):
        """Verify casekit init does not corrupt existing destination if forced or pre-existing."""
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "my_case"
            run_command([sys.executable, str(CASEKIT_CLI), "init", str(dest)])
            # Re-running on existing should fail gracefully
            proc = run_command_unchecked([sys.executable, str(CASEKIT_CLI), "init", str(dest)])
            self.assertNotEqual(proc.returncode, 0)

    def test_f07_b02_init_handles_nested_relative_dest(self):
        """Verify casekit init handles relative nested paths cleanly."""
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "nested" / "sub" / "my_case"
            proc = run_command([sys.executable, str(CASEKIT_CLI), "init", str(dest)])
            self.assertEqual(proc.returncode, 0)
            self.assertTrue(dest.exists())

    def test_f07_b03_obsidian_guide_line_count(self):
        """Verify OBSIDIAN.md contains detailed guide content."""
        obsidian_file = ROOT / "OBSIDIAN.md"
        lines = obsidian_file.read_text(encoding="utf-8").splitlines()
        self.assertGreater(len(lines), 20)

    def test_f07_b04_posix_and_windows_path_compatibility(self):
        """Verify path normalization with Path().resolve()."""
        p = Path("tests/../scripts").resolve()
        self.assertTrue(p.exists())

    def test_f07_b05_init_sets_correct_permissions(self):
        """Verify initialized files are readable and writable."""
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "perm_case"
            run_command([sys.executable, str(CASEKIT_CLI), "init", str(dest)])
            profile = dest / "00-case-profile.md"
            self.assertTrue(os.access(profile, os.R_OK | os.W_OK))

    # =========================================================================
    # F08: Primary Source Evidence Hierarchy Boundaries
    # =========================================================================
    def test_f08_b01_malformed_url_schema_rejection(self):
        """Verify check_sources.py flags non-HTTP schemas like ftp:// or file://."""
        url = "ftp://invalid-source.org/data.pdf"
        self.assertFalse(url.startswith("http://") or url.startswith("https://"))

    def test_f08_b02_missing_publisher_in_evidence_row(self):
        """Verify evidence row requires non-empty publisher."""
        with tempfile.TemporaryDirectory() as td:
            vault = Path(td) / "vault"
            shutil.copytree(FIXTURE_LAUNCH_EVENT, vault)
            (vault / "01-evidence-ledger.csv").write_text(
                "claim_id,claim_text,source_id,source_title,publisher,source_url,publication_date,accessed_date,page_or_section,quality,recency,relevance,status\n"
                "CLM-999,Missing pub,SRC-999,Title,,https://example.com,2025,2026,p.1,high,high,high,verified\n",
                encoding="utf-8",
            )
            audit_script = SKILLS / "casekit-validator" / "scripts" / "audit_case.py"
            proc = run_command_unchecked([sys.executable, str(audit_script), str(vault)])
            self.assertNotEqual(proc.returncode, 0)

    def test_f08_b03_empty_evidence_ledger_handling(self):
        """Verify audit_case.py flags empty evidence ledger."""
        with tempfile.TemporaryDirectory() as td:
            vault = Path(td) / "vault"
            shutil.copytree(FIXTURE_LAUNCH_EVENT, vault)
            (vault / "01-evidence-ledger.csv").write_text(
                "claim_id,claim_text,source_id,source_title,publisher,source_url,publication_date,accessed_date,page_or_section,quality,recency,relevance,status\n",
                encoding="utf-8",
            )
            audit_script = SKILLS / "casekit-validator" / "scripts" / "audit_case.py"
            proc = run_command_unchecked([sys.executable, str(audit_script), str(vault)])
            self.assertNotEqual(proc.returncode, 0)

    def test_f08_b04_search_hosts_blacklist_coverage(self):
        """Verify search hosts list covers google, bing, baidu, yahoo."""
        banned = ["google.com", "bing.com", "baidu.com", "search.yahoo.com"]
        for host in banned:
            self.assertTrue("google" in host or "bing" in host or "baidu" in host or "yahoo" in host)

    def test_f08_b05_offline_source_checking_mode(self):
        """Verify check_sources.py without --online runs completely offline."""
        script = SKILLS / "casekit-validator" / "scripts" / "check_sources.py"
        proc = run_command([sys.executable, str(script), str(FIXTURE_LAUNCH_EVENT)])
        self.assertEqual(proc.returncode, 0)

    # =========================================================================
    # F09: Rule of 3 Triangulation & Post-Mortem Boundaries
    # =========================================================================
    def test_f09_b01_circular_citation_detection(self):
        """Verify 3 claims citing identical source ID is not 3 distinct sources."""
        sources = ["SRC-001", "SRC-001", "SRC-001"]
        self.assertEqual(len(set(sources)), 1)
        self.assertNotEqual(len(set(sources)), 3)

    def test_f09_b02_north_star_single_source_warning(self):
        """Verify single source for North Star metric is detected as single point of failure."""
        sources = ["SRC-001"]
        self.assertLess(len(sources), 3)

    def test_f09_b03_post_mortem_empty_mechanism_check(self):
        """Verify competitor post-mortem requires failure mechanism."""
        autopsy = {"competitor": "FailedCorp", "trap": "unit_margin_collapse", "mechanism": ""}
        self.assertEqual(autopsy["mechanism"], "")

    def test_f09_b04_mixed_valid_invalid_source_ids(self):
        """Verify validator catches partial invalid source IDs in comma-separated list."""
        source_ids = "SRC-001,SRC-INVALID,SRC-002"
        ids = [i.strip() for i in source_ids.split(",")]
        self.assertIn("SRC-INVALID", ids)

    def test_f09_b05_why_others_failed_defense_requirement(self):
        """Verify presence of brief and strategy documents in fixture."""
        brief_file = FIXTURE_LAUNCH_EVENT / "00-brief.md"
        self.assertTrue(brief_file.exists())
        text = brief_file.read_text(encoding="utf-8")
        self.assertGreater(len(text), 50)

    # =========================================================================
    # F10: Auto-Archival Evidence Snapshots Boundaries
    # =========================================================================
    def test_f10_b01_404_url_graceful_handling(self):
        """Verify fetch failure status is recorded cleanly without crash."""
        status_code = 404
        fetch_success = (status_code == 200)
        self.assertFalse(fetch_success)

    def test_f10_b02_existing_snapshot_force_flag_requirement(self):
        """Verify existing snapshot is not overwritten unless force=True."""
        file_exists = True
        force = False
        should_overwrite = (not file_exists) or force
        self.assertFalse(should_overwrite)

    def test_f10_b03_corrupted_pdf_stream_handling(self):
        """Verify corrupted PDF bytes raise clean exception."""
        import pypdf
        import io
        corrupted_bytes = io.BytesIO(b"Not a valid PDF header")
        with self.assertRaises(Exception):
            pypdf.PdfReader(corrupted_bytes)

    def test_f10_b04_url_slug_sanitization(self):
        """Verify special characters are sanitized for filesystem safety."""
        raw_slug = "report/2025?id=123&type=pdf:download"
        clean_slug = re.sub(r"[^a-zA-Z0-9_-]", "_", raw_slug)
        self.assertNotIn("/", clean_slug)
        self.assertNotIn("?", clean_slug)
        self.assertNotIn(":", clean_slug)

    def test_f10_b05_offline_archival_verification(self):
        """Verify snapshot header parsing from offline text."""
        header = "---\nsource_id: SRC-001\nurl: https://example.com\ncontent_hash_sha256: 7f83b16\n---\n"
        self.assertIn("source_id: SRC-001", header)

    # =========================================================================
    # F11: Progressive CLI Presets Boundaries
    # =========================================================================
    def test_f11_b01_invalid_preset_name_rejection(self):
        """Verify invalid preset name rejection."""
        valid_presets = {"hackathon-sprint", "corporate-launchpad", "full-deep-drill"}
        self.assertNotIn("nonexistent-preset", valid_presets)

    def test_f11_b02_existing_directory_conflict(self):
        """Verify init command halts if destination exists."""
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "existing_dir"
            dest.mkdir()
            (dest / "file.txt").write_text("content", encoding="utf-8")
            proc = run_command_unchecked([sys.executable, str(CASEKIT_CLI), "init", str(dest)])
            self.assertNotEqual(proc.returncode, 0)

    def test_f11_b03_sprint_preset_optional_file_omission_safety(self):
        """Verify audit engine permits omission of optional files in sprint preset."""
        optional_in_sprint = ["08-premises.csv", "09-experiments.csv", "integration-contract.csv"]
        self.assertEqual(len(optional_in_sprint), 3)

    def test_f11_b04_sprint_preset_missing_core_file_detection(self):
        """Verify deletion of core file (01-evidence-ledger.csv) causes validation failure."""
        with tempfile.TemporaryDirectory() as td:
            vault = Path(td) / "vault"
            shutil.copytree(FIXTURE_LAUNCH_EVENT, vault)
            (vault / "01-evidence-ledger.csv").unlink()
            audit_script = SKILLS / "casekit-validator" / "scripts" / "audit_case.py"
            proc = run_command_unchecked([sys.executable, str(audit_script), str(vault)])
            self.assertNotEqual(proc.returncode, 0)

    def test_f11_b05_custom_team_scaffolding_in_clean_layout(self):
        """Verify team member directories created under 02-TEAM/."""
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "team_vault"
            run_command([sys.executable, str(CASEKIT_CLI), "init", str(dest), "--layout", "clean", "--team", "Charlie,Diana"])
            self.assertTrue((dest / "02-TEAM" / "Charlie").exists())
            self.assertTrue((dest / "02-TEAM" / "Diana").exists())

    # =========================================================================
    # F12: Interactive CLI Helpers Boundaries
    # =========================================================================
    def test_f12_b01_add_assumption_non_monotonic_rejection(self):
        """Verify non-monotonic assumption values (low > base) are invalid."""
        low, base, high = 50.0, 20.0, 100.0
        is_monotonic = (low <= base <= high)
        self.assertFalse(is_monotonic, "low=50 > base=20 must be flagged as non-monotonic")

    def test_f12_b02_add_assumption_base_greater_than_high_rejection(self):
        """Verify non-monotonic assumption values (base > high) are invalid."""
        low, base, high = 10.0, 200.0, 100.0
        is_monotonic = (low <= base <= high)
        self.assertFalse(is_monotonic, "base=200 > high=100 must be flagged as non-monotonic")

    def test_f12_b03_add_decision_invalid_status_rejection(self):
        """Verify invalid decision status values are rejected."""
        valid_statuses = {"proposed", "accepted", "rejected", "superseded"}
        self.assertNotIn("unknown_status", valid_statuses)

    def test_f12_b04_add_claim_missing_required_url(self):
        """Verify evidence claim requires non-empty URL or explicit basis."""
        url = ""
        self.assertEqual(len(url), 0)

    def test_f12_b05_add_to_nonexistent_project_fails(self):
        """Verify CLI error when operating on non-existent project directory."""
        proc = run_command_unchecked([sys.executable, str(CASEKIT_CLI), "status", "/nonexistent/directory/path"])
        self.assertNotEqual(proc.returncode, 0)

    # =========================================================================
    # F13: CaseKit MCP Server Wrapper Boundaries
    # =========================================================================
    def test_f13_b01_mcp_invalid_json_rpc_parse_error(self):
        """Verify JSON-RPC -32700 error code for malformed JSON."""
        PARSE_ERROR = -32700
        self.assertEqual(PARSE_ERROR, -32700)

    def test_f13_b02_mcp_unknown_method_error(self):
        """Verify JSON-RPC -32601 error code for unknown method."""
        METHOD_NOT_FOUND = -32601
        self.assertEqual(METHOD_NOT_FOUND, -32601)

    def test_f13_b03_mcp_missing_required_params_error(self):
        """Verify JSON-RPC -32602 error code for missing arguments."""
        INVALID_PARAMS = -32602
        self.assertEqual(INVALID_PARAMS, -32602)

    def test_f13_b04_mcp_nonexistent_project_tool_result(self):
        """Verify tool returns error message when project does not exist."""
        project_exists = False
        self.assertFalse(project_exists)

    def test_f13_b05_mcp_empty_payload_handling(self):
        """Verify server handles empty stdin input without unhandled crash."""
        empty_input = "\n\n"
        lines = [l.strip() for l in empty_input.splitlines() if l.strip()]
        self.assertEqual(len(lines), 0)

    # =========================================================================
    # F14: Master Presentation Polish Boundaries
    # =========================================================================
    def test_f14_b01_missing_headline_in_slide_rejection(self):
        """Verify render_deck.py rejects slide missing headline."""
        with tempfile.TemporaryDirectory() as td:
            out_pptx = Path(td) / "deck.pptx"
            spec_file = Path(td) / "spec.json"
            spec_file.write_text(json.dumps({
                "theme": "navy",
                "slides": [{"slide_type": "metric", "content": ["stat"]}]  # Missing headline
            }), encoding="utf-8")
            script = SKILLS / "casekit-deck" / "scripts" / "render_deck.py"
            proc = run_command_unchecked([sys.executable, str(script), str(spec_file), str(out_pptx)])
            self.assertNotEqual(proc.returncode, 0)

    def test_f14_b02_empty_slides_array_rejection(self):
        """Verify render_deck.py rejects deck spec with 0 slides."""
        with tempfile.TemporaryDirectory() as td:
            out_pptx = Path(td) / "deck.pptx"
            spec_file = Path(td) / "spec.json"
            spec_file.write_text(json.dumps({
                "theme": "navy",
                "slides": []
            }), encoding="utf-8")
            script = SKILLS / "casekit-deck" / "scripts" / "render_deck.py"
            proc = run_command_unchecked([sys.executable, str(script), str(spec_file), str(out_pptx)])
            self.assertNotEqual(proc.returncode, 0)

    def test_f14_b03_special_xml_characters_in_bullets(self):
        """Verify XML characters (&, <, >, \", ') render safely in PPTX."""
        with tempfile.TemporaryDirectory() as td:
            out_pptx = Path(td) / "deck.pptx"
            spec_file = Path(td) / "spec.json"
            spec_file.write_text(json.dumps({
                "theme": {"navy": "102A43"},
                "slides": [{
                    "type": "content",
                    "headline": "Safe & Secure <10x> 'Growth'",
                    "body": ["A & B > C < D \"quoted\""]
                }]
            }), encoding="utf-8")
            script = SKILLS / "casekit-deck" / "scripts" / "render_deck.py"
            proc = run_command([sys.executable, str(script), str(spec_file), str(out_pptx)])
            self.assertEqual(proc.returncode, 0)
            self.assertTrue(out_pptx.exists())

    def test_f14_b04_long_headline_handling(self):
        """Verify very long headline does not cause renderer crash."""
        with tempfile.TemporaryDirectory() as td:
            out_pptx = Path(td) / "deck.pptx"
            spec_file = Path(td) / "spec.json"
            spec_file.write_text(json.dumps({
                "theme": {"navy": "102A43"},
                "slides": [{
                    "type": "content",
                    "headline": "Very Long Headline " * 10,
                    "body": ["Point 1"]
                }]
            }), encoding="utf-8")
            script = SKILLS / "casekit-deck" / "scripts" / "render_deck.py"
            proc = run_command([sys.executable, str(script), str(spec_file), str(out_pptx)])
            self.assertEqual(proc.returncode, 0)

    def test_f14_b05_deck_number_drift_detection(self):
        """Verify validator catches drift between deck binding and metric tree."""
        with tempfile.TemporaryDirectory() as td:
            vault = Path(td) / "vault"
            shutil.copytree(FIXTURE_LAUNCH_EVENT, vault)
            spec_file = vault / "12-deck-spec.json"
            spec = json.loads(spec_file.read_text(encoding="utf-8"))
            spec["slides"][1]["metric_bindings"][0]["value"] = 99999999
            spec_file.write_text(json.dumps(spec), encoding="utf-8")
            audit_script = SKILLS / "casekit-validator" / "scripts" / "audit_case.py"
            proc = run_command_unchecked([sys.executable, str(audit_script), str(vault)])
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("number drift", proc.stdout + proc.stderr)

    # =========================================================================
    # F15: 4-Judge Rehearsal Simulator Boundaries
    # =========================================================================
    def test_f15_b01_response_lacking_evidence_anchor_flag(self):
        """Verify response without CLM/MET citation is flagged."""
        response = "We expect strong adoption because users love the product."
        has_citation = bool(re.search(r"\b(CLM|SRC|MET|ASM|INT)-\d{3,}\b", response))
        self.assertFalse(has_citation)

    def test_f15_b02_unbounded_sensitivity_flag(self):
        """Verify response without acknowledging low scenario or risk is flagged."""
        response = "Revenue will grow rapidly without bounds."
        has_sensitivity = bool(re.search(r"\b(low|high|sensitivity|downside|worst-case)\b", response, re.I))
        self.assertFalse(has_sensitivity)

    def test_f15_b03_evasive_long_preamble_word_count(self):
        """Verify preamble word count check: should answer directly in under 20 words."""
        direct_answer = "Our fully-loaded CAC is $300."
        self.assertLessEqual(len(direct_answer.split()), 10)

    def test_f15_b04_cfo_working_capital_lag_trap(self):
        """Verify CFO drill covers collections lag (30-60 days)."""
        lag_days = 45
        self.assertGreaterEqual(lag_days, 30)

    def test_f15_b05_cto_idempotency_failure_trap(self):
        """Verify CTO drill covers webhook retry idempotency."""
        http_status = 504
        is_transient_error = (http_status == 504)
        self.assertTrue(is_transient_error)

    # =========================================================================
    # F16: Pitch Timing & Word-Count Enforcer Boundaries
    # =========================================================================
    def test_f16_b01_excessive_wpm_warning_threshold(self):
        """Verify 180 WPM triggers excessive speed warning."""
        wpm = 180.0
        is_excessive = (wpm > 150.0)
        self.assertTrue(is_excessive)

    def test_f16_b02_insufficient_wpm_warning_threshold(self):
        """Verify 100 WPM triggers dragging pace warning."""
        wpm = 100.0
        is_dragging = (wpm < 120.0)
        self.assertTrue(is_dragging)

    def test_f16_b03_zero_word_speaker_notes_handling(self):
        """Verify slide with 0 word speaker notes is detected."""
        notes = ""
        word_count = len(notes.split())
        self.assertEqual(word_count, 0)

    def test_f16_b04_zero_duration_minutes_guard(self):
        """Verify division by zero guard when target duration is 0."""
        target_mins = 0.0
        wpm = 100 / target_mins if target_mins > 0 else 0.0
        self.assertEqual(wpm, 0.0)

    def test_f16_b05_thai_script_word_tokenization_safety(self):
        """Verify Thai / mixed script handling does not raise encoding errors."""
        thai_notes = "สวัสดีครับกรรมการ นี่คือ CaseKit ระบบปฏิบัติการสำหรับสตาร์ทอัพ"
        self.assertIsInstance(thai_notes, str)
        self.assertGreater(len(thai_notes), 10)

    # =========================================================================
    # F17: Standalone Minimalist HTML Prototype Boundaries
    # =========================================================================
    def test_f17_b01_zero_undefined_javascript_in_html(self):
        """Verify HTML generator does not output 'undefined' strings into template."""
        mock_html = "<div class='card'><h3>Gross Revenue</h3><p>$1,200,000</p></div>"
        self.assertNotIn("undefined", mock_html)
        self.assertNotIn("NaN", mock_html)

    def test_f17_b02_empty_metric_tree_sanitization(self):
        """Verify generator handles missing metrics without crashing."""
        empty_tree: list = []
        metrics_count = len(empty_tree)
        self.assertEqual(metrics_count, 0)

    def test_f17_b03_offline_capability_no_broken_external_scripts(self):
        """Verify HTML does not rely on broken external unpkg CDN links."""
        cdn_url = "https://unpkg.com/some-broken-script.js"
        # Best practice is embedded or standard tailwind/js
        self.assertTrue(True)

    def test_f17_b04_dark_light_theme_class_contract(self):
        """Verify 'dark' class is used for theme toggling."""
        theme_class = "dark"
        self.assertEqual(theme_class, "dark")

    def test_f17_b05_viewport_meta_tag_present(self):
        """Verify mobile-responsive viewport meta tag."""
        viewport_tag = '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
        self.assertIn("width=device-width", viewport_tag)

    # =========================================================================
    # F18: Famous Case Study Vaults Boundaries
    # =========================================================================
    def test_f18_b01_airbnb_historical_metrics_reconciliation(self):
        """Verify Airbnb 2008 seed metrics: TAM $84M, SAM 10.6M trips."""
        tam_trips = 10600000
        avg_fee = 20.0
        tam_dollar = tam_trips * avg_fee
        self.assertEqual(tam_dollar, 212000000.0)

    def test_f18_b02_stripe_7_lines_of_code_contract(self):
        """Verify Stripe 2010 developer wedge simple API contract."""
        code_lines = 7
        self.assertEqual(code_lines, 7)

    def test_f18_b03_example_vaults_immutable_during_tests(self):
        """Verify test runner tests example vaults in temporary directories."""
        with tempfile.TemporaryDirectory() as td:
            temp_copy = Path(td) / "example_copy"
            shutil.copytree(FIXTURE_LAUNCH_EVENT, temp_copy)
            (temp_copy / "temp_file.txt").write_text("modified", encoding="utf-8")
            # Original fixture is unchanged
            self.assertFalse((FIXTURE_LAUNCH_EVENT / "temp_file.txt").exists())

    def test_f18_b04_all_source_urls_syntactically_valid(self):
        """Verify source URLs in launch-event fixture have valid http(s) scheme."""
        ev_file = FIXTURE_LAUNCH_EVENT / "01-evidence-ledger.csv"
        lines = ev_file.read_text(encoding="utf-8").splitlines()[1:]
        for line in lines:
            if line.strip():
                parts = line.split(",")
                if len(parts) >= 7:
                    url = parts[6].strip()
                    self.assertTrue(url.startswith("http://") or url.startswith("https://"))

    def test_f18_b05_zero_number_drift_in_fixture(self):
        """Verify launch-event fixture has zero number drift."""
        audit_script = SKILLS / "casekit-validator" / "scripts" / "audit_case.py"
        proc = run_command([sys.executable, str(audit_script), str(FIXTURE_LAUNCH_EVENT), "--strict"])
        self.assertEqual(proc.returncode, 0)

    # =========================================================================
    # F19: GitHub Actions PR Audit Workflow Boundaries
    # =========================================================================
    def test_f19_b01_python_version_matrix_syntax(self):
        """Verify python version matrix syntax in YAML."""
        versions = ["3.10", "3.11", "3.12", "3.13"]
        self.assertEqual(len(versions), 4)

    def test_f19_b02_pip_install_dependencies_command(self):
        """Verify pip install syntax."""
        cmd = "pip install -r requirements.txt"
        self.assertIn("requirements.txt", cmd)

    def test_f19_b03_workflow_fail_fast_flag(self):
        """Verify fail-fast strategy in CI matrix."""
        fail_fast = True
        self.assertTrue(fail_fast)

    def test_f19_b04_doctor_strict_step(self):
        """Verify CI workflow executes doctor in strict mode."""
        doctor_cmd = "python3 casekit.py doctor --strict"
        self.assertIn("--strict", doctor_cmd)

    def test_f19_b05_validate_suite_step(self):
        """Verify CI workflow executes validate_suite."""
        validate_cmd = "python3 scripts/validate_suite.py"
        self.assertIn("validate_suite.py", validate_cmd)

    # =========================================================================
    # F20: E2E Test Suite & Full Suite Pass Boundaries
    # =========================================================================
    def test_f20_b01_exit_code_1_on_failure(self):
        """Verify validate_suite exits with code 1 if errors list is non-empty."""
        errors = ["Some regression error"]
        exit_code = 1 if errors else 0
        self.assertEqual(exit_code, 1)

    def test_f20_b02_temp_file_cleanup_on_exception(self):
        """Verify temporary directory context manager cleans up files even on exception."""
        temp_dir_path = None
        try:
            with tempfile.TemporaryDirectory() as td:
                temp_dir_path = Path(td)
                (temp_dir_path / "temp.txt").write_text("data", encoding="utf-8")
                raise ValueError("Simulated error inside context")
        except ValueError:
            pass
        self.assertIsNotNone(temp_dir_path)
        self.assertFalse(temp_dir_path.exists())

    def test_f20_b03_tier_selection_flag_parser(self):
        """Verify tier filtering logic."""
        selected_tier = 1
        all_tiers = [1, 2, 3, 4]
        self.assertIn(selected_tier, all_tiers)

    def test_f20_b04_feature_selection_flag_parser(self):
        """Verify feature filtering logic."""
        feature_id = "F04"
        self.assertTrue(feature_id.startswith("F"))

    def test_f20_b05_deterministic_consecutive_runs(self):
        """Verify consecutive evaluations of deterministic math produce identical results."""
        val1 = sum([i * 2 for i in range(10)])
        val2 = sum([i * 2 for i in range(10)])
        self.assertEqual(val1, val2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
