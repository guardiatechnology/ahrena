# Lexis: Mandatory Consultation of .directives

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** All sessions and activities of AI agents

## Purpose

Ahrena centralizes its canonical configuration in a single declarative file: `.ahrena/.directives`. This file lives in the `.ahrena/` directory — the canonical entry point of the framework in any project — and contains cross-cutting instructions such as default language, required languages, naming conventions, canonical paths, and other directives that govern the behavior of the entire framework.

Without mandatory consultation of this file, agents may make divergent decisions about language, casing, prefixes, and addressing, leading to inconsistency across artifacts and sessions.

This Lexis exists to ensure that **every agent consults and respects the canonical directives** defined in `.ahrena/.directives` before producing any output or artifact.

## Law

> **Every agent MUST read and apply the instructions defined in `.ahrena/.directives` before starting any activity that produces artifacts, documentation, or communication in the Ahrena context.**

## Rules

### 1. Canonical location

The directives file **ALWAYS** resides at:

```
.ahrena/.directives
```

The `.ahrena/` directory is the canonical entry point of the framework in any project that adopts Ahrena. The agent **MUST** look for this directory at the repository root.

### 2. Mandatory read at start

When starting a session or activity, the agent **MUST**:

1. Locate the `.ahrena/` directory at the repository root.
2. Read the `.ahrena/.directives` file in full.
3. Internalize the directives as active constraints for the entire session.

If the `.ahrena/` directory or the `.directives` file does not exist, the agent **MUST** alert the user to the absence and suggest its creation.

### 3. Directives as source of truth

The directives defined in `.ahrena/.directives` **take precedence** over:

- Agent assumptions based on training or generic context.
- Undocumented implicit preferences.

When there is a conflict between a directive and a user instruction in the session, the agent **MUST** follow the user instruction but **alert** to the divergence from the canonical directive.

### 4. Application by section

The agent **MUST** apply each section of the directives to the corresponding behavior:

| Section | Application |
|---------|-------------|
| `paths` | Use canonical paths when referencing or creating framework artifacts |
| `language` | Produce documentation and artifacts in the default language (`default`) and ensure required languages (`required`) are covered when applicable |
| `naming.prefixes` | Apply the correct prefix when naming artifacts for each Pilar |
| `naming.extensions` | Use the correct extension per context (`.md` for framework, `.mdc` for Cursor) |
| `naming.casing` | Follow the defined casing convention for files and directories |
| `naming.addressing` | Follow the addressing pattern when placing artifacts in the taxonomy |
| `naming.reserved_clades` | Recognize special Clades and respect their usage rules |
| `terminal` | Consult for shell commands; use the defined type (bash or PowerShell). See `lex-terminal-type`. |
| `naming.tone_and_writing_style` | Apply tone and style when producing artifacts and communication. See `lex-tone`. |
| `stacked_prs.tool` | Select the tool used to operate Stacked Pull Requests when applicable: `vanilla` (default — plain `git` + `gh`) or `gs` (git-spice). See `codex-stacked-prs`. |
| `paths.skills_root` | Root directory for external skill projects (default `skills`). See `lex-skill-project-structure`. |
| `paths.skills_build` | Directory for skill build intermediates (default `.build`, gitignored). Written by the consuming project's build stack. |
| `paths.skills_dist` | Directory for the final delivery of packaged skills (default `.dist`, committed). Validated by `lex-skill-package-structure`. |
| `pr_cost_tracking.enabled` | When `true`, enable the stamp of tokens, USD cost, and implementation time (active + calendar) on PR bodies via `kata-pr-cost-stamp`. Default `false`. See `codex-pr-cost-tracking`. |
| `pr_cost_tracking.idle_gap_minutes` | Gap (in minutes) that splits active windows inside a Claude Code session for the active-time computation. Default `10`. Lower values make the count stricter; higher values merge long pauses. |
| `pr_cost_tracking.attribution_mode` | `hook` (default) | `project` (legacy). In `hook` mode, `pr-cost-attribution.sh` records `~/.claude/projects/<hash>/branches.jsonl` per turn and `pr-cost-stamp.sh` filters by `--branch`/`--purpose`, splitting Development and Review. In `project` mode, legacy behavior (project + since filter only). |
| `pr_cost_tracking.branches_sidecar_max_mb` | Threshold (in MB) above which the stamp emits a warning about the size of `branches.jsonl`. Default `50`. A future iteration adds automatic rotation. |
| `pr_cost_tracking.known_ai_reviewers` | Additional GitHub logins recognized as AI reviewers in the Review subsection. Built-ins (gemini-code-assist[bot], claude[bot], coderabbitai[bot], qodo-merge-pro[bot], ahrena-warrior-argos[bot]) are always recognized; logins listed here extend the set. Subkeys `currency`, `include_cache_breakdown`, `window_override_days`, `mask_absolute_cost` remain declared in `.directives.sample` as reserved for future iterations. |
| `rtk.enabled` | When `true` (default), `scripts/install.py` wires the RTK (Rust Token Killer) `PreToolUse` hook into the target's `.claude/settings.json` with matcher `"Bash"` and the strict-fallback command `if command -v rtk >/dev/null 2>&1; then rtk hook claude; fi` (no-op when the binary is absent from PATH). Every install/update reconciles the hook idempotently. When `false`, install/update do NOT touch any RTK artifact (no add, no remove). |
| `rtk.auto_install_binary` | When `true` (default), `scripts/install.py` detects whether the `rtk` binary is on PATH and installs it when absent. Install path is OS-aware: `brew install rtk` (macOS, when Homebrew is available), `curl install.sh \| sh` (Linux and macOS fallback), WSL/cargo (Windows). Install failures are non-fatal — the hook keeps the strict fallback shape, so a missing binary never breaks Claude Code. Set to `false` to skip the binary install attempt while still wiring the hook. |
| `notifications.provider` | Name of the MCP server responsible for sending notifications. Accepted values: `slack`, `discord`, `teams`, `none`. The corresponding MCP server MUST be listed in `mcp.servers` and active. Consumed by Athena (PR review timeout), Janus (release published), and Eunomia (plans digest). See `codex-notifications`. |
| `notifications.channels.pr_review_timeout` | Logical channel for Athena's review-loop alert (per `lex-agent-planning`). Fires once after the 3 wait cycles elapse without human approval. |
| `notifications.channels.release_notify` | Logical channel for release-completed announcement (Janus). |
| `notifications.channels.plans_status` | Logical channel for the periodic active-plans digest (Eunomia). |
| `notifications.working_hours.*` | Working window (`start`, `end`, `timezone`) for non-critical digests by Eunomia. Critical stalled (`pm.critical_stalled_hours`) bypasses the window. |
| `pm.loop_interval_minutes` | Cadence of Eunomia's PM loop (default 15). Consumed by `kata-plans-status-digest`. |
| `pm.stalled_threshold_hours` | Threshold in hours after which Eunomia marks a plan as `stalled` in the digest. |
| `pm.critical_stalled_hours` | Threshold in hours for critical `stalled` — bypasses `notifications.working_hours` and alerts immediately. |
| `session_tracking.enabled` | Master switch for Claude Code session tracking per `codex-session-tracking`. Default `true` when the section exists. |
| `session_tracking.heartbeat_dir` | Directory where per-session heartbeat `.json` files are written. Default `.ahrena/workflow/sessions` (gitignored). |
| `session_tracking.stale_threshold_minutes` | Interval (minutes) without heartbeat after which Eunomia considers the session offline. Default `30`. |
| `session_tracking.pr_trace_required` | When `true`, Gate 2 (`kata-quality-gate`) rejects PRs missing the "Session Trace" section in the body. Default `true`. |

