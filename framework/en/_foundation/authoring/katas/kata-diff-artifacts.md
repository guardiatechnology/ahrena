# Kata: Diff Artifacts

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Comparing project artifacts with the framework

## Objective

Compare `.ahrena/artifacts` (and, when applicable, `.ahrena/framework`) with the framework in **local** mode (vs framework in the repo) or **remote** mode (vs latest version of the framework on GitHub). Identify what would be incorporated, what differs, or what is out of date relative to the remote.

## When to Use

- Before a push, to see what will be incorporated or what differs between the project and the framework
- To inspect divergence between project artifacts and the framework (local or remote)
- When invoked by `cry-diff-artifacts`

## Inputs

| Input | Required | Description |
|-------|:--------:|-------------|
| Mode | Yes | `local` or `remote`. Local: compare with `paths.framework` in the repo. Remote: compare with the latest version of the framework in the remote repository (obtained via GitHub MCP). |
| Target | No | Relative path(s) under `paths.project_artifacts` or "all". If omitted, consider all artifacts. |

## Workflow

```
Progress:
- [ ] 1. Read directives
- [ ] 2. Local mode: compare with local framework
- [ ] 3. Remote mode: compare with latest version (via GitHub MCP)
- [ ] 4. Final validation and report
```

### Step 1: Read Directives

1. Read `.ahrena/.directives` to obtain:
   - `paths.project_artifacts` — root of project artifacts
   - `paths.framework` — framework root (for local mode)
   - In **remote** mode: URL or ref of the framework repository / comparison branch (e.g. `paths.framework_repo` or `repo.framework`), if present

### Step 2: Local Mode — Compare with Local Framework

1. List `.md` files under `paths.project_artifacts` by relative path `{lang}/{clade}/{subclade}/{pilar}/{file}`.
2. For each logical artifact path, compare with `paths.framework/{lang}/{clade}/{subclade}/{pilar}/{file}`:
   - exists only in artifacts;
   - exists only in the framework;
   - exists in both (in that case, produce a content diff, e.g. line differences).
3. Optional: include `.ahrena/framework/` in the comparison with `paths.framework/` (same structure) to see divergence between the installed copy and the repo framework.
4. Output: table or list with columns "Artifact", "In artifacts", "In framework", "Diff (yes/no or summary)".

### Step 3: Remote Mode — Compare with Latest Version

1. **Required:** use the **GitHub MCP** to obtain the content of the latest version of the framework in the remote repository (main branch, e.g. `main`). The agent **MUST** use the GitHub MCP tools (e.g. read file content in the repo, list tree, compare) to obtain the framework artifacts on the remote.
2. Compare: (a) files in `.ahrena/artifacts/` vs the same path in the remote framework version (obtained via MCP); (b) files in local `paths.framework` (if it exists) vs the same path in the remote version. Output: "local only", "remote only", "different" (with diff summary when possible).
3. In remote mode, **do not** replace the GitHub MCP with only `git fetch`/clone on the command line; the remote diff **MUST** be based on data obtained via the GitHub MCP.

### Step 4: Final Validation

- [ ] Report delivered to the user with the differences found
- [ ] No changes were made to files (read-only)

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Diff report | Text (and optionally structured) | Response to user |

Report content: artifacts only in artifacts, only in the framework (local or remote), and those that differ (with diff indication).

## Constraints

- Read-only; do not modify `.ahrena/` or `framework/`.
- In **remote** mode, the GitHub MCP **must** be used to obtain the state of the framework on the remote; do not use only local git for comparison.

## References

- `codex-pilars` — Flow and concepts of project artifacts and Push
- `.ahrena/.directives` — paths.project_artifacts, paths.framework
- `kata-push-to-framework` — Procedure for incorporating into the framework
- Remote mode: GitHub MCP (server configured for the framework repository)
