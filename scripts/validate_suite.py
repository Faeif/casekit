#!/usr/bin/env python3
"""Validate the CaseKit package and run deterministic smoke tests."""

import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from openpyxl import Workbook


ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
NAME_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")
PROVIDER_PATHS = (".codex/skills", ".claude/skills", ".gemini/skills", ".agent/skills", ".agents/skills")


def fail(message, errors):
    errors.append(message)


def run(command):
    return subprocess.run(command, check=True, capture_output=True, text=True)


def run_unchecked(command):
    return subprocess.run(command, check=False, capture_output=True, text=True)


def replace_fixture_ids(value):
    if isinstance(value, dict):
        return {key: replace_fixture_ids(item) for key, item in value.items()}
    if isinstance(value, list):
        return [replace_fixture_ids(item) for item in value]
    if isinstance(value, str) and value.startswith("ASM-"):
        return "ASM-001"
    if isinstance(value, str) and value.startswith("MET-"):
        return "MET-001"
    return value


def parse_frontmatter(path, errors):
    text = path.read_text(encoding="utf-8")
    if "TODO" in text:
        fail(f"{path}: contains TODO placeholder", errors)
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        fail(f"{path}: missing YAML frontmatter", errors)
        return {}, text
    try:
        end = lines.index("---", 1)
    except ValueError:
        fail(f"{path}: unclosed YAML frontmatter", errors)
        return {}, text
    metadata = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        if ":" not in line:
            fail(f"{path}: malformed frontmatter line: {line}", errors)
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip()
    if set(metadata) != {"name", "description"}:
        fail(f"{path}: frontmatter must contain only name and description", errors)
    return metadata, text


def validate_skill(skill, errors):
    skill_file = skill / "SKILL.md"
    agent_file = skill / "agents" / "openai.yaml"
    if not skill_file.exists():
        fail(f"{skill}: missing SKILL.md", errors)
        return
    metadata, text = parse_frontmatter(skill_file, errors)
    name = metadata.get("name", "")
    if name != skill.name:
        fail(f"{skill}: frontmatter name '{name}' does not match directory", errors)
    if not NAME_RE.fullmatch(name):
        fail(f"{skill}: invalid skill name '{name}'", errors)
    if "--" in name:
        fail(f"{skill}: skill name contains consecutive hyphens", errors)
    if not metadata.get("description"):
        fail(f"{skill}: empty description", errors)
    if len(metadata.get("description", "")) > 1024:
        fail(f"{skill}: description exceeds Agent Skills 1024-character limit", errors)
    if len(text.splitlines()) > 500:
        fail(f"{skill_file}: exceeds 500 lines", errors)
    for provider_path in PROVIDER_PATHS:
        if provider_path in text:
            fail(f"{skill_file}: embeds provider discovery path {provider_path}; keep it in the portability adapter", errors)
    if not agent_file.exists():
        fail(f"{skill}: missing agents/openai.yaml", errors)
    else:
        agent_text = agent_file.read_text(encoding="utf-8")
        if f"${name}" not in agent_text:
            fail(f"{agent_file}: default prompt must mention ${name}", errors)


