---
description: "Skill build. Shortcut to invoke kata-build-skill and produce .build/{slug}/ + zip from the versioned source"
---

# Cry: Skill build

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Shortcut to invoke `kata-build-skill` and produce `.build/{slug}/` + zip from the versioned source

## Usage

```
/cry-skill-build <slug> [options]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `slug` | Yes | Project at `{paths.skills_root}/{slug}/` | `hello-skill` |
| `clean` | No | `true` deletes `.build/{slug}/` first; default `false` | `clean=true` |
| `skip_zip` | No | `true` skips the zip emission; default `false` | `skip_zip=true` |

## What the Command Does

1. Resolves `paths.skills_root`, `paths.skills_build` in `.ahrena/.directives`
2. Confirms the source project exists
3. Invokes `kata-build-skill` with the parameters
4. Reports the output path, sha256 hash, and zip size
5. Suggests the next step (load the zip into another agent for testing, or wait for `kata-package-skill` in PR 3)

## Prompt Template

```
Context:
- slug: {{slug}}
- clean: {{clean}} (optional, default false)
- skip_zip: {{skip_zip}} (optional, default false)

Task:
Invoke kata-build-skill with the parameters above. The kata:
1. Resolves paths and config
2. Phase 1 — Validate (frontmatter, skill.config, manifests)
3. Phase 2 — Build widgets (Vite production)
4. Phase 3 — Freeze scripts (lock preserved, no installation)
5. Phase 4 — Resolve tools (handler refs validated)
6. Phase 5 — Rewrite bindings (called_via dev → called_via_prod)
7. Phase 6 — Emit (.build/ + .skill-manifest.json + zip)
8. Validate idempotency

Abort on the first failure of any phase.

Output format:
Path of .build/, sha256 hash of the zip, size. On error, a specific
message indicating the phase and the violated rule.
```

## Invocation Example

```
/cry-skill-build hello-skill
```

**Expected output:**

```
✅ Build of hello-skill completed.
   Output: .build/hello-skill/
   Zip:    .build/hello-skill.zip   (124 KB)
   sha256: 7a8c…

Next steps:
- Load the zip into another Claude Code agent for manual testing
- kata-package-skill (PR 3) delivers an auditable .dist/hello-skill.skill
```

## Restrictions

- The Cry **does not modify** `skills/{slug}/` (read only)
- The Cry **does not touch** `.dist/`
- Messages to the user in `language.default`; technical identifiers preserved
- `lex-terminal-type`: shell commands respect the defined terminal

## Difference from Kata

| Aspect | Cry | Kata |
|--------|-----|------|
| **Nature** | 1:1 shortcut | Pipeline in 9 steps (6 phases + validation + report) |
| **Validation** | Parameter form | Frontmatter, manifests, refs, idempotency |
| **Effect** | Invokes the kata | Writes `.build/{slug}/` + zip + manifest |
