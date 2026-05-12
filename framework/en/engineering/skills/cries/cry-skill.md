# Cry: Skill Cycle (implement / validate / package)

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Shortcut to invoke `warrior-claudionor` and run the `implement → validate → package` cycle of an Anthropic Agent Skills project

## Description

Shortcut for the skill cycle after the initial scaffold (`cry-new-skill`). Invokes `warrior-claudionor`, who orchestrates one of three katas (or all three in sequence), with Hephaestus/Apollo delegated per gap.

> **When to prefer `cry-pov`:** if the goal is an **agent PoV** (proving value to the client via the Anthropic stack — Skills, Subagents, Plugins — with native observability and value-proof), use `cry-pov` as the preferred entry point. `cry-pov --kind skill` triggers the full PoV cycle (7 POV katas + `kata-skill-implement`) and produces `docs/{context}/agents-pov/` consumable by Mêtis via `--from-pov`. `cry-skill` remains the entry point when the goal is **packaging a skill as a distributable artifact** isolated from the PoV cycle.

## Invocation

```
/cry-skill --mode <implement|validate|package|all> --slug <name> [--dry-run]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `--mode` | Yes | Cycle phase to run: `implement` (authoring with delegation), `validate` (deterministic check), `package` (build → dist + manifest), or `all` (chains the three) | `--mode all` |
| `--slug` | Yes | Project name (identical to the directory name in `{paths.skills_root}/`) | `--slug scheduled-payments-skill` |
| `--dry-run` | No | Presents the plan without persisting changes to `{paths.skills_build}/`, `{paths.skills_dist}/`, or the project | `--dry-run` |

If `--dry-run` is passed with `--mode package`, the final package is not written — only the report of what would be produced.

## What the Command Does

1. Resolves `paths.skills_root/skills_build/skills_dist` from `.ahrena/.directives`
2. Confirms the project exists at `{paths.skills_root}/{slug}/`
3. Invokes `warrior-claudionor` passing `mode`, `slug`, and `dry_run`
4. Claudionor dispatches to the kata(s):
   - `--mode implement` → `kata-skill-implement` (delegates widgets to Hephaestus, Python tools/scripts to Apollo, authors `SKILL.md`/`references/`)
   - `--mode validate` → `kata-skill-validate` (checks `lex-skill-project-structure`)
   - `--mode package` → `kata-skill-validate` (precondition) + `kata-skill-package` (build → dist + manifest validated against `lex-skill-package-structure`)
   - `--mode all` → chains the three; aborts on the first error
5. Reports the final result (produced paths, file count, violations)

## Prompt Template

```
Context:
- mode: {{mode}}             # implement | validate | package | all
- slug: {{slug}}
- dry_run: {{dry_run}}        # default false

Task:
Invoke warrior-claudionor with the parameters above. The warrior:
1. Reads .ahrena/.directives (paths.skills_*) and verifies skills/{slug}/ exists
2. Dispatches to the kata(s) per `mode`
3. In `package` and `all`, aborts if kata-skill-validate returns `error`
4. In `implement`, delegates via Agent to warrior-hephaestus (widgets)
   and warrior-apollo (Python tools/scripts); authors SKILL.md and
   references/ in-house
5. Reports produced paths, file count, and violations by severity

Abort if: slug does not exist under paths.skills_root, mode is invalid,
or .ahrena/.directives is missing.

Output format:
Structured report per phase (implement / validate / package) with
named delegations and final state. On error, identify the kata + the
violated rule and the remediation step.
```

## Sample Invocations

```
# Full cycle: identifies gaps, implements, validates, and packages
/cry-skill --mode all --slug scheduled-payments-skill

# Deterministic validation only (CI or pre-commit)
/cry-skill --mode validate --slug scheduled-payments-skill

# Packaging only (after manual development)
/cry-skill --mode package --slug scheduled-payments-skill

# Preview of what would be packaged, without writing under .dist/
/cry-skill --mode package --slug scheduled-payments-skill --dry-run

# Implementation only (continue where we left off)
/cry-skill --mode implement --slug scheduled-payments-skill
```

**Expected output (`--mode all` on success):**

```
🛠  warrior-claudionor — full cycle for 'scheduled-payments-skill'

Phase 1/3 — kata-skill-implement
  Delegations: Hephaestus (widgets), Apollo (tools + scripts)
  Files produced: 4 widgets, 2 handlers, 1 test
  SKILL.md + references/ updated

Phase 2/3 — kata-skill-validate
  ✅ no violations

Phase 3/3 — kata-skill-package
  ✅ package: .dist/scheduled-payments-skill.skill (18 files)
```

## Restrictions

- The Cry does **not** modify `.ahrena/.directives` or `framework/`
- The Cry does **not** act without an existing project at `{paths.skills_root}/{slug}/`; to create a new one, use `cry-new-skill`
- The Cry does **not** create branches, worktrees, or commits — versioning discipline stays with the user (`lex-issue-first`, `lex-git-worktrees`, `lex-pr-quality`)
- Human messages in the language set by `language.default`; technical identifiers (slug, modes, paths) preserved

## Difference from Kata

| Aspect | Cry | Kata |
|--------|-----|------|
| **Nature** | Shortcut that collects `--mode` + `--slug` and dispatches | Complete procedure (validate/package/implement, individually) |
| **Validation** | Parameter shape | Phase logic, including delegations |
| **Effect** | Invokes `warrior-claudionor` | Reads/writes filesystem, delegates, or runs script |

## References

- `warrior-claudionor` — Warrior invoked by this Cry
- `kata-skill-implement` — invoked in `--mode implement` or `all`
- `kata-skill-validate` — invoked in `--mode validate`, `package`, and `all`
- `kata-skill-package` — invoked in `--mode package` and `all`
- `cry-new-skill` — predecessor (scaffold before the cycle)
- `lex-skill-project-structure`, `lex-skill-package-structure` — laws being verified
- `lex-directives` — reading `paths.skills_*`
