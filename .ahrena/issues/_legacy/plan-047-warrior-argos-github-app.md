---
plan_id: "047"
title: "warrior-argos-github-app"
status: in-progress
agent: claude
issue: "guardiatechnology/ahrena#132"
created_at: "2026-05-12T19:15:00Z"
updated_at: "2026-05-12T19:15:00Z"
---

# Plan: Wire warrior-argos to GitHub App (bot identity for PR reviews)

## Objective

Wire `warrior-argos` to authenticate as the `ahrena-warrior-argos` GitHub App (already created by user) so PR review comments appear under the `ahrena-warrior-argos[bot]` identity instead of the human user's account. Distinction between human and Argos reviews stops depending on the textual `argos-review-id:` marker; it becomes visible in the GitHub UI at a glance.

All 4 dependencies (App created, key generated, credentials wired via `.env.local`, permissions confirmed) are already resolved per Issue #132.

## Steps

- [x] Step 0 — Worktree + branch created (`feat/132-warrior-argos-github-app`)
- [ ] Step 1 — Block A: `scripts/argos/auth.sh` (bash + openssl, JWT RS256 → installation token, cache at `.ahrena/argos/installation-token.json`)
- [ ] Step 2 — Block B: Update `framework/{pt-BR,es,en}/engineering/quality/warriors/warrior-argos.md` with Authentication section; sync `.claude/agents/warrior-argos.md` + `.cursor/agents/warrior-argos.md`
- [ ] Step 3 — Block C: Update `framework/.directives.sample` (add `ahrena-warrior-argos[bot]` to `pr_cost_tracking.known_ai_reviewers` default + document `AHRENA_WARRIOR_ARGOS_GH_*` env vars); mirror in `lex-directives` table 3 langs
- [ ] Step 4 — Add `.ahrena/argos/` to `framework/.gitignore.sample` (and verify already covered in repo's `.gitignore` since `.ahrena/` is wildcarded)
- [ ] Step 5 — Block D: Smoke test on a real PR (find an open PR or use PR #136 retroactively); verify comment author appears as `ahrena-warrior-argos[bot]`
- [ ] Step 6 — Block E: Open PR per `lex-issue-first` + `lex-pr-quality`

## Dependencies

- ✅ GitHub App `ahrena-warrior-argos` created (bot: `ahrena-warrior-argos[bot]`)
- ✅ Private key at `~/.guardia/guardiatechnology/ahrena/warrior-argos.2026-05-12.private-key.pem` (chmod 600)
- ✅ `.env.local` template populated with `AHRENA_WARRIOR_ARGOS_GH_APP_ID`, `AHRENA_WARRIOR_ARGOS_GH_INSTALLATION_ID`, `AHRENA_WARRIOR_ARGOS_GH_PRIVATE_KEY_PATH`
- ✅ App permissions confirmed (Pull requests R/W + Contents R + Issues R/W + Metadata R)
- ✅ `.gitignore` already protects `.env*` (PR #136 merged into main)

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| 1 | JWT signing via openssl produces invalid signature for GitHub | Test with `gh api /app` after running auth.sh; document fallback to Python `cryptography` if needed |
| 2 | Token cache lingers stale across worktrees | Path is project-scope (each worktree has its own `.ahrena/`); TTL 50min < 60min limit |
| 3 | `.env.local` not copied to new worktree → script fails silently | auth.sh validates required env vars are set + non-empty; emits clear error |
| 4 | Smoke test PR has no AI bot comments to verify against | Use a freshly opened test PR or invoke Argos against PR #136 retroactively |
