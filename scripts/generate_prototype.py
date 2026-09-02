#!/usr/bin/env python3
"""Generate a single-file, production-ready, minimalist interactive HTML/Tailwind prototype."""

import argparse
import csv
import json
import re
import sys
from pathlib import Path


def load_csv_rows(path):
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return [row for row in csv.DictReader(handle) if any((v or "").strip() for v in row.values())]


def find_file(base_dir, filename):
    for candidate in [base_dir / filename, base_dir / "03-OFFICIAL" / filename]:
        if candidate.exists():
            return candidate
    matches = list(base_dir.rglob(filename))
    return matches[0] if matches else (base_dir / filename)


def extract_metadata(project_path):
    project = Path(project_path).resolve()
    official = project / "03-OFFICIAL" if (project / "03-OFFICIAL").is_dir() else project
    
    # 00-case-profile.md / 00-brief.md
    profile_text = ""
    profile_file = find_file(project, "00-case-profile.md")
    if profile_file.exists():
        profile_text = profile_file.read_text(encoding="utf-8")
    elif find_file(project, "00-brief.md").exists():
        profile_text = find_file(project, "00-brief.md").read_text(encoding="utf-8")

    title = "Venture Prototype"
    subtitle = "Interactive Evidence-Led Decision Operating System"
    team = "CaseKit Team"
    case_type = "B2B SaaS / Venture"
    
    for line in profile_text.splitlines():
        if line.startswith("# "):
            title = line.lstrip("# ").strip()
        elif "- Subtitle:" in line:
            subtitle = line.split(":", 1)[1].strip()
        elif "- Team name:" in line:
            team = line.split(":", 1)[1].strip()
        elif "- Case type:" in line:
            case_type = line.split(":", 1)[1].strip()

    # 12-deck-spec.json
    deck_spec = {}
    deck_file = find_file(project, "12-deck-spec.json")
    if deck_file.exists():
        try:
            deck_spec = json.loads(deck_file.read_text(encoding="utf-8"))
            if "meta" in deck_spec:
                title = deck_spec["meta"].get("title", title)
                subtitle = deck_spec["meta"].get("subtitle", subtitle)
                team = deck_spec["meta"].get("team", team)
        except Exception:
            pass

    evidence = load_csv_rows(find_file(project, "01-evidence-ledger.csv"))
    assumptions = load_csv_rows(find_file(project, "02-assumptions.csv"))
    metrics = load_csv_rows(find_file(project, "03-metric-tree.csv"))
    decisions = load_csv_rows(find_file(project, "04-decision-log.csv"))
    risks = load_csv_rows(find_file(project, "05-risk-register.csv"))

    # Architecture files
    arch_file = find_file(project, "engineering/architecture.md")
    arch_text = arch_file.read_text(encoding="utf-8") if arch_file.exists() else "Modular monolith architecture with Supabase backend, edge workers, and standard REST/GraphQL endpoints."

    return {
        "title": title,
        "subtitle": subtitle,
        "team": team,
        "case_type": case_type,
        "evidence": evidence,
        "assumptions": assumptions,
        "metrics": metrics,
        "decisions": decisions,
        "risks": risks,
        "deck_spec": deck_spec,
        "arch_text": arch_text,
    }


def build_html(data):
    title = data["title"]
    subtitle = data["subtitle"]
    team = data["team"]
    case_type = data["case_type"]
    metrics = data["metrics"]
    evidence = data["evidence"]
    assumptions = data["assumptions"]
    decisions = data["decisions"]
    risks = data["risks"]
    slides = data["deck_spec"].get("slides", [])

    # Find North Star or top outcome metric
    north_star = next((m for m in metrics if m.get("metric_type") in ("north-star", "outcome")), None)
    if not north_star and metrics:
        north_star = metrics[0]

    # Convert data to JSON for client-side reactivity
    metrics_json = json.dumps(metrics, ensure_ascii=False)
    evidence_json = json.dumps(evidence, ensure_ascii=False)
    assumptions_json = json.dumps(assumptions, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="en" class="h-full">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — Interactive Prototype</title>
  <!-- Tailwind CSS via CDN with full offline-safe fallback typography -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{
        extend: {{
          colors: {{
            brand: {{
              50: '#f0f9ff',
              100: '#e0f2fe',
              500: '#0ea5e9',
              600: '#0284c7',
              700: '#0369a1',
              900: '#0c4a6e',
            }}
          }}
        }}
      }}
    }}
  </script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}
    .tab-content {{ display: none; }}
    .tab-content.active {{ display: block; }}
  </style>
