# Lexis: Mandatory Structure of the Delivered `.skill` Package

> **Prefix:** `lex-` | **Type:** Unbreakable Law | **Scope:** `.skill` packages versioned in `{paths.skills_dist}/` (default `.dist/`) — final delivery consumed by external agents in the Anthropic Agent Skills format

## Law

> **Every `.skill` package in `{paths.skills_dist}/` (default `.dist/`) MUST contain (1) `SKILL.md` with a valid Anthropic Agent Skills frontmatter (`name` 1-64 chars kebab-case matching the package directory name, `description` 1-1024 chars), (2) `.skill-manifest.json` valid against the canonical Ahrena schema (`schema_version`, `skill.name`, `skill.version`, `skill.language`, non-empty `framework.ahrena_commit`, `references[]` and `files[]`), (3) for each entry in `files[]`: the file MUST exist in the package and its `sha256` MUST match, (4) for each entry in `references[]`: a file present at `references/<id>.md` with a matching `snapshot_sha256`, and a non-empty `source_commit`, (5) zero orphan files in the package (every delivered file MUST be declared in `files[]`). The law governs the packaged output; it is AGNOSTIC to the build — `Vite`, `uv`, `Node`, `zip`, ports, packaging tools are the exclusive responsibility of the consuming project's stack (Makefile, GitHub Actions, npm scripts, custom devops). Ahrena validates what arrives in `.dist/`, not how the build got it there.**

## Coverage

- **Applies to:** every `.skill` (directory or sealed file per Anthropic spec) delivered in `{paths.skills_dist}/`, in any language declared in `metadata.language`
- **Bound agents:** `warrior-claudionor` (orchestrator), `kata-skill-package` (deterministic packager that produces the package against this Lex), human reviewer, `kata-quality-gate` when it integrates the verification, authors who add or modify packages in `.dist/`
- **Exceptions:** None. Lexis admit no exceptions. `.skill` packages produced by automation or manually follow the same law

## Canonical schema of `.skill-manifest.json`

```json
{
  "schema_version": 1,
  "skill": {
    "name": "scheduled-payments-skill",
    "version": "0.1.0",
    "language": "pt-BR"
  },
  "framework": {
    "ahrena_commit": "956826f0419aea431e72b8d1796a409d0351e749"
  },
  "references": [
    {
      "kind": "lexis",
      "id": "engineering/skills/lexis/lex-skill-project-structure",
      "source_commit": "956826f0419aea431e72b8d1796a409d0351e749",
      "snapshot_path": "references/lex-skill-project-structure.md",
      "snapshot_sha256": "a1b2c3..."
    }
  ],
  "files": [
    { "path": "SKILL.md", "sha256": "..." },
    { "path": ".skill-manifest.json", "sha256": "self" },
    { "path": "widgets/dist/index.js", "sha256": "..." },
    { "path": "references/lex-skill-project-structure.md", "sha256": "..." }
  ]
}
```

| Field | Required | Constraint |
|-------|:--------:|------------|
| `schema_version` | Yes | Integer; current: `1` |
| `skill.name` | Yes | Matches the `.skill` directory name |
| `skill.version` | Yes | Semver per `lex-semantic-version` |
| `skill.language` | Yes | BCP 47 |
| `framework.ahrena_commit` | Yes | SHA-1 or SHA-256 of the Ahrena framework commit that produced the package; **MUST NOT be empty** |
| `references[]` | Yes (list MAY be empty) | Each entry: `kind`, `id`, `source_commit` (non-empty), `snapshot_path` (relative to the package), `snapshot_sha256` |
| `files[]` | Yes (list MUST NOT be empty) | Lexicographically ordered list of ALL files in the package with their `sha256`; the `.skill-manifest.json` entry MAY use the value `"self"` (manifest referencing itself) |

## Rules

### 1. Valid SKILL.md frontmatter

Per `codex-skill-anthropic-agent-skills`:

- `name`: regex `^[a-z0-9](?:[a-z0-9]|-(?!-)){0,62}[a-z0-9]?$`, 1-64 chars, no reserved words (`anthropic`, `claude`)
- `name` matches the root directory name of the `.skill`
- `description`: 1-1024 chars, non-empty
- Other optional fields (license, compatibility, metadata, allowed-tools) per spec when present

### 2. Valid `.skill-manifest.json`

- Parses as JSON
- Schema as in the table above
- `framework.ahrena_commit` is a non-empty SHA (40+ hexadecimal characters)
- `files[]` contains **every** entry that exists in the package (no orphans)
- `files[]` ordering is lexicographic by `path` (per auditability requirement)

### 3. Hashes match

For each `files[].path`:

- The file exists in the package
- `sha256(<file>) == files[<i>].sha256` (except for `.skill-manifest.json`, which MAY use the value `"self"`)

For each `references[]`:

- `references/<...>.md` exists (path relative to the package)
- `sha256(<snapshot file>) == references[<i>].snapshot_sha256`
- `source_commit` is a non-empty SHA (referencing the Ahrena framework commit from which the reference was snapshotted)

