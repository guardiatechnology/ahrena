# Codex: git-spice (gs) — Stacked Branch Automation

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Installation, setup, command catalog, and operational mapping for `git-spice` when the project adopts it for Stacked Pull Requests

## Overview

`git-spice` is a Go CLI (GPL-3.0) that automates stacked branch operations on top of native git. The central use case in the Ahrena context is eliminating manual cascade rebase: when a lower layer receives `commit create` or `commit amend` via `git-spice`, every layer above it is automatically rebased. Other conveniences include trunk declared once (`gs repo init --trunk`), `gs repo sync` that deletes merged branches and rebases the rest, and `gs auth login` that reuses the `gh` token via the CLI authentication method.

This Codex is the field reference when `.ahrena/.directives` declares `stacked_prs.tool: gs`. Strategic decisions (stack vs single PR, layer decomposition, naming, bottom-up merge policy) remain in `codex-stacked-prs` — this document covers only the `gs` operation.

## Context

- **Domain:** stacked branch chain automation via dedicated CLI; alternative to the vanilla path (`git` + `gh`)
- **Audience:** AI agents (warriors and katas executing `kata-stacked-pr-create`, `kata-stacked-pr-rebase`, `kata-stacked-pr-merge`); human contributors running stacks manually
- **Update:** when `gs` flags change in a new release, when a `gs` version is adopted as the framework's minimum tested version, or when recurring troubleshooting justifies a new entry

## Content

### 1. Minimum tested version

| Item | Value |
|------|-------|
| Minimum tested `git-spice` | `0.28.0` |
| Minimum `git` required by gs | `2.38` |
| Supported forges | GitHub, GitLab (from gs 0.9.0), Bitbucket Cloud (from gs 0.25.0) |

> **Important:** the binary installed by Homebrew is named `git-spice`, not `gs`. The `gs` alias is a shell convention (`alias gs='git-spice'`); the official documentation and this Codex use `gs` for brevity. Whenever an agent runs the command programmatically, it MUST invoke `git-spice` to avoid depending on a user shell alias.

### 2. Installation

