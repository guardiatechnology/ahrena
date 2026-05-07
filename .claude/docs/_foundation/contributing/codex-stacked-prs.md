# Codex: Stacked Pull Requests in the Ahrena Context

> **Prefix:** `codex-` | **Type:** Reference Manual | **Scope:** Concept, decision model, and operation of stacked Pull Requests for large features in any Guardia repository

## 1. Conceptual model

### 1.1 Branch chain

```
main
 └── feat/{N}-stack-1-{slug}     ← PR #X (base: main)
      └── feat/{N}-stack-2-{slug}  ← PR #Y (base: feat/{N}-stack-1-{slug})
           └── feat/{N}-stack-3-{slug}  ← PR #Z (base: feat/{N}-stack-2-{slug})
```

Each layer is a real PR on GitHub, with its base pointing to the previous layer. The base layer points to `main`. All PRs share a single shared worktree (see section 4).

### 1.2 Issue model (1 → N)

A single umbrella issue governs the entire stack. Layers reference it as follows:

| Layer | PR body |
|---|---|
| 1..N-1 (intermediate) | `Refs #N` |
| N (last) | `Closes #N` |

When the last layer merges, GitHub closes the issue automatically. **Do not create child issues** per layer — the model is umbrella issue + numbered ACs that map to layers. See `lex-issue-first` for the base rule.

### 1.3 Naming pattern

Compatible with `lex-git-branches`:

```
{type}/{N}-stack-{layer}-{slug}
```

| Field | Rule |
|---|---|
| `type` | One of the Conventional Commits types: `feat`, `fix`, `docs`, `build`, `chore`, `ci`, `style`, `refactor`, `perf`, `test` |
| `N` | Umbrella issue number |
| `layer` | Integer 1, 2, 3, ... (layer in the stack, base→top) |
| `slug` | kebab-case, max 50 characters total |

Valid examples:
- `feat/42-stack-1-schema`
- `feat/42-stack-2-api`
- `feat/42-stack-3-ui`

The literal `stack-{layer}` segment in the slug is the canonical signal that the branch belongs to a stack.

> **Important:** `{slug}` is unique and shared by the entire stack — it is the same `{slug}` used in the worktree directory (`.worktrees/{N}-{slug}-stack/`); only `{layer}` distinguishes layers. The names `schema`/`api`/`ui` in the examples above are values of `{layer}`, not of `{slug}`.

---

## 2. Decision Checklist (canonical)

This section is the **source of truth** consulted by `kata-stacked-pr-create` in Phase 0 (Pre-flight) and by `cry-new-stacked-pr` on explicit invocation. Do not duplicate criteria in other artifacts.

### 2.1 High signals (each counts 1 point)

| Signal | Threshold |
|---|---|
| Estimated diff size | > 500 lines modified |
| Independent ACs in the issue | ≥ 4 ACs |
| Technical Pillars crossed | ≥ 2 (e.g., backend + frontend) |
| Obvious layers present | schema → API → UI; data → service → handler; or equivalent |
| Review independence | reviewer A can assess layer X without needing context from Y |
| Per-layer rollback risk | change with migration + visible feature in the same issue |

### 2.2 Anti-signals (any present vetoes the stack)

| Anti-signal | Reason |
|---|---|
| Hotfix / incident response | speed > granularity; cascade rebase delays the fix |
| Cross-fork PR | stack tools do not support this well; manual stacking is fragile |
| Monolithic refactor | change that does not decompose into independent layers (e.g., rename across the entire module) |

### 2.3 Heuristic

- **≥ 3 high signals AND 0 anti-signals** → propose a stack with concrete decomposition
- **Otherwise** → redirect to a single PR (`kata-contributing-pr`)

The final decision always belongs to the human. The agent **proposes**, the user **confirms**.

### 2.4 Typical decompositions

| Feature type | Suggested layers |
|---|---|
| New API with persistence | 1) migration + entity, 2) repository + use case, 3) router + DTOs, 4) tests + observability |
| UI feature with backend | 1) schema + migration, 2) API endpoints, 3) frontend components, 4) E2E + telemetry |
| Refactor with module extraction | 1) new isolated module, 2) call sites migrated, 3) cleanup of old code |
| Adopting a new Lexis | 1) Lexis + Codex, 2) operational Kata, 3) Cry and platforms.yaml updates |

---

## 3. Mapping to affected Lexis

Stacked PRs coexist with existing Lexis. The table below is a quick reference:

| Lexis | Status | How Stacked PRs comply |
|---|---|---|
| `lex-protected-trunk` | ✅ | Force-push only on stack branches, never on trunk; PRs merge through the normal flow |
| `lex-issue-first` | ✅ | Umbrella issue exists before the base branch; each PR references via `Refs #N` or `Closes #N` |
| `lex-issue-quality` | ✅ | Umbrella issue meets the 5 canonical criteria once; layers inherit |
| `lex-git-branches` | ✅ | Naming `{type}/{N}-stack-{layer}-{slug}` matches the regex `^(feat\|fix\|...)\/[0-9]+-[a-z0-9][a-z0-9-]{0,49}$` |
| `lex-git-worktrees` | ⚠️ exception | A stack uses **a single** shared worktree: `.worktrees/{N}-{slug}-stack/`. Clause declared in "Allowed exceptions" of the Lexis |
| `lex-pr-quality` | ✅ | The 8-criteria HARD-GATE applies **per PR in the stack** (each layer is a real PR); issue labels mirror to each one |
| `lex-conventional-commits` | ✅ | Each layer uses conventional commits as usual |
| `lex-small-commits` | ✅ | Layers reinforce atomicity — one logical change per layer |
| `lex-signed-commits` | ✅ | Rebase preserves GPG signature when `commit.gpgsign=true` |
| `lex-commit-language` | ✅ | No change |
| `lex-issue-driven` | 🔄 follow-up | Athena does not yet orchestrate stacks; covered by plan-006 (future) |