def smoke_tests(errors):
    orchestrator = SKILLS / "casekit-orchestrator" / "scripts"
    finance = SKILLS / "casekit-finance"
    validator = SKILLS / "casekit-validator" / "scripts"
    deck = SKILLS / "casekit-deck" / "scripts" / "render_deck.py"
    fixture = ROOT / "examples" / "launch-event"
    casekit_cli = ROOT / "casekit.py"
    try:
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            project = temp_path / "sample-case"
            run([sys.executable, str(orchestrator / "new_case.py"), str(project)])
            run([sys.executable, str(orchestrator / "validate_case.py"), str(project)])
            required_start_files = {
                "README-START-HERE.md",
                "TEAM-WORKFLOW.md",
                "00-INBOX/README.md",
                "inputs/README.md",
                "00-case-profile.md",
                "research-backlog.csv",
                "option-portfolio.csv",
                "qna-bank.csv",
                "data-import-map.json",
                "integration-contract.csv",
                "engineering-delivery-plan.md",
                "engineering/00-engineering-profile.json",
                "engineering/architecture.md",
                "engineering/production-readiness.csv",
                "16-vision-growth-plan.md",
                "idea-backlog.csv",
            }
            missing_start_files = sorted(name for name in required_start_files if not (project / name).exists())
            if missing_start_files:
                fail(f"Obsidian workspace template is missing: {missing_start_files}", errors)

            production_case = temp_path / "production-case"
            shutil.copytree(fixture, production_case)
            (production_case / "engineering").mkdir()
            (production_case / "engineering" / "00-engineering-profile.json").write_text(
                json.dumps({"delivery_level": "production", "architecture_style": "modular-monolith"}),
                encoding="utf-8",
            )
            production_result = run_unchecked([sys.executable, str(validator / "audit_case.py"), str(production_case)])
            if production_result.returncode == 0 or "missing production artifact engineering/architecture.md" not in production_result.stdout:
                fail("Production readiness regression did not require architecture artifacts", errors)
            cli_project = temp_path / "cli-case"
            run([sys.executable, str(casekit_cli), "init", str(cli_project), "--case-type", "startup"])
            for skill_name in ("casekit-strategy", "casekit-engineering"):
                if not (cli_project / ".agents" / "skills" / skill_name / "SKILL.md").exists():
                    fail(f"Clone-to-case CLI did not install {skill_name}", errors)
            clean_cli_project = temp_path / "clean-cli-case"
            run([sys.executable, str(casekit_cli), "init", str(clean_cli_project), "--layout", "clean", "--team", "Alice,Bob"])
            clean_required = {
                "01-INPUTS/README.md", "02-TEAM/Alice/01-RESEARCH/.gitkeep", "02-TEAM/Bob/03-READY/.gitkeep",
                "03-OFFICIAL/00-case-profile.md", "03-OFFICIAL/12-deck-spec.json", "00-START-HERE.md", "AGENTS.md",
            }
            missing_clean = sorted(name for name in clean_required if not (clean_cli_project / name).exists())
            if missing_clean:
                fail(f"Clean team layout is missing: {missing_clean}", errors)
            if (clean_cli_project / "00-case-profile.md").exists() or (clean_cli_project / "inputs").exists():
                fail("Clean team layout retained legacy root artifacts", errors)
            clean_status = run([sys.executable, str(casekit_cli), "status", str(clean_cli_project)])
            if "Layout: clean team" not in clean_status.stdout or "Next: add the official brief" not in clean_status.stdout:
                fail("Workspace status did not report the expected clean-layout onboarding step", errors)
            install_target = temp_path / "installed"
            run(
                [
                    sys.executable,
                    str(ROOT / "install.py"),
                    "--target",
                    str(install_target),
                ]
            )
            marker = install_target / "casekit-finance" / "local-user-file.txt"
            marker.write_text("must survive dry run", encoding="utf-8")
            run([sys.executable, str(ROOT / "install.py"), "--target", str(install_target), "--force", "--dry-run"])
            if not marker.exists():
                fail("Installer dry-run modified an installed skill", errors)
            run([sys.executable, str(ROOT / "install.py"), "--target", str(install_target), "--force"])
            if marker.exists():
                fail("Installer force test did not replace the staged skill", errors)

            portable_project = temp_path / "portable-project"
            run([sys.executable, str(ROOT / "install.py"), "--scope", "project", "--project-root", str(portable_project)])
            portable_targets = [portable_project / ".agents" / "skills", portable_project / ".claude" / "skills"]
            for target in portable_targets:
                installed_names = {path.name for path in target.glob("casekit-*") if path.is_dir()}
                expected_names = {path.name for path in SKILLS.glob("casekit-*") if path.is_dir()}
                if installed_names != expected_names:
                    fail(f"Universal project install mismatch at {target}", errors)
                for name in expected_names:
                    source_text = (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
                    installed_text = (target / name / "SKILL.md").read_text(encoding="utf-8")
                    if installed_text != source_text:
                        fail(f"Provider adapter changed canonical skill content for {name} at {target}", errors)

            target_listing = run([sys.executable, str(ROOT / "install.py"), "--platform", "universal", "--scope", "project", "--project-root", str(portable_project), "--list-targets"])
            listed = {Path(line).resolve() for line in target_listing.stdout.splitlines() if line.strip()}
            if listed != {path.resolve() for path in portable_targets}:
                fail("Universal project target resolution returned unexpected paths", errors)

            project_adapters = {
                "codex": Path(".agents/skills"),
                "claude": Path(".claude/skills"),
                "gemini": Path(".agents/skills"),
                "antigravity": Path(".agents/skills"),
                "legacy-codex": Path(".codex/skills"),
                "legacy-gemini": Path(".gemini/skills"),
                "legacy-antigravity": Path(".agent/skills"),
            }
            for platform, relative in project_adapters.items():
                adapter = run([sys.executable, str(ROOT / "install.py"), "--platform", platform, "--scope", "project", "--project-root", str(portable_project), "--list-targets"])
                resolved = Path(adapter.stdout.strip()).resolve()
                if resolved != (portable_project / relative).resolve():
                    fail(f"Unexpected {platform} project adapter target: {resolved}", errors)

            context_bundle = temp_path / "casekit-context.md"
            run([sys.executable, str(ROOT / "scripts" / "export_context.py"), "--skill", "casekit-finance", "--skill", "casekit-validator", "--output", str(context_bundle)])
            bundle_text = context_bundle.read_text(encoding="utf-8")
            if "Skill package: casekit-finance" not in bundle_text or "Skill package: casekit-validator" not in bundle_text:
                fail("Portable context export omitted a requested skill", errors)
            if "<casekit-file path=\"skills/casekit-finance/SKILL.md\">" not in bundle_text:
                fail("Portable context export omitted canonical SKILL.md content", errors)

            deck_path = temp_path / "fixture.pptx"
            run([sys.executable, str(deck), str(fixture / "12-deck-spec.json"), str(deck_path)])
            with zipfile.ZipFile(deck_path) as archive:
                names = set(archive.namelist())
                required = {"[Content_Types].xml", "ppt/presentation.xml", "ppt/slides/slide1.xml", "ppt/slides/slide5.xml"}
                if not required <= names:
                    fail(f"Deck smoke test missing PPTX package entries: {sorted(required - names)}", errors)

            clean_layout = temp_path / "clean-layout"
            clean_official = clean_layout / "03-OFFICIAL"
            shutil.copytree(fixture, clean_official)
            (clean_layout / "01-INPUTS").mkdir()
            run([sys.executable, str(validator / "audit_case.py"), str(clean_layout), "--strict"])
            run([sys.executable, str(validator / "check_sources.py"), str(clean_layout)])
            clean_deck = temp_path / "clean-layout.pptx"
            run([sys.executable, str(casekit_cli), "render", str(clean_layout), "--output", str(clean_deck)])
            if not clean_deck.exists():
                fail("Clean-layout render did not create a PowerPoint", errors)

            synced = temp_path / "spreadsheet-sync-case"
            shutil.copytree(fixture, synced)
            (synced / "inputs").mkdir()
            workbook_path = synced / "inputs" / "model.xlsx"
            book = Workbook()
            sheet = book.active
            sheet.title = "Assumptions"
            sheet["B2"] = 1234567
            book.save(workbook_path)
            mapping_path = synced / "data-import-map.json"
            mapping_path.write_text(json.dumps({"version": 1, "mappings": [{"metric_id": "MET-001", "scenario": "base", "file": "inputs/model.xlsx", "sheet": "Assumptions", "cell": "B2"}]}), encoding="utf-8")
            inspection_path = synced / "inputs" / "model-inspection.md"
            run([sys.executable, str(casekit_cli), "inspect-spreadsheet", str(workbook_path), "--output", str(inspection_path)])
            if "Spreadsheet inspection" not in inspection_path.read_text(encoding="utf-8"):
                fail("Spreadsheet inspection did not create AI-readable Markdown", errors)
            preview = run([sys.executable, str(casekit_cli), "sync-spreadsheet", str(synced), str(mapping_path)])
            if "Preview only" not in preview.stdout or "1234567" not in preview.stdout:
                fail("Spreadsheet sync preview did not report the mapped value", errors)
            run([sys.executable, str(casekit_cli), "sync-spreadsheet", str(synced), str(mapping_path), "--apply"])
            metric_text = (synced / "03-metric-tree.csv").read_text(encoding="utf-8")
            if "MET-001,,Gross revenue,outcome,orders * average_order_value,THB,launch period,324000,1234567,1500000" not in metric_text:
                fail("Spreadsheet sync did not update the mapped metric", errors)
            synced_result = run_unchecked([sys.executable, str(validator / "audit_case.py"), str(synced)])
            if synced_result.returncode == 0 or "number drift for MET-001/base" not in synced_result.stdout:
                fail("Spreadsheet sync regression did not surface deck number drift", errors)
            formula_path = synced / "inputs" / "uncalculated.xlsx"
            formula_book = Workbook()
            formula_book.active.title = "Assumptions"
            formula_book.active["B2"] = "=1+1"
            formula_book.save(formula_path)
            formula_mapping = synced / "formula-import-map.json"
            formula_mapping.write_text(json.dumps({"version": 1, "mappings": [{"metric_id": "MET-001", "scenario": "base", "file": "inputs/uncalculated.xlsx", "sheet": "Assumptions", "cell": "B2"}]}), encoding="utf-8")
            formula_result = run_unchecked([sys.executable, str(casekit_cli), "sync-spreadsheet", str(synced), str(formula_mapping)])
            if formula_result.returncode == 0 or "without a cached result" not in formula_result.stderr:
                fail("Spreadsheet sync did not reject an uncalculated Excel formula", errors)

            strategy_case = temp_path / "strategy-case"
            shutil.copytree(fixture, strategy_case)
            (strategy_case / "option-portfolio.csv").write_text(
                "option_id,option_name,target_segment,mechanism,decision_goal,rubric_fit,impact,feasibility,viability,differentiation,evidence_confidence,weighted_score,evidence_ids,assumption_ids,critical_risk,fastest_test,stop_condition,owner,status\n"
                "OPT-001,Primary option,Eligible members,Invitation funnel,Validate demand,5,4,4,4,3,3,4.0,CLM-001,ASM-001,Low conversion,Landing test,Stop below threshold,Strategy,chosen\n"
                "OPT-002,Alternative option,Eligible members,Partner funnel,Validate demand,3,3,4,3,3,2,3.0,CLM-002,ASM-002,Partner delay,Partner interview,Stop without partner,Strategy,rejected\n",
                encoding="utf-8",
            )
            run([sys.executable, str(validator / "audit_case.py"), str(strategy_case), "--strict"])
            option_text = (strategy_case / "option-portfolio.csv").read_text(encoding="utf-8").replace("OPT-002,Alternative option", "OPT-001,Alternative option")
            (strategy_case / "option-portfolio.csv").write_text(option_text, encoding="utf-8")
            duplicate_option = run_unchecked([sys.executable, str(validator / "audit_case.py"), str(strategy_case)])
            if duplicate_option.returncode == 0 or "duplicate option_id OPT-001" not in duplicate_option.stdout:
                fail("Strategy option regression did not reject duplicate option IDs", errors)

            integration_case = temp_path / "integration-case"
            shutil.copytree(fixture, integration_case)
            (integration_case / "integration-contract.csv").write_text(
                "integration_id,system,purpose,user_journey_step,delivery_level,status,interface_type,auth_method,data_in,data_out,personal_data_classification,consent_or_legal_basis,owner,partner_owner,dependency,rate_limit_or_sla,cost_driver,fallback,demo_evidence,source_or_assumption_ids,risk_id,go_live_gate\n"
                "INT-001,Messaging partner,Send action alert,Notify caregiver,pilot,mocked,Webhook,N/A,Alert payload,Delivery status,low,N/A,Product,Partner pending,Mock service,N/A,ASM-005,Manual call,Screen recording,ASM-005,RSK-001,Partner approval\n",
                encoding="utf-8",
            )
            run([sys.executable, str(validator / "audit_case.py"), str(integration_case), "--strict"])
            real_text = (integration_case / "integration-contract.csv").read_text(encoding="utf-8").replace(",pilot,mocked,", ",production,real,")
            real_text = real_text.replace(",N/A,Alert payload", ",,Alert payload")
            (integration_case / "integration-contract.csv").write_text(real_text, encoding="utf-8")
            missing_real_fields = run_unchecked([sys.executable, str(validator / "audit_case.py"), str(integration_case)])
            if missing_real_fields.returncode == 0 or "real integration requires auth_method" not in missing_real_fields.stdout:
                fail("Integration contract regression did not reject an unsupported real integration", errors)

            idea_case = temp_path / "idea-case"
            shutil.copytree(fixture, idea_case)
            (idea_case / "idea-backlog.csv").write_text(
                "idea_id,title,status,origin,problem_or_hypothesis,proposed_mechanism,owner,required_evidence_or_test,experiment_ids,decision_id,promoted_artifacts,next_action,rationale_or_disposition\n"
                "IDEA-001,Test referral,accepted-for-test,Team chat,Referrals may lower CAC,Referral incentive,Growth,Landing-page test,EXP-001,,,Run test,Test before using in deck\n",
                encoding="utf-8",
            )
            run([sys.executable, str(validator / "audit_case.py"), str(idea_case), "--strict"])
            invalid_idea_text = (idea_case / "idea-backlog.csv").read_text(encoding="utf-8").replace("accepted-for-test", "accepted-for-case")
            (idea_case / "idea-backlog.csv").write_text(invalid_idea_text, encoding="utf-8")
            invalid_idea = run_unchecked([sys.executable, str(validator / "audit_case.py"), str(idea_case)])
            if invalid_idea.returncode == 0 or "accepted-for-case requires decision_id" not in invalid_idea.stdout:
                fail("Idea-promotion regression did not require an explicit case decision", errors)

            broken = temp_path / "broken-case"
            shutil.copytree(fixture, broken)
            assumption_path = broken / "02-assumptions.csv"
            assumption_path.write_text(assumption_path.read_text(encoding="utf-8") + "ASM-999,broken,broken,rate,0,0.5,1,team-judgment,SRC-999,low,high,test,QA,open\n", encoding="utf-8")
            broken_result = run_unchecked([sys.executable, str(validator / "audit_case.py"), str(broken)])
            if broken_result.returncode == 0 or "unresolved source reference SRC-999" not in broken_result.stdout:
                fail("Validator regression test did not reject an unresolved source ID", errors)

            drift = temp_path / "number-drift-case"
            shutil.copytree(fixture, drift)
            deck_spec_path = drift / "12-deck-spec.json"
            deck_spec = json.loads(deck_spec_path.read_text(encoding="utf-8"))
            deck_spec["slides"][1]["metric_bindings"][0]["value"] = 999999
            deck_spec_path.write_text(json.dumps(deck_spec, ensure_ascii=False, indent=2), encoding="utf-8")
            drift_result = run_unchecked([sys.executable, str(validator / "audit_case.py"), str(drift)])
            if drift_result.returncode == 0 or "number drift for MET-001/base" not in drift_result.stdout:
                fail("Validator regression test did not reject deck/model number drift", errors)

            snippet_case = temp_path / "search-snippet-case"
            shutil.copytree(fixture, snippet_case)
            evidence_path = snippet_case / "01-evidence-ledger.csv"
            evidence_path.write_text(evidence_path.read_text(encoding="utf-8").replace("https://example.com/synthetic-casekit-fixture", "https://www.google.com/search?q=synthetic+fixture"), encoding="utf-8")
            snippet_result = run_unchecked([sys.executable, str(validator / "check_sources.py"), str(snippet_case)])
            if snippet_result.returncode == 0 or "search-result URL is not an acceptable source" not in snippet_result.stdout:
                fail("Source-check regression test did not reject a search-result citation", errors)

            unit_script = finance / "scripts" / "unit_economics.py"
            unit_example = finance / "assets" / "unit-economics-input.example.json"
            unit_result = run([sys.executable, str(unit_script), str(unit_example)])
            unit_output = json.loads(unit_result.stdout)
            expected_unit_values = {
                "selected_cac": 300.0,
                "discounted_cohort_ltv_contribution": 589.5,
                "ltv_to_cac": 1.965,
                "cac_payback_periods": 5,
            }
            for key, expected_value in expected_unit_values.items():
                if unit_output.get("unit_economics", {}).get(key) != expected_value:
                    fail(f"Unit-economics smoke test returned unexpected {key}", errors)
            if unit_output.get("recurring_revenue", {}).get("gross_revenue_retention") != 0.9 or unit_output.get("recurring_revenue", {}).get("net_revenue_retention") != 0.95:
                fail("Recurring-revenue smoke test returned unexpected GRR/NRR", errors)
            if unit_output.get("cash", {}).get("runway_periods") != 4.8:
                fail("Cash smoke test returned unexpected runway", errors)
            if not all(result.get("pass") for result in unit_output.get("decision_threshold_results", [])):
                fail("Unit-economics example did not pass its synthetic decision thresholds", errors)

            invalid_unit = json.loads(unit_example.read_text(encoding="utf-8"))
            invalid_unit["cohort"][2]["logo_retention_rate"] = 0.95
            invalid_unit_path = temp_path / "invalid-unit.json"
            invalid_unit_path.write_text(json.dumps(invalid_unit), encoding="utf-8")
            invalid_unit_result = run_unchecked([sys.executable, str(unit_script), str(invalid_unit_path)])
            if invalid_unit_result.returncode == 0 or "logo retention cannot increase" not in invalid_unit_result.stderr:
                fail("Unit-economics regression test did not reject increasing logo retention", errors)

            invalid_channels = json.loads(unit_example.read_text(encoding="utf-8"))
            invalid_channels["acquisition"]["channels"][0]["new_customers"] = 800
            invalid_channels_path = temp_path / "invalid-channels.json"
            invalid_channels_path.write_text(json.dumps(invalid_channels), encoding="utf-8")
            invalid_channels_result = run_unchecked([sys.executable, str(unit_script), str(invalid_channels_path)])
            if invalid_channels_result.returncode == 0 or "channel new_customers exceed" not in invalid_channels_result.stderr:
                fail("Unit-economics regression test did not reject over-attributed customers", errors)

            invalid_mrr = json.loads(unit_example.read_text(encoding="utf-8"))
            invalid_mrr["recurring_revenue"]["contraction_mrr"] = 60000
            invalid_mrr["recurring_revenue"]["churned_mrr"] = 60000
            invalid_mrr_path = temp_path / "invalid-mrr.json"
            invalid_mrr_path.write_text(json.dumps(invalid_mrr), encoding="utf-8")
            invalid_mrr_result = run_unchecked([sys.executable, str(unit_script), str(invalid_mrr_path)])
            if invalid_mrr_result.returncode == 0 or "cannot exceed starting_mrr" not in invalid_mrr_result.stderr:
                fail("Recurring-revenue regression test did not reject impossible MRR movement", errors)

            no_payback = json.loads(unit_example.read_text(encoding="utf-8"))
            no_payback["acquisition"]["attributable_spend"] = 1000000
            no_payback["acquisition"]["fully_loaded_spend"] = 1000000
            no_payback_path = temp_path / "no-payback.json"
            no_payback_path.write_text(json.dumps(no_payback), encoding="utf-8")
            no_payback_output = json.loads(run([sys.executable, str(unit_script), str(no_payback_path)]).stdout)
            if no_payback_output["unit_economics"]["payback_reached_within_horizon"] is not False or not no_payback_output["warnings"]:
                fail("Unit-economics regression test did not expose payback beyond the modeled horizon", errors)

            discounted = json.loads(unit_example.read_text(encoding="utf-8"))
            discounted["discount_rate_per_period"] = 0.01
            discounted_path = temp_path / "discounted-unit.json"
            discounted_path.write_text(json.dumps(discounted), encoding="utf-8")
            discounted_output = json.loads(run([sys.executable, str(unit_script), str(discounted_path)]).stdout)
            if discounted_output["unit_economics"]["discounted_cohort_ltv_contribution"] >= 589.5:
                fail("Unit-economics discounting regression did not reduce cohort LTV", errors)

            threshold_unit = json.loads(unit_example.read_text(encoding="utf-8"))
            threshold_unit["decision_thresholds"]["minimum_ltv_to_cac"] = 2.0
            threshold_unit_path = temp_path / "threshold-unit.json"
            threshold_unit_path.write_text(json.dumps(threshold_unit), encoding="utf-8")
            threshold_result = json.loads(run([sys.executable, str(unit_script), str(threshold_unit_path)]).stdout)
            if threshold_result["decision_threshold_results"][0]["pass"] is not False:
                fail("Unit-economics threshold regression did not expose a failed decision gate", errors)

            economics_project = temp_path / "economics-project"
            shutil.copytree(fixture, economics_project)
            linked_input = replace_fixture_ids(json.loads(unit_example.read_text(encoding="utf-8")))
            linked_input_path = temp_path / "linked-unit.json"
            linked_input_path.write_text(json.dumps(linked_input), encoding="utf-8")
            run([sys.executable, str(unit_script), str(linked_input_path), "--output", str(economics_project / "14-unit-economics.json")])
            run([sys.executable, str(validator / "audit_case.py"), str(economics_project), "--strict"])
            tampered = json.loads((economics_project / "14-unit-economics.json").read_text(encoding="utf-8"))
            tampered["unit_economics"]["ltv_to_cac"] = 99
            (economics_project / "14-unit-economics.json").write_text(json.dumps(tampered), encoding="utf-8")
            tampered_result = run_unchecked([sys.executable, str(validator / "audit_case.py"), str(economics_project)])
            if tampered_result.returncode == 0 or "LTV:CAC does not reconcile" not in tampered_result.stdout:
                fail("Validator did not reject tampered LTV:CAC output", errors)

            cfo_script = finance / "scripts" / "cfo_operating_plan.py"
            cfo_example = finance / "assets" / "cfo-operating-plan-input.example.json"
            cfo_output = json.loads(run([sys.executable, str(cfo_script), str(cfo_example)]).stdout)
            if cfo_output["summary"]["ending_cash"] != 211230.0 or cfo_output["summary"]["ending_accounts_receivable"] != 45250.0:
                fail("CFO operating-plan smoke test returned unexpected cash or AR", errors)
            if not all(result.get("pass") for result in cfo_output.get("decision_threshold_results", [])):
                fail("CFO operating-plan example did not pass its decision thresholds", errors)
            invalid_cfo = json.loads(cfo_example.read_text(encoding="utf-8"))
            invalid_cfo["cohorts"][0]["retention_rates"][2] = 0.95
            invalid_cfo_path = temp_path / "invalid-cfo.json"
            invalid_cfo_path.write_text(json.dumps(invalid_cfo), encoding="utf-8")
            invalid_cfo_result = run_unchecked([sys.executable, str(cfo_script), str(invalid_cfo_path)])
            if invalid_cfo_result.returncode == 0 or "retention cannot increase" not in invalid_cfo_result.stderr:
                fail("CFO operating-plan regression did not reject increasing retention", errors)
            cfo_project = temp_path / "cfo-project"
            shutil.copytree(fixture, cfo_project)
            linked_cfo = replace_fixture_ids(json.loads(cfo_example.read_text(encoding="utf-8")))
            linked_cfo_path = temp_path / "linked-cfo.json"
            linked_cfo_path.write_text(json.dumps(linked_cfo), encoding="utf-8")
            run([sys.executable, str(cfo_script), str(linked_cfo_path), "--output", str(cfo_project / "15-cfo-operating-plan.json")])
            run([sys.executable, str(validator / "audit_case.py"), str(cfo_project), "--strict"])
            tampered_cfo = json.loads((cfo_project / "15-cfo-operating-plan.json").read_text(encoding="utf-8"))
            tampered_cfo["periods"][0]["ending_cash"] = 999999
            (cfo_project / "15-cfo-operating-plan.json").write_text(json.dumps(tampered_cfo), encoding="utf-8")
            tampered_cfo_result = run_unchecked([sys.executable, str(validator / "audit_case.py"), str(cfo_project)])
            if tampered_cfo_result.returncode == 0 or "period 1 ending cash does not reconcile" not in tampered_cfo_result.stdout:
                fail("Validator did not reject tampered CFO operating-plan output", errors)
        result = run(
            [
                sys.executable,
                str(finance / "scripts" / "forecast.py"),
                str(finance / "assets" / "forecast-input.example.json"),
            ]
        )
        output = json.loads(result.stdout)
        if set(output.get("scenarios", {})) != {"low", "base", "high"}:
            fail("Finance smoke test did not return low/base/high scenarios", errors)
        routed = run([sys.executable, str(finance / "scripts" / "model_router.py"), str(finance / "assets" / "model-input.example.json")])
        routed_output = json.loads(routed.stdout)
        if routed_output.get("model_type") != "subscription" or set(routed_output.get("scenarios", {})) != {"low", "base", "high"}:
            fail("Finance model-router smoke test returned an invalid result", errors)
        sensitivity = run([sys.executable, str(finance / "scripts" / "sensitivity.py"), str(finance / "assets" / "model-input.example.json"), "--top", "3"])
        sensitivity_output = json.loads(sensitivity.stdout)
        if len(sensitivity_output.get("ranked_drivers", [])) != 3:
            fail("Finance sensitivity smoke test did not return the requested driver count", errors)
        run([sys.executable, str(validator / "audit_case.py"), str(fixture), "--strict"])
        run([sys.executable, str(validator / "check_sources.py"), str(fixture)])
        rubric = run([sys.executable, str(validator / "score_rubric.py"), str(fixture / "11-rubric-scorecard.csv")])
        if "80.0/100" not in rubric.stdout:
            fail("Rubric scoring smoke test returned an unexpected score", errors)
    except (subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        details = getattr(exc, "stderr", "") or getattr(exc, "stdout", "")
        fail(f"Smoke test failed: {exc}; {details}", errors)


def main():
    errors = []
    manifest = json.loads((ROOT / "casekit.json").read_text(encoding="utf-8"))
    if manifest.get("format", {}).get("standard") != "Agent Skills":
        fail("Manifest does not declare the Agent Skills portability standard", errors)
    required_clients = {"codex", "claude-code", "gemini-cli", "google-antigravity"}
    if set(manifest.get("native_clients", {})) != required_clients:
        fail("Manifest native client compatibility matrix is incomplete", errors)
    expected = set(manifest.get("skills", []))
    actual = {path.name for path in SKILLS.glob("casekit-*") if path.is_dir()}
    if expected != actual:
        fail(f"Manifest skills differ from filesystem: expected={sorted(expected)} actual={sorted(actual)}", errors)
    for skill in sorted(SKILLS.glob("casekit-*")):
        validate_skill(skill, errors)
    smoke_tests(errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"CaseKit validation failed with {len(errors)} error(s)")
        raise SystemExit(1)
    print(f"CaseKit {manifest.get('version')} valid: {len(actual)} skills and all smoke tests passed")


if __name__ == "__main__":
    main()
