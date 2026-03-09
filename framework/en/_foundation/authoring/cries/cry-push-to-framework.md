# Cry: Push to Framework

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Incorporating project artifacts into the framework

## Description

Quick command to incorporate into the canonical framework the artifacts created in the project space (`.ahrena/artifacts/`). It invokes `kata-push-to-framework`, which copies files to `framework/`, ensures translations in the required languages, and optionally removes the copies from the project.

## Usage

```
/cry-push-to-framework [target] [--remove]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `target` | No | Path(s) under `.ahrena/artifacts/` or "all". If omitted, processes all artifacts found | `pt-BR/engineering/quality/lexis/lex-foo.md` or `all` |
| `--remove` | No | If present, removes artifacts from `.ahrena/artifacts/` after copying to the framework | `--remove` |

## What the Command Does

1. Reads `.ahrena/.directives` to obtain `paths.project_artifacts`, `paths.framework`, and `language.i18n`
2. Identifies artifacts in `.ahrena/artifacts/` (all or the specified ones)
3. Runs `kata-push-to-framework` with the provided parameters
4. Copies artifacts to `framework/` and generates missing translations
5. Optionally removes files from the project
6. Reports the incorporated files

## Prompt Template

```
Context:
- Target: {{target}} (or all artifacts in .ahrena/artifacts/)
- Remove from project after Push: {{--remove}}

Task:
Execute kata-push-to-framework. Consult .ahrena/.directives for
paths.project_artifacts and language.i18n. Incorporate the artifacts into
the framework and ensure versions in all required languages.

Output format:
List of files copied to framework/ and translations created (if any).
If --remove was used, confirmation of removal in .ahrena/artifacts/.
```

## Invocation Examples

**Incorporate all project artifacts:**

```
/cry-push-to-framework
```

**Incorporate a specific artifact:**

```
/cry-push-to-framework pt-BR/engineering/quality/lexis/lex-code-review.md
```

**Incorporate and remove from project:**

```
/cry-push-to-framework all --remove
```

## Constraints

- Only incorporates artifacts under `.ahrena/artifacts/` with valid structure (lang/clade/subclade/pilar)
- Always runs `kata-push-to-framework` (never performs the copy directly without the Kata)

## References

- `kata-push-to-framework` — Procedure executed by this Cry
- `codex-pilars` — Recommended flow (create in project → validate → Push)
