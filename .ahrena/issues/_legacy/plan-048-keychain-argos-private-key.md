---
plan_id: "048"
title: "keychain-argos-private-key"
status: in-progress
agent: claude
issue: "guardiatechnology/ahrena#138"
created_at: "2026-05-12T23:30:00Z"
updated_at: "2026-05-12T23:30:00Z"
---

# Plan: macOS Keychain support for warrior-argos private key

## Objective

Allow the `ahrena-warrior-argos[bot]` GitHub App private key to live in the macOS login Keychain instead of as a `.pem` file under `~/.guardia/`. Dual-mode resolution in `scripts/argos/auth.sh`: Keychain wins when available, file path fallback when not (Linux/CI).

## Steps

- [x] Step 0 — Issue #138 + worktree
- [ ] Step 1 — Update `scripts/argos/auth.sh`: detect macOS + Keychain entry at service `ahrena.warrior-argos.github-app`; if present, materialize to ephemeral `mktemp` (chmod 600 + trap cleanup) and use that as `PRIVATE_KEY_PATH`. If absent, fallback to env-var path.
- [ ] Step 2 — Update `framework/{pt-BR,es,en}/engineering/quality/warriors/warrior-argos.md` Authentication section: add "Keychain mode (macOS — recommended)" subsection alongside the existing File mode.
- [ ] Step 3 — Update `.env.sample` with a comment noting Keychain wins when present.
- [ ] Step 4 — Re-sync `.claude/agents/` and `.cursor/agents/` via `scripts/install.py --self`.
- [ ] Step 5 — Smoke test: `security add-generic-password` the current `.pem`, invalidate token cache, run `auth.sh`, verify mint via Keychain path + tempfile cleanup.
- [ ] Step 6 — Commit + push + open PR per `lex-pr-quality`.
- [ ] Step 7 — Argos review (paper-trail rule will be satisfied if Argos finds anything).

## Dependencies

- ✅ Issue #132 shipped the .pem-based path that this enhances
- ✅ `pinentry-mac` already installed (orthogonal to this — GPG vs. App key)
- ✅ `security` CLI built-in on macOS

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| 1 | Tempfile leaks if `auth.sh` is SIGKILLed | `trap … EXIT` catches normal exits; SIGKILL is unfixable but the window is ~1s and `umask 077` ensures 0600 perms even if leaked |
| 2 | Keychain prompt for ACL when first reading | First read may pop "auth.sh wants to use Keychain" — user clicks "Always Allow" once |
| 3 | Linux/CI breakage | Explicit OS check; fallback path is unchanged |
| 4 | Multiple keys (key rotation): wrong key returned | Service name includes app suffix `ahrena.warrior-argos.github-app`; account name optional but `-a warrior-argos` recommended for unambiguity |