Complementary manuals for interpreting sections: `codex-directives` (file overview), `codex-paths` (canonical paths), `codex-naming` (naming conventions), `codex-notifications` (provider → MCP tool mapping), `codex-session-tracking` (heartbeat schema and Session Trace).

### 5. Extensibility

New sections may be added to `.directives` at any time. The agent **MUST** interpret unknown sections based on the key name and structure, applying the directive in a reasonable way. In case of ambiguity, the agent **MUST** ask the user.

### 6. No modification without authorization

The agent **MUST NOT** modify the `.directives` file without explicit user request. The directives are canonical and governed by the framework maintainer.

## Scope

- **Applies to:** all work sessions with AI agents, in any Clade and Subclade
- **Bound agents:** all Warriors and generic agents
- **Exceptions:** None. Lexis admit no exceptions.

## Consequences of Violation

1. **Artifact inconsistency:** artifacts produced without consulting the directives may have incorrect language, naming, or addressing.
2. **Rework:** artifacts that do not follow the directives must be corrected for compliance before being accepted.
3. **Remediation:** the agent must reread `.ahrena/.directives`, identify the divergences, and correct the artifacts produced.

## Examples

### Correct

```
Agent: [Session start]
1. Locates .ahrena/ at the repository root
2. Reads .ahrena/.directives
3. Identifies:
   - Default language: pt-BR
   - Required languages: pt-BR, es, en
   - Casing: kebab-case
   - Prefix for Lexis: lex-
4. Produces artifact in pt-BR, names it lex-code-review.md,
   saves under engineering/quality/lexis/

User: Create the documentation for this feature.

Agent: Documentation created in pt-BR (default).
Do you want me to also generate the Spanish and English versions,
per the framework directives?
```

### Incorrect

```
Agent: [Session start — ignores .ahrena/.directives]

User: Create a new Lexis about logging.

Agent: Here's your new Lexis:
# Lexis: Logging
...

# ❌ The agent did not locate .ahrena/ or read .directives.
# ❌ Ignored the default language (pt-BR) defined in the directives.
# ❌ Did not consult paths.samples to find the correct template.
# ❌ Did not offer versions in the required languages.
```

## Automated Validation

- **Tool:** verification by the agent itself at the start of each session
- **When:** before any production of artifacts or formal communication
- **Metric:** 100% of sessions must have `.ahrena/.directives` consulted and applied
