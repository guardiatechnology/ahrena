# Lexis: Mandatory Rule in platforms.yaml for Lexis and Codex

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** Creation of Lexis and Codex in the Ahrena framework

## Law

> **Every Lexis and every Codex created in the framework MUST have a corresponding entry in `cursor.rules` in `framework/platforms.yaml`. The entry MUST include at least the `description` key.**

## Rules

### 1. Mandatory entry

For each Lexis or Codex artifact (file `lex-*.md` or `codex-*.md` in the framework), there MUST exist in `cursor.rules` a key equal to the artifact's **rule key** (framework-relative path without language and without `.md`). E.g. `_foundation/process/lexis/lex-directives`, `documentation/i18n/codex-language-ptbr`.

### 2. Mandatory `description` key

Each entry in `cursor.rules` **MUST** contain the **`description`** key with text that guides the platform (e.g. Cursor) to apply the rule intelligently. The keys `alwaysApply` and `globs` are optional (default: alwaysApply false; no globs).

### 3. When creating

When creating a new Lexis or Codex (via kata-create-lexis, kata-create-codex or equivalent flow), the agent **MUST** add the entry to `framework/platforms.yaml` under `cursor.rules` immediately, with at least `description`. The sync (`python .ahrena/update.py --sync-cursor`) will fail if any lex/codex is not listed.

### 4. Project override

The project may define or override entries in `.ahrena/platforms.yaml`. The requirement is that the entry exists (in default or override); the source may be the framework or the project.
