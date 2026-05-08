# Codex: Anthropic Agent Skills (SKILL.md format)

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Canonical specification of Anthropic's Agent Skills format — external format consumed by the Claude API, Claude Code, Cursor, Codex CLI, and other agents that adopted the open spec

## Content

### Directory structure

A skill is a directory with, at minimum, a `SKILL.md`:

```
skill-name/
├── SKILL.md          # Required — metadata + instructions
├── scripts/          # Optional — executable code
├── references/       # Optional — additional documentation
├── assets/           # Optional — templates, static resources
└── ...               # Any other files
```

**Important restriction:** the root directory name **MUST** be identical to the value of the `name` field in the frontmatter.

### SKILL.md frontmatter

| Field | Required | Constraints |
|-------|:--------:|-------------|
| `name` | Yes | 1-64 chars; only `a-z`, `0-9`, and hyphen; does not start/end with hyphen; no `--`; **must match the directory name** |
| `description` | Yes | 1-1024 chars; non-empty; describes **what it does** and **when to use** |
| `license` | No | License name or reference to a bundled `LICENSE` file |
| `compatibility` | No | 1-500 chars; environment requirements (target product, system packages, network access) |
| `metadata` | No | Arbitrary key→value map for properties not defined by the spec |
| `allowed-tools` | No | Space-separated string, pre-approved tools (experimental; support varies by agent) |

#### `name`

Skill identifier. Matches the root directory name. Cannot use reserved words (`anthropic`, `claude`) per Anthropic documentation.

Valid: `pdf-processing`, `data-analysis`, `code-review`.

Invalid: `PDF-Processing` (uppercase), `-pdf` (leading hyphen), `pdf--processing` (consecutive hyphens).

#### `description`

Text the agent reads at startup (Level 1) to decide when to activate the skill. **It MUST include concrete keywords** that match the user's task; generic descriptions (`"helps with PDFs"`) reduce correct activation.

Good: *"Extracts text and tables from PDF files, fills PDF forms, and merges multiple PDFs. Use when working with PDF documents or when the user mentions PDFs, forms, or document extraction."*

#### `license`

Short identifier (e.g., `Apache-2.0`, `MIT`) or pointer to a bundled file (e.g., `Proprietary. LICENSE.txt has complete terms`).

#### `compatibility`

When the skill has non-obvious requirements. Valid examples:

```yaml
compatibility: Designed for Claude Code (or similar products)
compatibility: Requires git, docker, jq, and access to the internet
compatibility: Requires Python 3.14+ and uv
```

Most skills do not need the field.

#### `metadata`

Free-form map. Ahrena conventions (not from the spec) that the consuming project's build may honor:

| Key | Ahrena use |
|-----|------------|
| `version` | Semver per `lex-semantic-version` (e.g., `"0.1.0"`) |
| `language` | BCP 47 of the skill content (`pt-BR`, `es`, `en`) |
| `author` | Person, team, or authoring organization |
| `spec_version` | Validated Agent Skills spec version (drift control) |

Other keys are free-form; the consuming agent only sees the raw map. Prefixing organization-specific keys is recommended (e.g., `guardia.bounded_context: scheduled-payments`) to avoid collision.

#### `allowed-tools`

Space-separated string, in `Tool` or `Tool(scope)` format:

```yaml
allowed-tools: Bash(git:*) Bash(jq:*) Read
```

**Experimental** — support varies between Claude Code, the Claude API, and other agents. Treat as a suggestion, not a strong contract.

### SKILL.md body (Markdown after the frontmatter)

No structural restriction. The agent reads the entire body when it activates the skill (Level 2). Spec recommendations:

- Keep below **500 lines** and **5,000 tokens**
- Move extensive material to `references/`
- Include: steps, input/output examples, common edge cases

No restriction does not mean no judgment — a verbose body affects the token budget of every invocation.

### Optional directories

#### `scripts/`

Executable code invoked by the agent via bash. Accepted languages depend on the agent runtime (Python, Bash, Node are common). They MUST:

- Be self-contained or document dependencies explicitly
- Emit useful error messages
- Handle edge cases without silent crashes