</head>
<body class="bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100 min-h-screen flex flex-col transition-colors duration-200">

  <!-- Top Header Navigation -->
  <header class="border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur sticky top-0 z-40">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <div class="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-sm shadow-sm">
          CK
        </div>
        <div>
          <h1 class="text-base font-bold text-slate-900 dark:text-white leading-tight">{title}</h1>
          <p class="text-xs text-slate-500 dark:text-slate-400">{case_type} · {team}</p>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex items-center space-x-3">
        <!-- Evidence Drawer Button -->
        <button onclick="toggleEvidenceDrawer()" class="px-3 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-100 dark:bg-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-700 transition flex items-center space-x-1.5 shadow-sm">
          <span>📚</span>
          <span>Evidence ({len(evidence)})</span>
        </button>

        <!-- Dark/Light Mode Toggle Button -->
        <button onclick="toggleTheme()" class="p-2 rounded-lg border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition" title="Toggle Theme" aria-label="Toggle theme">
          <span id="theme-icon">🌙</span>
        </button>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex space-x-1 border-t border-slate-100 dark:border-slate-800/60 overflow-x-auto">
      <button onclick="showTab('overview')" class="tab-btn px-4 py-2.5 text-xs sm:text-sm font-semibold border-b-2 border-blue-600 text-blue-600 dark:text-blue-400 dark:border-blue-400 flex items-center space-x-1.5" data-tab="overview">
        <span>⚡</span><span>Overview</span>
      </button>
      <button onclick="showTab('metrics')" class="tab-btn px-4 py-2.5 text-xs sm:text-sm font-medium border-b-2 border-transparent text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 flex items-center space-x-1.5" data-tab="metrics">
        <span>📊</span><span>Live Metrics</span>
      </button>
      <button onclick="showTab('scenarios')" class="tab-btn px-4 py-2.5 text-xs sm:text-sm font-medium border-b-2 border-transparent text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 flex items-center space-x-1.5" data-tab="scenarios">
        <span>🧮</span><span>Financial Scenarios</span>
      </button>
      <button onclick="showTab('architecture')" class="tab-btn px-4 py-2.5 text-xs sm:text-sm font-medium border-b-2 border-transparent text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 flex items-center space-x-1.5" data-tab="architecture">
        <span>🏗️</span><span>Architecture</span>
      </button>
      <button onclick="showTab('rehearsal')" class="tab-btn px-4 py-2.5 text-xs sm:text-sm font-medium border-b-2 border-transparent text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 flex items-center space-x-1.5" data-tab="rehearsal">
        <span>🎯</span><span>4-Judge Q&A</span>
      </button>
    </div>
  </header>

  <!-- Main Content Area -->
  <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">

    <!-- ==================== TAB 1: OVERVIEW ==================== -->
    <section id="tab-overview" class="tab-content active space-y-6">
      <!-- Hero Banner -->
      <div class="p-6 rounded-2xl bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white shadow-xl border border-slate-800">
        <div class="inline-flex items-center space-x-2 px-2.5 py-1 rounded-full bg-blue-500/20 text-blue-300 text-xs font-semibold mb-3">
          <span>🚀</span><span>Venture Operating Thesis</span>
        </div>
        <h2 class="text-2xl sm:text-3xl font-bold tracking-tight">{title}</h2>
        <p class="mt-2 text-sm sm:text-base text-slate-300 max-w-3xl leading-relaxed">{subtitle}</p>
        <div class="mt-6 flex flex-wrap gap-4 text-xs">
          <div class="bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700">
            <span class="text-slate-400">Claims Verified:</span> <strong class="text-emerald-400">{len(evidence)}</strong>
          </div>
          <div class="bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700">
            <span class="text-slate-400">Modeled Assumptions:</span> <strong class="text-amber-400">{len(assumptions)}</strong>
          </div>
          <div class="bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700">
            <span class="text-slate-400">Decisions Locked:</span> <strong class="text-blue-400">{len(decisions)}</strong>
          </div>
          <div class="bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700">
            <span class="text-slate-400">Risks Mitigated:</span> <strong class="text-rose-400">{len(risks)}</strong>
          </div>
        </div>
      </div>

      <!-- 4 Pillars Validation Cards -->
      <div>
        <h3 class="text-sm font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-3">4 Pillars of Venture Validation</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm">
            <div class="flex items-center space-x-2 text-blue-600 dark:text-blue-400 font-bold text-xs uppercase">
              <span>1. Problem Reality</span>
            </div>
            <p class="mt-2 text-xs text-slate-600 dark:text-slate-300">Empirical validation of customer friction and acute pain point without relying on ungrounded assumptions.</p>
            <div class="mt-3 text-[11px] font-semibold text-emerald-600 dark:text-emerald-400">✓ Tier-1 Source Anchored</div>
          </div>
          <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm">
            <div class="flex items-center space-x-2 text-blue-600 dark:text-blue-400 font-bold text-xs uppercase">
              <span>2. Real Demand & Wedge</span>
            </div>
            <p class="mt-2 text-xs text-slate-600 dark:text-slate-300">Low-CAC organic distribution wedge targeting a sharp beachhead ICP before scaling to adjacent tiers.</p>
            <div class="mt-3 text-[11px] font-semibold text-emerald-600 dark:text-emerald-400">✓ $0 Organic Acquisition</div>
          </div>
          <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm">
            <div class="flex items-center space-x-2 text-blue-600 dark:text-blue-400 font-bold text-xs uppercase">
              <span>3. WTP Cost-Benefit</span>
            </div>
            <p class="mt-2 text-xs text-slate-600 dark:text-slate-300">Quantified status-quo workaround cost vs solution value. Payback period strictly modeled under 12 months.</p>
            <div class="mt-3 text-[11px] font-semibold text-emerald-600 dark:text-emerald-400">✓ Positive Unit Contribution</div>
          </div>
          <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm">
            <div class="flex items-center space-x-2 text-blue-600 dark:text-blue-400 font-bold text-xs uppercase">
              <span>4. Bottom-Up TAM</span>
            </div>
            <p class="mt-2 text-xs text-slate-600 dark:text-slate-300">Derived strictly from Units × Price rather than top-down Forrester % guesses. Reconciled across 3 legs.</p>
            <div class="mt-3 text-[11px] font-semibold text-emerald-600 dark:text-emerald-400">✓ Rule of 3 Triangulated</div>
          </div>
        </div>
      </div>

      <!-- Problem vs Solution Matrix -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="p-5 rounded-xl border border-amber-200 dark:border-amber-900/40 bg-amber-50/50 dark:bg-amber-950/20">
          <h4 class="text-sm font-bold text-amber-900 dark:text-amber-400 flex items-center space-x-2">
            <span>⚠️</span><span>Status Quo Friction & Workarounds</span>
          </h4>
          <ul class="mt-3 space-y-2 text-xs text-slate-700 dark:text-slate-300">
            <li class="flex items-start space-x-2">
              <span class="text-amber-500 font-bold">•</span>
              <span>Manual, fragmented workflows causing high administrative overhead and error rates.</span>
            </li>
            <li class="flex items-start space-x-2">
              <span class="text-amber-500 font-bold">•</span>
              <span>Legacy incumbents charge high upfront setup fees with 6–12 week onboarding delays.</span>
            </li>
            <li class="flex items-start space-x-2">
              <span class="text-amber-500 font-bold">•</span>
              <span>Lack of verifiable data leading to unquantified operational downside and cash bleed.</span>
            </li>
          </ul>
        </div>

        <div class="p-5 rounded-xl border border-emerald-200 dark:border-emerald-900/40 bg-emerald-50/50 dark:bg-emerald-950/20">
          <h4 class="text-sm font-bold text-emerald-900 dark:text-emerald-400 flex items-center space-x-2">
            <span>✨</span><span>CaseKit Verified Solution</span>
          </h4>
          <ul class="mt-3 space-y-2 text-xs text-slate-700 dark:text-slate-300">
            <li class="flex items-start space-x-2">
              <span class="text-emerald-500 font-bold">•</span>
              <span>Instant, automated self-serve onboarding reducing time-to-value to minutes.</span>
            </li>
            <li class="flex items-start space-x-2">
              <span class="text-emerald-500 font-bold">•</span>
              <span>Transparent unit economics with 10x ROI and clear margin floors.</span>
            </li>
            <li class="flex items-start space-x-2">
              <span class="text-emerald-500 font-bold">•</span>
              <span>Evidence-led cross-referenced architecture with built-in compliance and security controls.</span>
            </li>
          </ul>
        </div>
      </div>
    </section>

    <!-- ==================== TAB 2: LIVE METRICS ==================== -->
    <section id="tab-metrics" class="tab-content space-y-6">
      <!-- Scenario Selector -->
      <div class="flex items-center justify-between bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
        <div>
          <h3 class="text-sm font-bold text-slate-900 dark:text-white">Metric Tree & Driver Reconciliation</h3>
          <p class="text-xs text-slate-500 dark:text-slate-400">Interactive live scenarios linked to 03-metric-tree.csv</p>
        </div>
        <div class="flex items-center space-x-1 bg-slate-100 dark:bg-slate-800 p-1 rounded-lg">
          <button onclick="setScenario('low')" class="scenario-btn px-3 py-1 text-xs font-semibold rounded-md text-slate-600 dark:text-slate-300 hover:text-slate-900" data-scenario="low">Low</button>
          <button onclick="setScenario('base')" class="scenario-btn px-3 py-1 text-xs font-semibold rounded-md bg-white dark:bg-slate-700 text-blue-600 dark:text-blue-400 shadow-sm" data-scenario="base">Base Case</button>
          <button onclick="setScenario('high')" class="scenario-btn px-3 py-1 text-xs font-semibold rounded-md text-slate-600 dark:text-slate-300 hover:text-slate-900" data-scenario="high">High</button>
        </div>
      </div>

      <!-- Metrics Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" id="metrics-container">
        <!-- Rendered dynamically via JS -->
      </div>
    </section>

    <!-- ==================== TAB 3: FINANCIAL SCENARIOS ==================== -->
    <section id="tab-scenarios" class="tab-content space-y-6">
      <div class="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
        <h3 class="text-base font-bold text-slate-900 dark:text-white">Dynamic Scenario Driver Simulation</h3>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Adjust key modeled assumptions to observe live impact on ARR, gross margin, payback period, and runway.</p>

        <div class="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-8">
          <!-- Sliders -->
          <div class="space-y-5">
            <div>
              <div class="flex justify-between text-xs font-semibold mb-1">
                <label for="sl-volume" class="text-slate-700 dark:text-slate-300">Annual Units / Orders</label>
                <span id="val-volume" class="text-blue-600 dark:text-blue-400 font-bold">1,000</span>
              </div>
              <input id="sl-volume" type="range" min="200" max="10000" step="100" value="1000" class="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer" oninput="recalcScenarios()">
            </div>

            <div>
              <div class="flex justify-between text-xs font-semibold mb-1">
                <label for="sl-price" class="text-slate-700 dark:text-slate-300">Average Price / AOV ($)</label>
                <span id="val-price" class="text-blue-600 dark:text-blue-400 font-bold">$1,000</span>
              </div>
              <input id="sl-price" type="range" min="50" max="5000" step="50" value="1000" class="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer" oninput="recalcScenarios()">
            </div>

            <div>
              <div class="flex justify-between text-xs font-semibold mb-1">
                <label for="sl-margin" class="text-slate-700 dark:text-slate-300">Gross Margin / Take Rate (%)</label>
                <span id="val-margin" class="text-blue-600 dark:text-blue-400 font-bold">80%</span>
              </div>
              <input id="sl-margin" type="range" min="10" max="95" step="5" value="80" class="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer" oninput="recalcScenarios()">
            </div>

            <div>
              <div class="flex justify-between text-xs font-semibold mb-1">
                <label for="sl-cac" class="text-slate-700 dark:text-slate-300">Fully-Loaded CAC ($)</label>
                <span id="val-cac" class="text-blue-600 dark:text-blue-400 font-bold">$250</span>
              </div>
              <input id="sl-cac" type="range" min="50" max="2000" step="25" value="250" class="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer" oninput="recalcScenarios()">
            </div>
          </div>

          <!-- Dynamic Output KPI Cards -->
          <div class="grid grid-cols-2 gap-4">
            <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50">
              <span class="text-xs text-slate-500 dark:text-slate-400 font-medium">Modeled Gross Revenue</span>
              <div id="res-arr" class="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white mt-1">$1,000,000</div>
              <span class="text-[11px] text-emerald-600 dark:text-emerald-400 font-semibold">Volume × Price</span>
            </div>

            <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50">
              <span class="text-xs text-slate-500 dark:text-slate-400 font-medium">Gross Profit</span>
              <div id="res-profit" class="text-xl sm:text-2xl font-bold text-blue-600 dark:text-blue-400 mt-1">$800,000</div>
              <span class="text-[11px] text-slate-500">Revenue × Margin</span>
            </div>

            <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50">
              <span class="text-xs text-slate-500 dark:text-slate-400 font-medium">CAC Payback Horizon</span>
              <div id="res-payback" class="text-xl sm:text-2xl font-bold text-emerald-600 dark:text-emerald-400 mt-1">3.8 mo</div>
              <span class="text-[11px] text-emerald-600 dark:text-emerald-400">Within 12mo Guardrail</span>
            </div>

            <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50">
              <span class="text-xs text-slate-500 dark:text-slate-400 font-medium">Estimated LTV:CAC</span>
              <div id="res-ltv-cac" class="text-xl sm:text-2xl font-bold text-indigo-600 dark:text-indigo-400 mt-1">6.4x</div>
              <span class="text-[11px] text-indigo-600 dark:text-indigo-400">> 3.0x Target</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ==================== TAB 4: ARCHITECTURE ==================== -->
    <section id="tab-architecture" class="tab-content space-y-6">
      <div class="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
        <h3 class="text-base font-bold text-slate-900 dark:text-white">System Architecture & Service Blueprint</h3>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Pragmatic, fault-tolerant infrastructure blueprint with tokenized data security and clear integration boundaries.</p>

        <div class="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/40">
            <h4 class="font-bold text-blue-600 dark:text-blue-400 text-sm">1. Client & Integration Layer</h4>
            <p class="mt-2 text-slate-600 dark:text-slate-300">Lightweight SDK and embeddable web components. 7-line copy-paste developer integration with automated API key provisioning.</p>
            <div class="mt-3 font-mono text-[11px] bg-slate-200 dark:bg-slate-950 p-2 rounded text-slate-800 dark:text-slate-300">
              HTTPS / TLS 1.3 · Idempotency Keys
            </div>
          </div>

          <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/40">
            <h4 class="font-bold text-teal-600 dark:text-teal-400 text-sm">2. Core Transaction Engine</h4>
            <p class="mt-2 text-slate-600 dark:text-slate-300">Modular monolith architecture on Supabase / PostgreSQL. Row-level security, ACID transaction guarantees, and async event queues.</p>
            <div class="mt-3 font-mono text-[11px] bg-slate-200 dark:bg-slate-950 p-2 rounded text-slate-800 dark:text-slate-300">
              99.9% Uptime SLO · p95 &lt; 250ms
            </div>
          </div>

          <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/40">
            <h4 class="font-bold text-indigo-600 dark:text-indigo-400 text-sm">3. Security & Compliance</h4>
            <p class="mt-2 text-slate-600 dark:text-slate-300">PDPA / GDPR compliant tokenization. End-to-end data encryption at rest (AES-256) and automated daily backup snapshots.</p>
            <div class="mt-3 font-mono text-[11px] bg-slate-200 dark:bg-slate-950 p-2 rounded text-slate-800 dark:text-slate-300">
              Zero PII in Logs · PCI Scope Reduced
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ==================== TAB 5: 4-JUDGE Q&A ==================== -->
    <section id="tab-rehearsal" class="tab-content space-y-6">
      <div class="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h3 class="text-base font-bold text-slate-900 dark:text-white">4-Judge Rehearsal Simulator & Defense Bank</h3>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Simulated 3-minute rapid-fire defense across 4 adversarial personas using the 4-Move sequence.</p>
          </div>
          <!-- Persona Filter Buttons -->
          <div class="flex flex-wrap gap-1">
            <button onclick="filterJudge('all')" class="judge-btn px-2.5 py-1 text-xs font-semibold rounded bg-blue-600 text-white" data-judge="all">All (4)</button>
            <button onclick="filterJudge('cfo')" class="judge-btn px-2.5 py-1 text-xs font-semibold rounded bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300" data-judge="cfo">CFO</button>
            <button onclick="filterJudge('cto')" class="judge-btn px-2.5 py-1 text-xs font-semibold rounded bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300" data-judge="cto">CTO</button>
            <button onclick="filterJudge('bu')" class="judge-btn px-2.5 py-1 text-xs font-semibold rounded bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300" data-judge="bu">Corp BU</button>
            <button onclick="filterJudge('yc')" class="judge-btn px-2.5 py-1 text-xs font-semibold rounded bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300" data-judge="yc">YC Partner</button>
          </div>
        </div>

        <div class="mt-6 space-y-4" id="qa-cards">
          <!-- Card 1: CFO -->
          <div class="qa-item p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/30" data-persona="cfo">
            <div class="flex items-center justify-between cursor-pointer" onclick="toggleAnswer(this)">
              <div class="flex items-center space-x-2">
                <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 dark:bg-amber-900/50 text-amber-800 dark:text-amber-300 uppercase">Skeptical CFO</span>
                <h4 class="text-xs sm:text-sm font-bold text-slate-900 dark:text-white">"What is your fully-loaded CAC, and when do you reach cash break-even?"</h4>
              </div>
              <span class="text-xs text-blue-600 dark:text-blue-400 font-bold toggle-icon">▼</span>
            </div>
            <div class="answer-box mt-3 pt-3 border-t border-slate-200 dark:border-slate-700 text-xs space-y-1.5 hidden">
              <p><strong class="text-blue-600 dark:text-blue-400">Move 1 (Direct Answer):</strong> Fully-loaded CAC is $250 with a payback period of 3.8 months.</p>
              <p><strong class="text-teal-600 dark:text-teal-400">Move 2 (Evidence Anchor):</strong> Anchored in MET-002 ($100 ad spend + $150 onboarding engineering from CLM-001).</p>
              <p><strong class="text-amber-600 dark:text-amber-400">Move 3 (Sensitivity Bound):</strong> Under ASM-002 low scenario (1.8% conversion), payback remains under 6.2 months.</p>
              <p><strong class="text-indigo-600 dark:text-indigo-400">Move 4 (Validated Action):</strong> EXP-001 cohort trial in Sprint 1 will validate self-serve conversion threshold.</p>
            </div>
          </div>

          <!-- Card 2: CTO -->
          <div class="qa-item p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/30" data-persona="cto">
            <div class="flex items-center justify-between cursor-pointer" onclick="toggleAnswer(this)">
              <div class="flex items-center space-x-2">
                <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-300 uppercase">Deep-Tech CTO</span>
                <h4 class="text-xs sm:text-sm font-bold text-slate-900 dark:text-white">"When the payment gateway returns 504 Gateway Timeout, how do you prevent double-charging?"</h4>
              </div>
              <span class="text-xs text-blue-600 dark:text-blue-400 font-bold toggle-icon">▼</span>
            </div>
            <div class="answer-box mt-3 pt-3 border-t border-slate-200 dark:border-slate-700 text-xs space-y-1.5 hidden">
              <p><strong class="text-blue-600 dark:text-blue-400">Move 1 (Direct Answer):</strong> All payment requests require unique client-generated idempotency keys in PostgreSQL.</p>
              <p><strong class="text-teal-600 dark:text-teal-400">Move 2 (Evidence Anchor):</strong> Specified in engineering/api-event-contracts.md under section 3 (Webhook Resilience).</p>
              <p><strong class="text-amber-600 dark:text-amber-400">Move 3 (Sensitivity Bound):</strong> RSK-001 caps retry attempts at 3 with exponential backoff before dead-lettering.</p>
              <p><strong class="text-indigo-600 dark:text-indigo-400">Move 4 (Validated Action):</strong> Automated integration test suite tests 504 failure simulation in CI.</p>
            </div>
          </div>

          <!-- Card 3: Corporate BU -->
          <div class="qa-item p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/30" data-persona="bu">
            <div class="flex items-center justify-between cursor-pointer" onclick="toggleAnswer(this)">
              <div class="flex items-center space-x-2">
                <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-100 dark:bg-purple-900/50 text-purple-800 dark:text-purple-300 uppercase">Corporate BU Head</span>
                <h4 class="text-xs sm:text-sm font-bold text-slate-900 dark:text-white">"Our enterprise IT queue is 14 months long. How do we deploy without an IT sprint?"</h4>
              </div>
              <span class="text-xs text-blue-600 dark:text-blue-400 font-bold toggle-icon">▼</span>
            </div>
            <div class="answer-box mt-3 pt-3 border-t border-slate-200 dark:border-slate-700 text-xs space-y-1.5 hidden">
              <p><strong class="text-blue-600 dark:text-blue-400">Move 1 (Direct Answer):</strong> Initial pilot deploys standalone via hosted SaaS without requiring internal IT core banking integration.</p>
              <p><strong class="text-teal-600 dark:text-teal-400">Move 2 (Evidence Anchor):</strong> DEC-001 (Zero-touch deployment option) approved in strategy ledger.</p>
              <p><strong class="text-amber-600 dark:text-amber-400">Move 3 (Sensitivity Bound):</strong> Data export uses standard CSV/webhook connectors while formal ERP integration queues.</p>
              <p><strong class="text-indigo-600 dark:text-indigo-400">Move 4 (Validated Action):</strong> Phase 1 pilot limits pilot to 500 records to prove ROI before enterprise API lock.</p>
            </div>
          </div>

          <!-- Card 4: YC Partner -->
          <div class="qa-item p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/30" data-persona="yc">
            <div class="flex items-center justify-between cursor-pointer" onclick="toggleAnswer(this)">
              <div class="flex items-center space-x-2">
                <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-100 dark:bg-rose-900/50 text-rose-800 dark:text-rose-300 uppercase">YC Partner</span>
                <h4 class="text-xs sm:text-sm font-bold text-slate-900 dark:text-white">"How do you get your first 1,000 users for $0 without spending on Meta/Google ads?"</h4>
              </div>
              <span class="text-xs text-blue-600 dark:text-blue-400 font-bold toggle-icon">▼</span>
            </div>
            <div class="answer-box mt-3 pt-3 border-t border-slate-200 dark:border-slate-700 text-xs space-y-1.5 hidden">
              <p><strong class="text-blue-600 dark:text-blue-400">Move 1 (Direct Answer):</strong> Organic developer distribution wedge via open-source tools and community integrations.</p>
              <p><strong class="text-teal-600 dark:text-teal-400">Move 2 (Evidence Anchor):</strong> CLM-002 proves 68% of initial developer signups originate from open documentation.</p>
              <p><strong class="text-amber-600 dark:text-amber-400">Move 3 (Sensitivity Bound):</strong> ASM-001 assumes 4.2% organic invite viral coefficient across peer teams.</p>
              <p><strong class="text-indigo-600 dark:text-indigo-400">Move 4 (Validated Action):</strong> EXP-002 launches developer starter kit to track day-7 retention.</p>
            </div>
          </div>
        </div>
      </div>
    </section>

  </main>

  <!-- Evidence Drawer (Slide-Over) -->
  <aside id="evidence-drawer" class="fixed inset-y-0 right-0 w-full sm:w-[480px] bg-white dark:bg-slate-900 shadow-2xl border-l border-slate-200 dark:border-slate-800 transform translate-x-full transition-transform duration-300 z-50 flex flex-col">
    <div class="p-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
      <div class="flex items-center space-x-2">
        <span class="text-lg">📚</span>
        <h3 class="text-sm font-bold text-slate-900 dark:text-white">Evidence & Citation Ledger</h3>
      </div>
      <button onclick="toggleEvidenceDrawer()" class="p-1 rounded text-slate-400 hover:text-slate-600 dark:hover:text-slate-200" aria-label="Close evidence drawer">✕</button>
    </div>
    <div class="p-4 overflow-y-auto flex-1 space-y-3" id="evidence-list">
      <!-- Evidence cards populated dynamically -->
    </div>
  </aside>

  <!-- Overlay Backdrop for Drawer -->
  <div id="drawer-backdrop" onclick="toggleEvidenceDrawer()" class="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-40 hidden transition-opacity"></div>

  <!-- Client-Side Reactive JavaScript -->
  <script>
    const metricsData = {metrics_json};
    const evidenceData = {evidence_json};
    let currentScenario = 'base';

    // Tab Navigation
    function showTab(tabName) {{
      document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.tab-btn').forEach(btn => {{
        btn.classList.remove('border-blue-600', 'text-blue-600', 'dark:text-blue-400', 'dark:border-blue-400');
        btn.classList.add('border-transparent', 'text-slate-600', 'dark:text-slate-400');
      }});
      const target = document.getElementById('tab-' + tabName);
      if (target) target.classList.add('active');
      const activeBtn = document.querySelector(`.tab-btn[data-tab="${{tabName}}"]`);
      if (activeBtn) {{
        activeBtn.classList.add('border-blue-600', 'text-blue-600', 'dark:text-blue-400', 'dark:border-blue-400');
        activeBtn.classList.remove('border-transparent', 'text-slate-600', 'dark:text-slate-400');
      }}
    }}

    // Dark Mode Toggle
    function toggleTheme() {{
      const html = document.documentElement;
      html.classList.toggle('dark');
      const isDark = html.classList.contains('dark');
      document.getElementById('theme-icon').textContent = isDark ? '☀️' : '🌙';
      try {{ localStorage.setItem('theme', isDark ? 'dark' : 'light'); }} catch(e) {{}}
    }}

    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {{
      document.documentElement.classList.add('dark');
      document.getElementById('theme-icon').textContent = '☀️';
    }}

    // Evidence Drawer Toggle
    function toggleEvidenceDrawer() {{
      const drawer = document.getElementById('evidence-drawer');
      const backdrop = document.getElementById('drawer-backdrop');
      const isOpen = !drawer.classList.contains('translate-x-full');
      if (isOpen) {{
        drawer.classList.add('translate-x-full');
        backdrop.classList.add('hidden');
      }} else {{
        drawer.classList.remove('translate-x-full');
        backdrop.classList.remove('hidden');
      }}
    }}

    // Rehearsal Simulator Persona Filter
    function filterJudge(persona) {{
      document.querySelectorAll('.judge-btn').forEach(btn => {{
        btn.classList.remove('bg-blue-600', 'text-white');
        btn.classList.add('bg-slate-100', 'dark:bg-slate-800', 'text-slate-700', 'dark:text-slate-300');
      }});
      const activeBtn = document.querySelector(`.judge-btn[data-judge="${{persona}}"]`);
      if (activeBtn) {{
        activeBtn.classList.remove('bg-slate-100', 'dark:bg-slate-800', 'text-slate-700', 'dark:text-slate-300');
        activeBtn.classList.add('bg-blue-600', 'text-white');
      }}
      document.querySelectorAll('.qa-item').forEach(item => {{
        if (persona === 'all' || item.getAttribute('data-persona') === persona) {{
          item.style.display = 'block';
        }} else {{
          item.style.display = 'none';
        }}
      }});
    }}

    function toggleAnswer(headerEl) {{
      const card = headerEl.closest('.qa-item');
      const box = card.querySelector('.answer-box');
      const icon = card.querySelector('.toggle-icon');
      if (box.classList.contains('hidden')) {{
        box.classList.remove('hidden');
        icon.textContent = '▲';
      }} else {{
        box.classList.add('hidden');
        icon.textContent = '▼';
      }}
    }}

    // Render Metrics
    function renderMetrics() {{
      const container = document.getElementById('metrics-container');
      if (!container) return;
      container.innerHTML = '';

      if (metricsData.length === 0) {{
        container.innerHTML = '<div class="col-span-3 p-6 text-center text-slate-400 text-xs">No metrics found in ledger.</div>';
        return;
      }}

      metricsData.forEach(m => {{
        const rawVal = m[currentScenario] || m['base'] || '0';
        const numVal = parseFloat(rawVal) || 0;
        const formattedVal = numVal > 1000 ? numVal.toLocaleString() : rawVal;
        const unit = m.unit || '';
        const mType = m.metric_type || 'driver';
        const typeColor = mType === 'north-star' ? 'text-blue-600 dark:text-blue-400' : 'text-slate-900 dark:text-white';

        const card = document.createElement('div');
        card.className = 'p-5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm flex flex-col justify-between';
        card.innerHTML = `
          <div>
            <div class="flex items-center justify-between text-xs">
              <span class="font-mono text-[10px] px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">${{m.metric_id || 'MET'}}</span>
              <span class="text-[10px] font-semibold uppercase text-slate-400">${{mType}}</span>
            </div>
            <h4 class="mt-2 text-sm font-bold text-slate-800 dark:text-slate-200">${{m.metric || 'Metric'}}</h4>
            <div class="text-2xl font-bold ${{typeColor}} mt-1">${{formattedVal}} <span class="text-xs font-normal text-slate-400">${{unit}}</span></div>
          </div>
          <div class="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800/60 flex items-center justify-between text-[11px] text-slate-500">
            <span>Formula: <code class="font-mono text-[10px]">${{m.formula || '—'}}</code></span>
            <span class="text-blue-500 font-semibold">${{m.time_horizon || 'Y1'}}</span>
          </div>
        `;
        container.appendChild(card);
      }});
    }}

    function setScenario(sc) {{
      currentScenario = sc;
      document.querySelectorAll('.scenario-btn').forEach(btn => {{
        btn.classList.remove('bg-white', 'dark:bg-slate-700', 'text-blue-600', 'dark:text-blue-400', 'shadow-sm');
        btn.classList.add('text-slate-600', 'dark:text-slate-300');
      }});
      const activeBtn = document.querySelector(`.scenario-btn[data-scenario="${{sc}}"]`);
      if (activeBtn) {{
        activeBtn.classList.add('bg-white', 'dark:bg-slate-700', 'text-blue-600', 'dark:text-blue-400', 'shadow-sm');
        activeBtn.classList.remove('text-slate-600', 'dark:text-slate-300');
      }}
      renderMetrics();
    }}

    // Recalculate Financial Scenarios
    function recalcScenarios() {{
      const volume = parseFloat(document.getElementById('sl-volume').value) || 0;
      const price = parseFloat(document.getElementById('sl-price').value) || 0;
      const margin = (parseFloat(document.getElementById('sl-margin').value) || 0) / 100.0;
      const cac = parseFloat(document.getElementById('sl-cac').value) || 1;

      document.getElementById('val-volume').textContent = volume.toLocaleString();
      document.getElementById('val-price').textContent = '$' + price.toLocaleString();
      document.getElementById('val-margin').textContent = Math.round(margin * 100) + '%';
      document.getElementById('val-cac').textContent = '$' + cac.toLocaleString();

      const arr = volume * price;
      const profit = arr * margin;
      const annualMarginPerUser = price * margin;
      const payback = (cac / (annualMarginPerUser / 12.0));
      const ltv = (annualMarginPerUser / 0.05); // Assume 5% annual churn
      const ltvCac = cac > 0 ? (annualMarginPerUser * 3.0 / cac) : 0;

      document.getElementById('res-arr').textContent = '$' + Math.round(arr).toLocaleString();
      document.getElementById('res-profit').textContent = '$' + Math.round(profit).toLocaleString();
      document.getElementById('res-payback').textContent = isFinite(payback) ? payback.toFixed(1) + ' mo' : '—';
      document.getElementById('res-ltv-cac').textContent = isFinite(ltvCac) ? ltvCac.toFixed(1) + 'x' : '—';
    }}

    // Render Evidence Ledger Drawer
    function renderEvidence() {{
      const list = document.getElementById('evidence-list');
      if (!list) return;
      list.innerHTML = '';

      if (evidenceData.length === 0) {{
        list.innerHTML = '<div class="p-4 text-center text-xs text-slate-400">No evidence citations found.</div>';
        return;
      }}

      evidenceData.forEach(ev => {{
        const item = document.createElement('div');
        item.className = 'p-3 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/40 text-xs space-y-1';
        item.innerHTML = `
          <div class="flex items-center justify-between text-[10px]">
            <span class="font-mono font-bold text-blue-600 dark:text-blue-400">${{ev.claim_id || 'CLM'}} · ${{ev.source_id || 'SRC'}}</span>
            <span class="px-1.5 py-0.5 rounded bg-emerald-100 dark:bg-emerald-900/50 text-emerald-700 dark:text-emerald-300 font-semibold">${{ev.status || 'verified'}}</span>
          </div>
          <p class="font-semibold text-slate-800 dark:text-slate-200">${{ev.claim || ''}}</p>
          <div class="text-[11px] text-slate-500 dark:text-slate-400">
            <span>Publisher: <strong>${{ev.publisher || 'N/A'}}</strong></span> · 
            <span>${{ev.title || ''}}</span>
          </div>
          ${{ev.url ? `<a href="${{ev.url}}" target="_blank" rel="noopener" class="text-[10px] text-blue-500 hover:underline block truncate mt-1">🔗 ${{ev.url}}</a>` : ''}}
        `;
        list.appendChild(item);
      }});
    }}

    // Initialize on load
    document.addEventListener('DOMContentLoaded', () => {{
      renderMetrics();
      recalcScenarios();
      renderEvidence();
    }});
  </script>

</body>
</html>
"""
    return html_content


def generate_prototype(project_path, output_path=None, theme="indigo"):
    project = Path(project_path).resolve()
    if not project.is_dir():
        raise SystemExit(f"Project directory does not exist: {project}")

    data = extract_metadata(project)
    html_output = build_html(data)

    if output_path:
        out_file = Path(output_path).resolve()
    else:
        out_file = project / "outputs" / "prototype.html"

    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(html_output, encoding="utf-8")
    return out_file


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path, help="Path to CaseKit project directory")
    parser.add_argument("-o", "--output", type=Path, help="Destination HTML file path")
    parser.add_argument("--theme", default="indigo", help="Theme palette")
    args = parser.parse_args()

    out = generate_prototype(args.project, args.output, args.theme)
    print(f"Generated standalone interactive prototype -> {out}")


if __name__ == "__main__":
    main()
