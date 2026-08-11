# Agent guidance

Treat CaseKit as a coordinated, provider-neutral Agent Skills suite, not a collection of independent prompts.

- Preserve `casekit-orchestrator` as the owner of workflow and shared ledgers.
- Preserve stable Claim, Source, Assumption, Metric, Decision, Risk, and Experiment IDs.
- Keep case facts separate from methodology references.
- Do not add unsourced benchmarks to templates.
- Run `python3 scripts/validate_suite.py` after skill or script changes.
- Add both a passing fixture and a failing regression whenever a new deterministic gate is introduced.
- Keep live URL checks opt-in; CI must validate metadata and citation discipline without depending on third-party uptime.
- Keep `skills/` canonical. Do not maintain divergent Claude, Codex, Gemini, or Antigravity prompt copies; install identical skills through adapters.
- Keep provider-specific metadata optional so clients that implement only the Agent Skills standard can ignore it safely.
- Do not vendor gstack or startup-skill into this repository. Integrate through documented handoffs or original CaseKit adaptations.
