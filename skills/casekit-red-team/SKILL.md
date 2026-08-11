---
name: casekit-red-team
description: Adversarially review a case competition or hackathon submission against its judging rubric, evidence, logic, financial model, feasibility, differentiation, slide deck, demo, and Q&A. Use before submission, rehearsal, or major strategy lock to find contradictions, unsupported claims, fragile assumptions, double counting, feasibility gaps, and high-impact fixes.
---

# CaseKit Red Team

Attack the case as a skeptical judge, then prioritize repairs by score impact and time.

## Review order

1. Reconstruct the case using only slide headlines and visible evidence.
2. Score each official rubric criterion independently before reading team rationale.
3. Trace every major number to formula, unit, period, Assumption IDs, and Source IDs.
4. Test problem evidence, strategic choice, differentiation, economics, operational/technical feasibility, GTM volume, risk, demo, and delivery.
5. Search for contradictions across deck, script, model, prototype, and ledgers.
6. Generate judge questions and classify as fatal, major, moderate, or polish.
7. Recommend the smallest fix that produces the largest expected score gain.
8. For coded demos, run or request report-only functional/UX QA and security/privacy review when material; map findings to Risks and acceptance checks.

Read `references/attack-checklist.md`. Use `assets/red-team-report.md`.

## Rules

- Separate missing evidence from weak reasoning and from poor communication.
- Do not reward effort that judges cannot observe.
- Do not rewrite the whole case when a focused correction works.
- Mark fatal issues: wrong answer to brief, impossible economics, fabricated evidence, unsafe claim, demo dependency without fallback, or numbers that cannot reconcile.
- Re-score after fixes and state residual uncertainty.

## Output

Provide rubric score, executive verdict, contradiction table, financial stress test, feasibility attacks, top judge questions with strong answer structure, prioritized repair queue, rehearsal drills, go/no-go checklist, and CaseKit handoff.

Do not require external QA tooling. When gstack is installed, its report-only QA and specialist reviews may provide additional evidence; keep remediation decisions inside CaseKit.