When the agent runs a script, **only the output** enters the context — the source code stays on the filesystem (Level 3). This makes a script cheaper in tokens than asking the agent to generate equivalent code inline.

#### `references/`

Additional Markdown for the agent to load **on demand**. Common convention:

- `REFERENCE.md` — detailed technical reference
- `FORMS.md` — templates or structured formats
- Files by domain (`finance.md`, `legal.md`)

Keeping each file focused and short reduces cost when the agent pulls only what it needs.

#### `assets/`

Static resources: document templates, images, data files (CSV, JSON), schemas. The agent opens them when the task flow demands.

### Progressive loading (3 levels)

| Level | When it loads | Approximate cost | Content |
|-------|---------------|------------------|---------|
| 1 — Metadata | Always, at startup | ~100 tokens per skill | `name` + `description` from the frontmatter |
| 2 — Instructions | When the skill is activated | < 5,000 tokens recommended | `SKILL.md` Markdown body |
| 3 — Resources | On demand | Practically unlimited (does not enter the context until read) | Files in `scripts/`, `references/`, `assets/` |

Layered content partitioning is the central principle of the spec. Well-designed skills respect this hierarchy — lean metadata, concise body, weight in resources.

### Cross-file references

Paths **relative to the skill root**:

```markdown
See [the reference guide](references/REFERENCE.md) for details.

To extract, run: `scripts/extract.py`
```

The spec recommends keeping references **one level deep** from the `SKILL.md`. Deep chains hinder progressive loading.

### Availability per surface

A skill produced under the Anthropic spec is consumable by:

| Surface | Support | Distribution |
|---------|---------|--------------|
| Claude API | Pre-built + custom | `/v1/skills` endpoint; requires beta headers `code-execution-2025-08-25`, `skills-2025-10-02`, `files-api-2025-04-14` |
| Claude Code | Custom | Filesystem — `~/.claude/skills/{slug}/` (personal) or `.claude/skills/{slug}/` (project) |
| claude.ai | Pre-built + custom (zip upload in Settings → Features; Pro+ plans) | Per user; no org-wide distribution |
| Cursor / Codex CLI / Gemini CLI | Adopted the open spec | Filesystem similar to Claude Code |

Skills **do not synchronize automatically across surfaces** — separate upload per surface.

### Runtime restrictions

| Surface | Network | Packages |
|---------|---------|----------|
| Claude API | No external access | Pre-installed only; no installation at runtime |
| Claude Code | Same access as the user's program | Installing local to the skill is recommended, not global |
| claude.ai | Variable (admin/user config) | Per surface |

`compatibility` in the frontmatter is where you declare these dependencies — agents that do not satisfy them MAY refuse activation.

### Validation

The spec maintains the [`skills-ref`](https://github.com/agentskills/agentskills/tree/main/skills-ref) CLI:

```bash
skills-ref validate ./my-skill
```

Checks valid frontmatter, naming, and minimum structure. The consuming project's build stack may integrate this validation.

### Security

Anthropic documentation is explicit: treat a skill as installed software. A malicious skill MAY invoke tools harmfully, leak data, or run code outside the declared purpose. Audit:

- Each bundled file (SKILL.md, scripts, references, assets)
- Network calls (skills that fetch external URLs have amplified risk)
- File access / bash patterns inconsistent with the `description`

Skills produced in Ahrena are auditable through the commit trail (refs snapshotted with hash, deterministic manifest enforced by `lex-skill-package-structure`).

## Restrictions

- The spec **does not define** layout for MCP tools nor UI widgets. The Ahrena convention (`codex-skill-tools-and-widgets`) creates additional `tools/` and `widgets/` directories — agents that only know the spec ignore these directories. Documenting the convention as an "Ahrena extension" is mandatory in the generated SKILL.md.
- The spec **does not define** versioning of the skill itself — Ahrena puts it in `metadata.version` (semver per `lex-semantic-version`).
- The spec **does not define** internationalization — Ahrena puts it in `metadata.language`. Each packaged skill is single-language.