---

## 4. Shared worktree

Unlike the standard flow (1 branch = 1 worktree), an entire stack uses **a single** worktree:

```
.worktrees/{N}-{slug}-stack/
```

| Field | Rule |
|---|---|
| `N` | Umbrella issue number |
| `slug` | Descriptive slug, without the `stack-{layer}` segment |

Example: for issue #42 (scheduled payments), the worktree is `.worktrees/42-scheduled-payments-stack/`. Inside it, the agent switches between stack branches via `git checkout`.

Technical reason: cascade rebase operates by reading and rewriting the branches in sequence; one worktree per branch breaks the single working dir assumption.

The exception is declared in `lex-git-worktrees` under "Allowed exceptions" (Rule 5).

---

## 5. Stack lifecycle

```
umbrella issue exists
    ↓
Decision Checklist (Phase 0 of kata-create)  →  failed: single PR
    ↓ approved
create shared worktree
    ↓
for each layer i in 1..N:
    git checkout -b feat/{N}-stack-{i}-{slug}
    work
    signed commit
    push
    gh pr create --base {previous layer}
    gh pr edit (mirror labels/assignee/reviewers)
    ↓
review happens in parallel (lower layer first)
    ↓
change in lower layer?  →  cascade rebase (kata-rebase)
    ↓
bottom-up merge (kata-merge):
    merge layer 1
    gh pr edit layer 2 --base main
    rebase layer 2 onto main
    repeat for upper layers
    ↓
after the last layer merges:
    git worktree remove
    cleanup local branches
```

Operational details live in the dedicated katas:

- `kata-stacked-pr-create` — Phase 0 (Decision Checklist) and chain creation
- `kata-stacked-pr-rebase` — manual cascade rebase after a lower-layer change
- `kata-stacked-pr-merge` — bottom-up policy and cleanup

---

## 6. Recommended limits

| Aspect | Vanilla limit | When to exceed |
|---|---|---|
| Number of layers | 3-4 | Consider git-spice (plan-005), which automates cascade rebase |
| Average size per layer | 200-500 lines | Very small layers signal artificial decomposition; very large layers cancel the review benefit |
| Stack lifetime | ≤ 2 weeks | Long stacks accumulate conflicts with `main`; prefer to merge lower layers and open a new stack |
| ACs per layer | 1-3 ACs | More than that signals a layer that is too broad; refine the decomposition |

---

## 7. Trade-offs of the vanilla path

| Advantage | Trade-off |
|---|---|
| Zero external dependency — works on any GitHub repository today | Cascade rebase is manual; each lower-layer change requires 1 rebase + 1 push per upper layer |
| Transparent flow — every command is a readable `git`/`gh` invocation | More prone to human error (rebase against the wrong branch, force-push without lease) |
| Compatible with any existing hook/lint/CI | No native "stack map" UI; reviewers must navigate PR by PR |
| Step-by-step auditable | Reordering layers in the middle is expensive (recreate manually) |

For stacks of 4+ layers or high iteration frequency, consider `git-spice` once plan-005 lands.

---

## 8. Best practices

1. **Decompose by contract, not by file.** Layers must represent stable interfaces (schema, API, UI), not directories. The reviewer of layer N+1 trusts the contract closed by layer N.
2. **`--force-with-lease` always.** Never `--force` blindly. The lease prevents overwriting commits from someone else who was reviewing the layer.
3. **Merge lower layers fast.** Do not wait for the entire stack to merge the base — the longer it lives, the more conflict it accumulates.
4. **Update the next PR's `base` explicitly after each merge.** GitHub does not migrate automatically; see `kata-stacked-pr-merge`.
5. **Mirror labels on each layer.** `lex-pr-quality` applies per PR; `kata-stacked-pr-create` automates this via `gh pr edit`.
6. **Write in each PR's body which slice it covers.** E.g., `Refs #42 (2/3 — API endpoints)`. Helps reviewers understand the position.

---

## 9. When NOT to use stacked PRs

- Trivial change (typo, docs minor, single-file refactor) — N-PR overhead exceeds the gain
- Incident hotfix — speed > granularity
- Stack proposed without natural layers (forcing artificial decomposition)
- Team unfamiliar with `git rebase` — cascade error risk
- Cross-fork — technical limitation of stack tools

In any of these cases, the agent redirects to `kata-contributing-pr` (single PR).

---

## 10. Directive `stacked_prs.tool`

In `.ahrena/.directives`:

```yaml
stacked_prs:
  tool: vanilla   # vanilla | gs
```

| Value | Behavior |
|---|---|
| `vanilla` | Default; follows the procedures in this codex and the corresponding katas |
| `gs` | Available after plan-005 lands; activates the "Variant: git-spice" sections of the katas |

Absence of the directive = implicit `vanilla`.

---
