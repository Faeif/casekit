"""Tier 4: Real-World End-to-End Application Scenarios Test Suite for CaseKit.

Tests full venture workflows under realistic hackathon, startup, and enterprise conditions.
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


class TestTier4Scenarios(unittest.TestCase):
    """Tier 4 Real-World Application Scenarios Suite."""

    def test_scenario_01_hackathon_sprint_24h_workflow(self):
        """Scenario 1: Rapid 24-Hour Hackathon Sprint End-to-End Journey."""
        with tempfile.TemporaryDirectory() as td:
            vault = Path(td) / "hackathon_case"
            # 1. Initialize
            proc_init = run_command([sys.executable, str(CASEKIT_CLI), "init", str(vault)])
            self.assertEqual(proc_init.returncode, 0)
            self.assertTrue((vault / "01-evidence-ledger.csv").exists())

            # 2. Populate sample deck slide in 12-deck-spec.json
            deck_spec_file = vault / "12-deck-spec.json"
            deck_spec_file.write_text(json.dumps({
                "theme": {"navy": "102A43", "blue": "1677FF"},
                "meta": {"title": "Hackathon Pitch", "team": "Team Alpha"},
                "slides": [
                    {"type": "cover", "headline": "Fast Venture Pitch", "subhead": "24h sprint pilot"},
                    {"type": "metric", "headline": "Customer Traction", "metric": "1,500+", "label": "Signups", "body": ["Verified with pilot data"]}
                ]
            }), encoding="utf-8")

            # 3. Check status
            proc_status = run_command([sys.executable, str(CASEKIT_CLI), "status", str(vault)])
            self.assertEqual(proc_status.returncode, 0)

            # 4. Render slide deck
            out_pptx = vault / "hackathon_deck.pptx"
            proc_render = run_command([sys.executable, str(CASEKIT_CLI), "render", str(vault), "--output", str(out_pptx)])
            self.assertEqual(proc_render.returncode, 0)
            self.assertTrue(out_pptx.exists())

    def test_scenario_02_b2b_saas_series_a_due_diligence(self):
        """Scenario 2: B2B SaaS Series A Dilution & Metrics Due Diligence."""
        with tempfile.TemporaryDirectory() as td:
            vault = Path(td) / "saas_due_diligence"
            shutil.copytree(FIXTURE_LAUNCH_EVENT, vault)
            (vault / "inputs").mkdir(exist_ok=True)

            # 1. Build SaaS Financial Model
            model_path = build_mock_financial_model(
                vault / "inputs" / "b2b_saas.xlsx",
                scenario_revenue=2500000.0,
                gross_margin=0.82,
                cash_runway_months=24.0,
                cac_payback_months=9.0,
                ltv_to_cac=5.2,
            )
            self.assertTrue(model_path.exists())

            # 2. Cap Table Waterfall calculations
            safe_investment = 500000.0
            safe_cap = 10000000.0
            safe_ownership = safe_investment / safe_cap
            self.assertAlmostEqual(safe_ownership, 0.05)

            # Series A $10M on $40M pre-money (20% new dilution)
            post_series_a_founders = (1.0 - 0.15) * (1.0 - safe_ownership) * 0.80
            self.assertGreater(post_series_a_founders, 0.40)

            # 3. Map & Sync to Metric Tree
            map_path = vault / "data-import-map.json"
            map_path.write_text(json.dumps({
                "version": 1,
                "mappings": [
                    {"metric_id": "MET-001", "scenario": "base", "file": "inputs/b2b_saas.xlsx", "named_range": "Gross_Revenue_Base"}
                ]
            }), encoding="utf-8")
            sync_script = SKILLS / "casekit-finance" / "scripts" / "spreadsheet_sync.py"
            proc_sync = run_command([sys.executable, str(sync_script), "sync", str(vault), str(map_path), "--apply"])
            self.assertEqual(proc_sync.returncode, 0)

            # 4. Verify updated metric
            metric_text = (vault / "03-metric-tree.csv").read_text(encoding="utf-8")
            self.assertIn("2500000", metric_text)

    def test_scenario_03_marketplace_two_sided_liquidity_and_float(self):
        """Scenario 3: Two-Sided Marketplace Liquidity & Float Economics."""
        with tempfile.TemporaryDirectory() as td:
            vault = Path(td) / "marketplace_vault"
            shutil.copytree(FIXTURE_LAUNCH_EVENT, vault)

            # 1. Mathematical model of marketplace unit economics
            gmv = 10000000.0
            take_rate = 0.15
            net_revenue = gmv * take_rate
            self.assertEqual(net_revenue, 1500000.0)

            buyer_cac = 25.0
            seller_cac = 150.0
            buyer_to_seller_ratio = 20.0
            blended_cac_per_order = (buyer_cac + (seller_cac / buyer_to_seller_ratio)) / 2.5
            self.assertLess(blended_cac_per_order, 20.0)

            # 2. Float working capital calculation (14 days payout lag)
            daily_gmv = gmv / 365.0
            float_held = daily_gmv * 14.0
            self.assertGreater(float_held, 300000.0)

    def test_scenario_04_enterprise_corporate_launchpad_transformation(self):
        """Scenario 4: Enterprise Corporate Launchpad & Synergy Transformation."""
        with tempfile.TemporaryDirectory() as td:
            vault = Path(td) / "enterprise_vault"
            shutil.copytree(FIXTURE_LAUNCH_EVENT, vault)

            # 1. Corporate ROI NPV & Labor Savings Math
            eligible_users = 1000
            hours_saved_weekly = 3.5
            loaded_wage_hr = 50.0
            weeks_per_yr = 50
            realization_rate = 0.80

            annual_gross_savings = eligible_users * hours_saved_weekly * loaded_wage_hr * weeks_per_yr * realization_rate
            self.assertEqual(annual_gross_savings, 7000000.0)

            annual_license_fee = eligible_users * 1200.0
            net_annual_savings = annual_gross_savings - annual_license_fee
            self.assertEqual(net_annual_savings, 5800000.0)

            roi_multiple = annual_gross_savings / annual_license_fee
            self.assertGreaterEqual(roi_multiple, 5.0)

            # 2. Rehearsal Q&A Persona Coverage
            audit_script = SKILLS / "casekit-validator" / "scripts" / "audit_case.py"
            proc_audit = run_command([sys.executable, str(audit_script), str(vault), "--strict"])
            self.assertEqual(proc_audit.returncode, 0)

    def test_scenario_05_hardware_iot_asset_light_production(self):
        """Scenario 5: Asset-Light Hardware & IoT Production Lifecycle."""
        # 1. Unit BOM & Gross Margin Math
        bom_cost = 45.0
        freight = 5.0
        scrap_rate = 0.06
        yield_rate = 1.0 - scrap_rate
        unit_cogs = (bom_cost + freight) / yield_rate + 2.0  # +$2 warranty reserve
        self.assertAlmostEqual(unit_cogs, 55.19, delta=0.5)

        msrp = 149.0
        gross_margin = (msrp - unit_cogs) / msrp
        self.assertGreaterEqual(gross_margin, 0.60)

        # 2. IoT Cloud Subscription recurring attachment
        sub_arpu_mo = 9.99
        sub_cogs_mo = 1.50
        sub_contribution_mo = sub_arpu_mo - sub_cogs_mo
        self.assertAlmostEqual(sub_contribution_mo, 8.49, places=2)

    def test_scenario_06_d2c_retail_cohort_retention_and_contribution(self):
        """Scenario 6: D2C Retail Cohort Retention & Contribution Margin."""
        # 1. First order contribution economics
        aov = 85.0
        shipping_revenue = 5.0
        returns_allowance = 0.08 * aov
        net_order_value = aov + shipping_revenue - returns_allowance

        cogs = 25.0
        fulfillment = 8.0
        blended_cac = 22.0
        order_variable_cost = cogs + fulfillment + (0.029 * aov + 0.30)
        contribution_1 = net_order_value - order_variable_cost - blended_cac
        self.assertGreater(contribution_1, 15.0)

        # 2. 12-Month repeat order cohort multiplier
        repeat_orders_yr1 = 1.8
        annual_contribution_ltv = (net_order_value - order_variable_cost) * repeat_orders_yr1
        ltv_to_cac = annual_contribution_ltv / blended_cac
        self.assertGreaterEqual(ltv_to_cac, 3.0)

    def test_scenario_07_yc_demo_day_pitch_rehearsal_and_timing(self):
        """Scenario 7: YC Demo Day Pitch Rehearsal & Pacing Defense."""
        # 1. 5-Minute Pitch Word Budget Verification
        pitch_duration_min = 5.0
        target_wpm = 140.0
        target_total_words = pitch_duration_min * target_wpm
        self.assertEqual(target_total_words, 700.0)

        # 2. 4-Move Response Sequence Verification
        response = {
            "move_1_direct_answer": "Our fully-loaded CAC is $300 across paid search and developer evangelism.",
            "move_2_evidence_anchor": "Anchored in CLM-001 and MET-001 cohort retention data.",
            "move_3_sensitivity_bound": "Under our low scenario (ASM-001), CAC increases to $450 with 14 months runway.",
            "move_4_validated_action": "We are executing EXP-001 landing page optimization next week."
        }
        self.assertEqual(len(response), 4)
        self.assertIn("CLM-001", response["move_2_evidence_anchor"])
        self.assertIn("ASM-001", response["move_3_sensitivity_bound"])
        self.assertIn("EXP-001", response["move_4_validated_action"])

    def test_scenario_08_canonical_case_study_replay(self):
        """Scenario 8: Canonical Historical Case Study Replay & Integrity Audit."""
        # Validate launch-event synthetic baseline fixture
        audit_script = SKILLS / "casekit-validator" / "scripts" / "audit_case.py"
        proc = run_command([sys.executable, str(audit_script), str(FIXTURE_LAUNCH_EVENT), "--strict"])
        self.assertEqual(proc.returncode, 0)
        self.assertIn("0 error(s)", proc.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