### 4. No orphan files

Every file in the package directory (recursive, except `.skill-manifest.json` itself) MUST appear in `files[]`. Orphan files break auditability of what was delivered.

### 5. Build-agnostic

The law does NOT prescribe:

- Widget bundler (Vite, esbuild, Webpack, Rollup — the project's choice)
- Script runtime (Python via uv, pip, conda; Node, Bun, Deno; etc.)
- Packaging command (zip, tar, proprietary format, etc.)
- Hash, ordering, or mtime computation tool
- CI/CD pipeline (GitHub Actions, GitLab CI, Jenkins, manual local)
- Ports, hosts, local dev environments

The consuming project's stack decides. The law only validates what arrives in `.dist/`.

## HARD-GATE

Per [`lex-hard-gate-pattern`](../../../_foundation/quality/lexis/lex-hard-gate-pattern.md), the canonical textual block:

```
<HARD-GATE>
Reviewer (human) and any agent that validates PRs MUST NOT approve
the merge of a PR that adds or modifies a `.skill` package in
`{paths.skills_dist}/` (default `.dist/`) without the package
satisfying ALL 5 canonical criteria:

  (a) SKILL.md with valid Anthropic frontmatter (name, description)
      and name identical to the package directory name
  (b) .skill-manifest.json valid against the schema (schema_version,
      skill, non-empty framework.ahrena_commit, references[], files[])
  (c) For each files[].path: file present + sha256 matches
  (d) For each references[]: snapshot present + snapshot_sha256
      matches + non-empty source_commit
  (e) Zero orphan files (every file in the package listed in files[])

This rule applies to EVERY .skill package in .dist/, regardless of:
  - perceived size ("it's just a smaller version")
  - urgency ("must ship today")
  - who requested ("the customer is asking")
  - confidence in the author ("the author already validated locally")

Declared exception: None. Re-submit a corrected package if any
criterion fails.
</HARD-GATE>
```

## Violation Consequences

1. **Merge block:** a PR containing a `.skill` that fails any of the 5 criteria is rejected by the reviewer or (in the future) by integrated `kata-quality-gate`.
2. **Alert:** the automated validator identifies the violated criterion and the path of the offending file.
3. **Remediation:** the author fixes the package (regenerates the build, updates the manifest, completes hashes, declares orphan files) and resubmits. There is no conditional merge.

## Examples

### Correct

```
.dist/hello-skill.skill/
├── SKILL.md                         # name: hello-skill (matches the directory)
├── .skill-manifest.json             # schema_version=1, ahrena_commit=956826f..., 5 files, 1 ref
├── references/
│   └── lex-skill-project-structure.md   # snapshot, snapshot_sha256 matches, source_commit=956826f...
└── widgets/
    └── dist/
        └── index.js                  # listed in files[], sha256 matches
```

`.skill-manifest.json` listing all 5 files in `files[]` ordered; no orphan files.

### Incorrect

```
.dist/hello-skill.skill/
├── SKILL.md                         # name: helloskill (does not match the directory)  ❌ criterion (a)
├── .skill-manifest.json             # framework.ahrena_commit: ""                       ❌ criterion (b)
├── references/
│   └── lex-skill-project-structure.md   # source_commit: ""                              ❌ criterion (d)
├── extras/
│   └── debug.log                     # file present, NOT in files[]                      ❌ criterion (e)
└── widgets/
    └── dist/
        └── index.js                  # declared sha256 diverges                          ❌ criterion (c)
```

A PR containing this package MUST be blocked in review for 5 criteria violated simultaneously.

## Automated Validation

- **Tool:** `scripts/skills/package.py` implements the deterministic validator of this Lex using stdlib (`hashlib.sha256` to check each declared file, `os.walk(package)` ∖ `manifest.files[]` for orphan files, inline manifest parser). `kata-skill-package` orchestrates build → dist → validation and is invoked by `warrior-claudionor` (or directly via `cry-skill --mode package`). Human reviewer verifies the result on the PR while `kata-quality-gate` does not integrate.
- **When:** PR review (human today; future Gate 2 via `kata-quality-gate` once the validator is integrated); CI when enabled.
- **Metric:** 0 PRs merged with a `.skill` package violating any of the 5 criteria; 0 entries with empty `framework.ahrena_commit` or `source_commit`; 0 orphan files.

## References

- `codex-skill-anthropic-agent-skills` — SKILL.md frontmatter, naming, file references
- `codex-skill-project-architecture` — structure of the source project that produces the package
- `codex-skill-tools-and-widgets` — convention of the `tools/` and `widgets/` manifests
- `lex-skill-project-structure` — source/build/dist separation
- `lex-semantic-version` — versioning of `skill.version`
- `lex-hard-gate-pattern` — textual pattern applied in this law
- `warrior-claudionor`, `kata-skill-package` — orchestrator and packager that give operational voice to this Lex
- `scripts/skills/package.py` — deterministic implementation used by `kata-skill-package`
