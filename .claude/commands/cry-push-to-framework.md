Push to Framework. Incorporating project artifacts into the framework

# Cry: Push to Framework

> **Prefix:** `cry-` | **Type:** Recurring Command | **Scope:** Incorporating project artifacts into the framework

## Usage

```
/cry-push-to-framework [target] [--local | --remote] [--remove]
```

## Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|---------|
| `target` | No | Path(s) under `.ahrena/artifacts/` or "all". If omitted, processes all artifacts found | `pt-BR/engineering/quality/lexis/lex-foo.md` or `all` |
| `--local` | No | Incorporate into `framework/` in the current repository (disk copy + i18n). | `--local` |
| `--remote` | No | Incorporate into the framework repository on GitHub using the **GitHub MCP** (branch, push, open PR). | `--remote` |
| `--remove` | No | If present, removes artifacts from `.ahrena/artifacts/` after copying to the framework (local) or after successful send (remote) | `--remove` |

## What the Command Does

1. Determines the mode (local or remote) from the `--local` or `--remote` parameters
2. Reads `.ahrena/.directives` to obtain `paths.project_artifacts`, `paths.framework`, and `language.i18n`
3. Identifies artifacts in `.ahrena/artifacts/` (all or the specified ones)
4. Runs `kata-push-to-framework` with the mode and parameters provided
5. In local mode: copies artifacts to `framework/` and generates missing translations; in remote mode: sends to the framework repository via GitHub MCP (branch, push, PR)
6. Optionally removes files from the project
7. Reports the incorporated files (and in remote mode, the PR link)

## Prompt Template

```
Context:
- Mode: {{--local}} or {{--remote}}
- Target: {{target}} (or all artifacts in .ahrena/artifacts/)
- Remove from project after Push: {{--remove}}

Task:
Execute kata-push-to-framework in the indicated mode. Consult .ahrena/.directives for
paths.project_artifacts, paths.framework, and language.i18n. In remote mode, use
the GitHub MCP to sync with the framework repository.

Output format:
List of incorporated files and translations created (local mode) or branch and PR link (remote mode).
If --remove was used, confirmation of removal in .ahrena/artifacts/.
```

## Constraints

- Only incorporates artifacts under `.ahrena/artifacts/` with valid structure (lang/clade/subclade/pilar)
- Always runs `kata-push-to-framework` (never performs the copy directly without the Kata)
