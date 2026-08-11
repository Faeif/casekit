# CaseKit portability

CaseKit uses the open Agent Skills folder format: one directory per skill, a required `SKILL.md` with `name` and `description`, and optional `scripts/`, `references/`, and `assets/`. Provider metadata such as `agents/openai.yaml` is optional and ignored by clients that do not use it.

## Native discovery paths

| Client | Project/workspace | User/global | Notes |
|---|---|---|---|
| OpenAI Codex | `.agents/skills/` | `~/.agents/skills/` | Current interoperable path |
| Claude Code | `.claude/skills/` | `~/.claude/skills/` | Same core format; `/skill-name` can invoke directly |
| Gemini CLI | `.agents/skills/` | `~/.agents/skills/` | `.gemini/skills/` remains a supported provider path |
| Google Antigravity | `.agents/skills/` | `~/.gemini/config/skills/` | `.agent/skills/` remains a legacy workspace path |
| Other Agent Skills clients | `.agents/skills/` | client-dependent | Use `--target` when discovery differs |
| AI without Agent Skills | no automatic discovery | no automatic discovery | Attach the relevant `SKILL.md` and referenced files, or paste the universal invocation below |

## Install patterns

Install for all natively supported clients at user scope:

```bash
python3 install.py
```

Install into a repository for Codex, Gemini CLI, Antigravity, and Claude Code:

```bash
python3 install.py --scope project --project-root /path/to/project
```

Install one adapter:

```bash
python3 install.py --platform claude
python3 install.py --platform codex
python3 install.py --platform gemini
python3 install.py --platform antigravity
```

Install to an arbitrary client directory:

```bash
python3 install.py --target /path/to/client/skills
```

Preview all writes before installation:

```bash
python3 install.py --scope project --project-root /path/to/project --dry-run
```

Legacy adapters are explicit: `legacy-codex`, `legacy-gemini`, and `legacy-antigravity`.

For an AI product that only accepts uploads or pasted context, export one or all skill packages:

```bash
python3 scripts/export_context.py --skill casekit-finance --skill casekit-validator --output casekit-context.md
python3 scripts/export_context.py --all --output casekit-complete-context.md
```

Upload the generated Markdown and then use the universal invocation. The bundle includes textual instructions, references, and text templates; executable helpers remain listed by repository path.

## Universal invocation

When a client has automatic skill discovery, ask:

```text
Use casekit-orchestrator to analyze this brief and coordinate a complete evidence-led, judge-ready case. Use the sibling CaseKit skills when their gates are reached, keep one shared set of IDs and numbers, and run casekit-validator before deck freeze.
```

Provider-specific shortcuts are optional:

- Codex: `$casekit-orchestrator`
- Claude Code: `/casekit-orchestrator`
- Gemini CLI: inspect with `/skills list`; relevant skills activate from the request
- Antigravity: relevant skills activate from the request

## Compatibility boundary

Portable means the methodology, files, scripts, and outputs are provider-neutral. It does not mean every chat product can automatically discover local folders. Clients without Agent Skills support can still use CaseKit by receiving the relevant `SKILL.md` and its referenced resources as context.

Do not maintain separate provider copies in source control. `skills/` is the canonical source; the installer creates synchronized copies at discovery paths.

## Official references

- Agent Skills specification: https://agentskills.io/specification
- Codex skills: https://developers.openai.com/codex/skills/
- Claude Code skills: https://code.claude.com/docs/en/skills
- Gemini CLI Agent Skills: https://geminicli.com/docs/cli/skills/
- Google Antigravity skills: https://antigravity.google/docs/skills
