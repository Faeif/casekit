---
casekit_dashboard: true
---

# 🚀 CaseKit Project Cockpit & Dashboard

> [!TIP] Obsidian No-Code Setup
> If tables do not render below, ensure the **Dataview** community plugin is enabled in Obsidian **Settings -> Community Plugins**.
> To edit tabular ledgers in a spreadsheet view, right-click any `.csv` file and select **Open as CSV Table** (powered by Edit CSV).

## 🎯 Case Overview & 5-Level Funnel
```dataview
TABLE file.mtime AS "Last Modified", case_type AS "Type", stage AS "Stage", beachhead_icp AS "Beachhead ICP"
FROM "00-case-profile.md" or "03-OFFICIAL/00-case-profile.md"
```

---

## 🧪 Active Assumptions & Validation Status
```dataview
TABLE WITHOUT ID
  link(file.path, file.name) AS "Source",
  variable AS "Variable",
  base AS "Base Value",
  confidence AS "Confidence",
  sensitivity AS "Sensitivity",
  status AS "Status"
FROM ""
WHERE contains(file.name, "02-assumptions") or contains(tags, "assumption")
SORT sensitivity DESC
```

---

## 🔍 Evidence Ledger & Triangulation
```dataview
TABLE WITHOUT ID
  claim_id AS "Claim ID",
  claim AS "Claim Statement",
  source_type AS "Source Type",
  quality AS "Quality",
  status AS "Status"
FROM ""
WHERE contains(file.name, "01-evidence-ledger") or contains(tags, "evidence")
SORT quality DESC
```

---

## ⚠️ Risk Register & Mitigation Controls
```dataview
TABLE WITHOUT ID
  risk_id AS "Risk ID",
  risk AS "Risk Description",
  category AS "Category",
  likelihood AS "Likelihood",
  impact AS "Impact",
  mitigation AS "Mitigation",
  status AS "Status"
FROM ""
WHERE contains(file.name, "05-risk-register") or contains(tags, "risk")
SORT impact DESC
```

---

## 📑 Pitch Deck Slide Completion
```dataview
TABLE WITHOUT ID
  slide_id AS "Slide",
  title AS "Slide Title",
  status AS "Status",
  owner AS "Owner"
FROM ""
WHERE contains(tags, "slide") or contains(file.path, "deck")
```
