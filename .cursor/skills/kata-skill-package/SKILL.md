---
name: kata-skill-package
description: "Package Skill. Deterministic packaging of a skill project from {paths.skills_root}/{slug}/ (source) to {paths.skills_dist}/{slug}.skill/ (delivery), with manifest, hashes, and validation against lex-skill-package-structure"
---

# Kata: Package Skill

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Deterministic packaging of a skill project from `{paths.skills_root}/{slug}/` (source) to `{paths.skills_dist}/{slug}.skill/` (delivery), with manifest, hashes, and validation against `lex-skill-package-structure`

## Workflow

```
Progress:
- [ ] 1. Resolve paths (.ahrena/.directives + overrides)
- [ ] 2. Validate the source (kata-skill-validate as precondition)
- [ ] 3. Resolve version/language from frontmatter + framework HEAD SHA
- [ ] 4. Copy source → build/{slug}/
- [ ] 5. Materialize dist/{slug}.skill/ from build
- [ ] 6. Generate .skill-manifest.json (schema_version, skill, framework, references, files)
- [ ] 7. Validate the final package against lex-skill-package-structure
- [ ] 8. Report
```

### Step 1: Resolve paths

1. Read `.ahrena/.directives`, `paths` section:
   - `paths.skills_root` (default `skills`)
   - `paths.skills_build` (default `.build`, gitignored)
   - `paths.skills_dist` (default `.dist`, committed)
2. Apply any overrides passed as arguments
3. Verify the source `{repo_root}/{skills_root}/{slug}/` exists

### Step 2: Validate the source as precondition

1. Invoke `kata-skill-validate skill_path={skills_root}/{slug}`
2. If any `error`-severity violation appears, **abort** without writing under `{skills_build}/` or `{skills_dist}/`
3. Warnings do not block — propagate them to the final report

### Step 3: Resolve metadata

1. Parse the frontmatter of `{skills_root}/{slug}/SKILL.md`:
   - `metadata.version` → goes into `manifest.skill.version`
   - `metadata.language` → goes into `manifest.skill.language`
2. Resolve `framework.ahrena_commit` via `git -C {repo_root} rev-parse HEAD`
3. Abort if the SHA cannot be resolved (≥40 hex chars) — `lex-skill-package-structure` forbids an empty `ahrena_commit`

### Step 4: Copy source → build

1. Clean `{repo_root}/{skills_build}/{slug}/` if present
2. Recursively copy `{skills_root}/{slug}/` → `{skills_build}/{slug}/`, ignoring `__pycache__` and `.DS_Store`
3. Do not transform — the build here is a 1:1 copy of the source; transformations (bundling, dependency resolution) belong to the consuming project's stack, outside this kata's scope

### Step 5: Materialize dist

1. Clean `{repo_root}/{skills_dist}/{slug}.skill/` if present
2. Copy `{skills_build}/{slug}/` → `{skills_dist}/{slug}.skill/` (same `__pycache__`/`.DS_Store` exclusion)

### Step 6: Generate `.skill-manifest.json`

Canonical schema (`lex-skill-package-structure`):

```json
{
  "schema_version": 1,
  "skill": {
    "name": "<slug>",
    "version": "<metadata.version>",
    "language": "<metadata.language>"
  },
  "framework": {
    "ahrena_commit": "<framework HEAD SHA>"
  },
  "references": [
    {
      "kind": "reference",
      "id": "<derived from path: references/<id>.md>",
      "source_commit": "<ahrena_commit>",
      "snapshot_path": "references/<id>.md",
      "snapshot_sha256": "<file sha256>"
    }
  ],
  "files": [
    { "path": ".skill-manifest.json", "sha256": "self" },
    { "path": "SKILL.md", "sha256": "..." },
    { "path": "references/<id>.md", "sha256": "..." },
    ...
  ]
}
```

1. The `.skill-manifest.json` entry uses the literal `"self"` as sha256 (manifest referencing itself)
2. Other entries: hexadecimal SHA-256 of the file's binary content
3. `files[]` is sorted lexicographically by `path`
4. `references[]` is sorted by `id`
5. Persist at `{skills_dist}/{slug}.skill/.skill-manifest.json` with indent=2 and a trailing newline

### Step 7: Validate the final package

Invoke `scripts/skills/package.py` in validation mode (already wired into the pipeline) against `lex-skill-package-structure`, checking the 5 criteria:

| Criterion | Check |
|-----------|-------|
| (a) frontmatter | `SKILL.md` with `name == slug` and `description ∈ [1, 1024]` |
| (b) manifest | schema_version=1, skill.{name,version,language}, framework.ahrena_commit non-empty (≥40 hex) |
| (c) files+sha | every `files[].path` exists and its sha256 matches (except `"self"` for the manifest itself) |
| (d) references | every `references[]` with non-empty `source_commit` + snapshot present + sha256 matches |
| (e) orphans | every file in the package appears in `files[]` |

Any failure here **blocks** the package — rebuild from the source; never edit `{skills_dist}/` by hand.

### Step 8: Report

1. Path of the produced package
2. Path of the manifest
3. Number of packaged files
4. List of violations (empty on success)
5. Exit code `0` when the package passes all 5 criteria; `1` otherwise

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Delivery directory | `{paths.skills_dist}/{slug}.skill/` | filesystem (committed) |
| Manifest | `{paths.skills_dist}/{slug}.skill/.skill-manifest.json` | filesystem |
| Report | Human text or JSON | `stdout` |

## Example Execution

### Input

```
kata-skill-package slug=scheduled-payments-skill
```

### Expected output

```
✅ package: .dist/scheduled-payments-skill.skill
   manifest: .dist/scheduled-payments-skill.skill/.skill-manifest.json
   files:    18
```

### Content of `.dist/scheduled-payments-skill.skill/`

```
.dist/scheduled-payments-skill.skill/
├── SKILL.md
├── .skill-manifest.json    # schema_version=1, files[], references[]
├── references/
│   └── REFERENCE.md
├── scripts/
│   └── ...
└── widgets/
    └── ...
```

## Restrictions

- The kata is **build-stack agnostic**: `lex-skill-package-structure` is explicit — Vite/uv/Node/zip belong to the consuming stack. This kata copies 1:1 from the source; transformations are out of scope
- The kata **never** edits `{skills_dist}/` by hand outside the pipeline; rebuilding from source is the only remediation path
- The kata **does not update** `.directives` — it reads only
- The kata **aborts** when the source has validation errors; packaging over an invalid source is forbidden
- For skills with runtime dependencies (Python venv, Node `node_modules`), resolution is out of scope here — declare the limitation in `SKILL.md` or open a dedicated plan