| Platform | Command |
|----------|---------|
| macOS / Linux (Homebrew) | `brew install git-spice` |
| Any OS with Go ≥ 1.22 | `go install go.abhg.dev/gs@latest` |
| Debian / Ubuntu | `.deb` from [releases](https://github.com/abhinav/git-spice/releases) |
| Fedora / RHEL | `.rpm` from releases |
| Alpine | `.apk` from releases |
| Arch Linux (AUR) | `git-spice-bin` |

After installing, add the alias if desired:

```bash
# bash / zsh
echo "alias gs='git-spice'" >> ~/.zshrc

# fish
abbr -a gs git-spice
```

Verification:

```bash
git-spice --version
# git-spice 0.28.0 or higher
```

### 3. Per-repository setup (one-time)

#### 3.1 Initialization

Inside the repository (in any worktree, including the shared worktree of a stack):

```bash
git-spice repo init --trunk main --remote origin
```

| Flag | Meaning |
|------|---------|
| `--trunk=BRANCH` | Branch protected against writes (`main`, `master`, `release/*`). Honors `lex-protected-trunk` |
| `--remote=NAME` | Remote to push submitted branches to (default: `origin`) |
| `--upstream=NAME` | Remote against which to open CRs; differs from `--remote` only in fork mode |
| `--reset` | Forgets all gs metadata for the repository (rare; use when metadata is corrupted) |

If `--upstream` is not passed, gs uses the same remote as `--remote`. Re-running `repo init` on an already-initialized repo migrates existing branches to the new trunk if it changes.

Metadata lives in `.git/spice/` (inside `.git/`, untracked — no `.gitignore` needed).

#### 3.2 Authentication

```bash
git-spice auth login
```

The prompt offers:

| Method | When to prefer |
|--------|----------------|
| **CLI** | `gh` (or `glab`) already authenticated on the machine — `gs` reuses the token; fastest option in the Ahrena environment |
| **OAuth** | Browser flow; no `gh` installed |
| **GitHub App** | Per-repo install; useful in organizations with restrictive SSO |
| **Git Credential Manager** | Reuse credentials already stored by Git |
| **Personal Access Token** | Manually generated token; less secure than OAuth |

The token is stored in the OS keyring (Keychain on macOS, Secret Service on Linux, Credential Manager on Windows). To revalidate:

```bash
git-spice auth status            # check state
git-spice auth login --refresh   # renew
git-spice auth logout            # remove
```

> **Ahrena rule:** never persist tokens in tracked files or in `.ahrena/.directives` (per `lex-mcp` rule 2 and equivalent practices). Use only the OS keyring.

### 4. Command catalog by category

Reference version: gs 0.28.0. Each subcommand has a short alias in parentheses.

#### 4.1 Repository

| Command | Function |
|---------|----------|
| `gs repo (r) init (i)` | Initialize gs metadata in the repo (defines trunk, remotes) |
| `gs repo (r) sync (s)` | Pull trunk + delete already-merged branches + optional `--restack` |
| `gs repo (r) restack (r)` | Restack **all** branches tracked by gs |

#### 4.2 Branch

| Command | Function |
|---------|----------|
| `gs branch (b) track (tr)` | Import existing branch into gs (optional `--base`) |
| `gs branch (b) untrack (untr)` | Remove branch from tracking without deleting |
| `gs branch (b) checkout (co)` | Switch branches within the stack |
| `gs branch (b) create (c)` | Create new branch above the current one; commit current stage; accepts `--target`, `--insert`, `--below`, `-m`, `-a` |
| `gs branch (b) delete (d, rm)` | Delete branch (local + tracking) |
| `gs branch (b) submit (s)` | Create/update CR for the current branch only |
| `gs branch (b) restack (r)` | Restack only the current branch against its base |
| `gs branch (b) onto (on)` | Move branch onto another base (replaces `git rebase --onto` in common cases) |
| `gs branch (b) rename (rn, mv)` | Rename branch and update metadata |
| `gs branch (b) fold (fo)` | Merge the branch into its base (consolidate layers) |
| `gs branch (b) split (sp)` | Split the branch into multiple branches per commit |
| `gs branch (b) squash (sq)` | Squash the branch into a single commit |
| `gs branch (b) edit (e)` | `git rebase -i` aware of the stack |
| `gs branch (b) diff (di)` | Diff between branch and base |

#### 4.3 Stack / Upstack / Downstack

| Command | Function |
|---------|----------|
| `gs stack (s) submit (s)` | Submit the **entire** stack (creates/updates each layer's CR) |
| `gs stack (s) restack (r)` | Restack the entire stack |
| `gs stack (s) edit (e)` | Reorder or remove layers via editor (occasional use) |
| `gs stack (s) delete (d)` | Delete **all** stack branches |
| `gs upstack (us) submit (s)` | Submit only the current branch and those above |
| `gs upstack (us) restack (r)` | Restack only the current branch and those above |
| `gs upstack (us) onto (o)` | Move the current branch + upper layers to a new base |
| `gs upstack (us) delete (d)` | Delete only the branches above |
| `gs downstack (ds) track (tr)` | Import branches below in the graph |
| `gs downstack (ds) submit (s)` | Submit only the current branch and those below |
| `gs downstack (ds) edit (e)` | Reorder layers below |

#### 4.4 Commit

| Command | Function |
|---------|----------|
| `gs commit (c) create (c)` | Shortcut for `git commit` + `gs upstack restack` (keeps upper layers in sync) |
| `gs commit (c) amend (a)` | Shortcut for `git commit --amend` + `gs upstack restack` |
| `gs commit (c) split (sp)` | Split the last commit into multiple |
| `gs commit (c) fixup (f)` | Create fixup commit against an earlier commit |
| `gs commit (c) pick (p)` | Stack-aware cherry-pick |

Relevant flags (`commit create` / `commit amend`):

| Flag | Function |
|------|----------|
| `-a, --all` | Auto-stage modified files (equivalent to `git commit -a`) |
| `-m, --message=MSG` | Inline message |
| `--no-verify` | Skips `pre-commit`/`commit-msg` hooks (use with caution; consult `lex-conventional-commits`) |
| `--signoff` | Adds `Signed-off-by:` (not GPG signing; see section 7) |
| `--no-edit` (amend only) | Does not open editor |

#### 4.5 Rebase

| Command | Function |
|---------|----------|
| `gs rebase (rb) continue (c)` | Continue rebase interrupted by conflict (replaces `git rebase --continue`) |
| `gs rebase (rb) abort (a)` | Abort rebase in progress |

#### 4.6 Log and navigation

| Command | Function |
|---------|----------|
| `gs log (l) short (s)` | List tracked branches (stack visualization) |
| `gs log (l) long (l)` | List branches + commits |
| `gs up (u)` | Move up one layer |
| `gs down (d)` | Move down one layer |
| `gs top (U)` | Go to top of stack |
| `gs bottom (D)` | Go to bottom of stack |
| `gs trunk` | Go to trunk (`main`) |

### 5. Operation → vanilla → gs mapping

Equivalence table between the vanilla path described in `codex-stacked-prs` and the gs path. Use during mental translation when alternating between projects.

| Operation | Vanilla (`git` + `gh`) | git-spice |
|-----------|------------------------|-----------|
| Initialize stack support in the repo | (no setup) | `gs repo init --trunk main` (one-time) |
| Create the stack's first layer | `git checkout -b feat/N-stack-1-slug main` | `gs branch create feat/N-stack-1-slug` (with stage) |
| Create layer above | `git checkout -b feat/N-stack-2-slug feat/N-stack-1-slug` | `gs branch create feat/N-stack-2-slug` (while on layer 1, with stage) |
| Commit while keeping upper layers in sync | `git commit && for i in upper: git checkout {i} && git rebase {i-1} && git push --force-with-lease` | `gs commit create -m "..."` (auto-restack of upper layers) |
| Amend an already-submitted commit | `git commit --amend && manual cascade rebase` | `gs commit amend [--no-edit]` (auto-restack) |
| Rebase against advanced trunk | `git fetch && git rebase origin/main && manual cascade rebase` | `gs repo sync --restack` |
| Submit PR for current layer only | `gh pr create --base $PREV --head $THIS ...` | `gs branch submit` |
| Submit PRs for the whole stack | loop of N `gh pr create` | `gs stack submit [--draft] [--fill]` |
| Update PRs after push | (auto via head push) | `gs branch submit` or `gs stack submit` (idempotent) |
| Safe force-push | `git push --force-with-lease` | gs uses lease by default; `--force` bypasses |
| Delete merged branches | manual: `git push origin --delete` + `git branch -D` | `gs repo sync` (handles local cleanup; `--delete-branch` on merge handles remote) |
| Update PR `base` after merging the lower layer | `gh pr edit $PR --base main` | `gs repo sync` rebases automatically; `gs branch submit` recreates with new base |
| Resolve rebase conflict | `git rebase --continue` / `--abort` | `gs rebase continue` / `gs rebase abort` |
| Reorder layers in the middle | recreate manually | `gs stack edit` |

### 6. Force-push: lease by default

Unlike `git push`, `gs branch submit` and `gs stack submit` apply `--force-with-lease` automatically — the push is rejected if a reviewer committed on top since the last fetch.

| Flag | Behavior |
|------|----------|
| (default) | Implicit `--force-with-lease` |
| `--force` | Bypasses lease — equivalent to blind `git push --force` |
| `--no-verify` | Skips `pre-push` hooks |

> **Ahrena rule:** never pass `--force` without recorded justification. The default already covers 99% of cases. `--no-verify` requires explicit user authorization (same discipline applied to the vanilla path).

### 7. Hooks and GPG interaction

#### 7.1 pre-commit / commit-msg hooks

`gs commit create` and `gs commit amend` run hooks just like `git commit` would. For heavy hooks (linters, tests), auto-restack can be slow because each upper layer redoes the hook cycle. Mitigations:

1. **Optimize hooks** — move heavy validation to CI; keep pre-commit fast (≤ 1s).
2. **Stack-state-conditional hook** — a hook that detects active `.git/spice/` may choose lite mode.
3. **Deliberate `--no-verify`** — in extreme cases, with user authorization and recorded justification (ideally in the PR body).

#### 7.2 GPG signing (lex-signed-commits)

`gs` respects the global git config (`commit.gpgsign=true`, `user.signingkey`). Since `gs commit create/amend` calls `git commit` underneath, the signature is preserved normally; there is no specific flag in `gs`. In auto-restack rebase, git re-applies the commits and — if `commit.gpgsign=true` — signs the resulting new commits with the configured key.

Verification:

```bash
git log --show-signature -3
# expected: "Good signature from ..." on each layer's commits
```

> **Note:** `--signoff` (`Signed-off-by:`) is a plain-text trailer, not a cryptographic signature. `lex-signed-commits` requires verifiable GPG signing; the trailer is optional and orthogonal.

### 8. Recommended workflow (short)

1. `gs repo init --trunk main` — once per repo.
2. `gs auth login` (use **CLI** method if `gh` is logged in).
3. Shared worktree for the stack (per `codex-stacked-prs` section 4): `git worktree add .worktrees/{N}-{slug}-stack -b feat/{N}-stack-1-{slug} main`.
4. `cd .worktrees/{N}-{slug}-stack`
5. Edit files, `git add`, `gs commit create -m "feat(scope): layer 1 — schema (1/N)"`.
6. `gs branch create feat/{N}-stack-2-{slug}` (while staged with layer 2's files). Repeat through the last layer.
7. `gs stack submit --draft` to open all PRs as drafts at once (or `--fill` to populate title/body from commits).
8. For each created PR, mirror labels/assignee/reviewers via `gh pr edit` (see `kata-stacked-pr-create` "Variant: git-spice" section). `gs stack submit` accepts `--label`, `--reviewer`, `--assign` but does not differentiate per layer — for exact mirroring use `gh pr edit`.
9. Review iteration: `gs commit amend` on the criticized layer, then `gs branch submit` (idempotent).
10. Bottom-up merge: `gh pr merge --squash` for the base layer; then `gs repo sync` to rebase the rest and delete the merged layer locally.

### 9. Known limitations

| Limitation | Source |
|------------|--------|
| Cross-fork PR (forks with different upstream and push remotes) only creates CR for branches based directly on trunk | Official doc — `guide/limits/` |
| Upstream squash-merge erases unsquashed history; upper layers need `gs repo sync` (and sometimes `gs upstack restack`) to reflect | Official doc |
| Bitbucket Cloud has no support for labels, assignees, or template enumeration via `gs submit` | Official doc |
| Repos that dismiss approval on PR base change are incompatible with stacks (GitHub limitation, not `gs`'s) | Official doc |
| Layer reordering via `gs stack edit` is well supported, but hooks that depend on a specific commit order may confuse the restack — test in sandbox first | Operational |

### 10. Troubleshooting

| Symptom | Likely cause | Resolution |
|---------|--------------|------------|
| `gs commit create` fails with "branch is not tracked" | Branch created with `git checkout -b` instead of `gs branch create` | `gs branch track` to import |
| `gs stack submit` rejects push | `--force-with-lease` detected divergence (someone pushed to the remote branch) | `git fetch origin {branch}` and investigate; never `--force` blindly |
| Auto-restack loops with heavy hook | Hook re-triggering rebase | Optimize hook or use `--no-verify` with authorization |
| `gs auth status` shows "not logged in" but `gh` is | Auth method selected the first time was different from **CLI** | `gs auth login --refresh` and choose **CLI** |
| Upstream squash merge produces "artificial conflicts" in rebase | Squashed history doesn't match what `gs` expected | `gs repo sync` resolves most cases; otherwise `gs upstack onto main` |
| `gs repo init --trunk main` fails with "trunk does not exist" | Trunk branch doesn't exist locally yet | `git fetch origin && git checkout main && gs repo init --trunk main` |
| Confusion between `gs` and `git-spice` | Alias not configured | Use `git-spice` directly in scripts; `gs` only in interactive shell |

### 11. Related directive

The choice between `vanilla` and `gs` is controlled by `.ahrena/.directives`:

```yaml
stacked_prs:
  tool: gs        # vanilla (default) | gs
```

| Value | Behavior |
|-------|----------|
| `vanilla` (or absent) | Katas execute the classic `git` + `gh` procedure |
| `gs` | Katas execute the "Variant: git-spice" section — precondition: `git-spice` installed and `gs repo init` ran |

Switching from `vanilla` to `gs` in a project with active stacks requires manual import via `gs branch track` for each existing branch. There is no automation for this migration.

## Glossary

| Term | Definition |
|------|------------|
| Trunk | Branch protected against writes, the stack's final target (`main`, `master`, `release/*`). Declared once in `gs repo init --trunk` |
| Stack | Ordered chain of branches where each has the previous as base; in git-spice, the set tracked by gs |
| Upstack / Downstack | Layers above / below the current branch in the stack |
| Restack | Re-rebase of one or more layers against their updated bases; in gs it is automatic after `commit create`/`amend` |
| Track | Import an existing git branch into gs tracking |
| CR (Change Request) | gs-agnostic term for Pull Request (GitHub) / Merge Request (GitLab) / Pull Request (Bitbucket) |
| `--force-with-lease` | Variant of `git push --force` that rejects overwriting remote commits not fetched locally; default in `gs submit` |

## References

- [git-spice — official site](https://abhinav.github.io/git-spice/)
- [git-spice — repository (GPL-3.0)](https://github.com/abhinav/git-spice)
- `codex-stacked-prs` — conceptual model and canonical Decision Checklist (shared between vanilla and gs)
- `kata-stacked-pr-create` "Variant: git-spice" section — operational creation steps
- `kata-stacked-pr-rebase` "Variant: git-spice" section — auto-restack and conflict resolution
- `kata-stacked-pr-merge` "Variant: git-spice" section — bottom-up merge with `gs repo sync`
- `cry-new-stacked-pr` — shortcut that dispatches kata-create by `stacked_prs.tool`
- `lex-protected-trunk` — trunk protection preserved (`gs` honors it)
- `lex-git-branches` — `gs` accepts the naming `{type}/{N}-stack-{layer}-{slug}`
- `lex-signed-commits` — GPG signing preserved via global `commit.gpgsign=true`
- `lex-pr-quality` — labels/assignee/reviewers still applied via `gh pr edit` per PR
