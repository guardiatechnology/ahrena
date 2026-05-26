---
name: kata-commit
description: "Create Standardized Commit. Creating commits compliant with Guardia Lexis"
---

# Kata: Create Standardized Commit

> **Prefix:** `kata-` | **Type:** Repeatable Skill | **Scope:** Creating commits compliant with Guardia Lexis

## Workflow

```
Progress:
- [ ] 1. Analyze changes
- [ ] 2. Classify and compose message
- [ ] 3. Validate against Lexis
- [ ] 4. Resolve author (human or warriors-default)
- [ ] 5. Execute commit
- [ ] 6. Final verification
```

### Step 1: Analyze Changes

1. Run `git status` to check staged files
2. If no files are staged, analyze the diff and suggest what to include with `git add`
3. Run `git diff --staged` to understand the content of the changes
4. Verify that changes are atomic (`lex-small-commits`):
   - Do all changes belong to a single purpose?
   - If not, guide the user to split into separate commits

### Step 2: Classify and Compose Message

1. Consult `codex-commit-standards` for reference
2. **Identify the type:** feat, fix, docs, build, chore, ci, style, refactor, perf, test
3. **Identify the scope:** main affected module or domain (optional)
4. **Compose the subject:**
   - Imperative present tense in English (`lex-commit-language`)
   - Maximum 72 characters
   - No trailing period
   - Format: `type(scope): description`
5. **Compose the body (if needed):**
   - English version with `[en]` tag
   - Local language version with `[pt-BR]` or `[es]` tag (if requested)
   - Detail the "why" of the change
6. **Add footers (if applicable):**
   - `Closes #N` to close issues
   - `BREAKING CHANGE:` for incompatible changes
   - `Co-authored-by:` for pair programming

### Step 3: Validate Against Lexis

Verify compliance with each Lexis before executing:

- [ ] `lex-conventional-commits`: correct `type(scope): description` format?
- [ ] `lex-small-commits`: atomic changes (single purpose)?
- [ ] `lex-commit-language`: subject in English? Language tag in the body?
- [ ] `lex-signed-commits`: GPG configured? (`git config --get commit.gpgsign` = true)

If any validation fails, fix it before proceeding.

### Step 4: Resolve Author (human or warriors-default)

Before invoking `git commit`, the kata decides between two authorship paths:

1. **Source `scripts/ahrena-auth.sh`** (always — it is a no-op when `warriors_default_author.enabled=false`):
   ```bash
   source scripts/ahrena-auth.sh
   ```
   When the directive is off, the script returns immediately without exporting anything. When on, it exports `GH_TOKEN_AHRENA_WARRIORS_DEFAULT` (the GitHub App installation token) and the `GIT_AUTHOR_*` / `GIT_COMMITTER_*` variables pointing at the fleet-default `[bot]` identity (`ahrena-bot[bot]`).

2. **Read `warriors_default_author.enabled` and `warriors_default_author.apply_to`** from `.ahrena/.directives`.

3. **Routing decision:**
   - If `warriors_default_author.enabled == true` AND the `--warrior <name>` input was provided AND `<name>` is in `warriors_default_author.apply_to`: take the **warriors-default-author path** (Step 5a below).
   - Otherwise (no `--warrior`, master switch off, or warrior not in `apply_to`): take the **human path** (Step 5b).

4. **Warriors-default-author path** — assemble the `Co-authored-by` from the human driving the session:
   ```bash
   HUMAN_CO_AUTHOR="$(git config user.name) <$(git config user.email)>"
   ```
   That value becomes the commit trailer in Step 5a.

### Step 5: Execute Commit

#### Step 5a: Warriors-default-author path (server-side)

When Step 4 routed to the warriors-default-author path:

1. Invoke `scripts/ahrena-api-commit.sh` to create the commit via the GitHub Git Data API:
   ```bash
   scripts/ahrena-api-commit.sh \
     --branch "$(git rev-parse --abbrev-ref HEAD)" \
     --message "$(cat <<'EOF'
   type(scope): description

   [en]
   Detailed description in English.

   [pt-BR]
   Descrição detalhada em português.

   Closes #123
   EOF
   )" \
     --co-author "${HUMAN_CO_AUTHOR}"
   ```

2. The script runs `POST /git/blobs` (per staged file) → `POST /git/trees` → `POST /git/commits` → `PATCH /git/refs/heads/{branch}`. The resulting commit is signed by the App installation token (server-verified) and attributed to `ahrena-bot[bot]`.

3. Script exit codes:
   - `0` — commit created on the remote + local working tree resynced.
   - `2` — network/API failure (commit NOT created). **Mandatory fallback**: fall through to Step 5b (human path) and emit a visible warning explaining the degradation.
   - `3` — commit created on the remote BUT the local `git fetch && git reset --hard` failed. Warn the user to resync manually before the next push.

4. On fallback from exit code `2`, the agent MUST keep the staged content (do not undo `git add`) and proceed with Step 5b.

#### Step 5b: Human path (local, GPG signature)

When Step 4 routed to the human path (or as the fallback from 5a):

1. Run the commit with GPG signature:
   ```
   git commit -S -m "<message>"
   ```
2. For multiline messages (with body), use:
   ```
   git commit -S -m "$(cat <<'EOF'
   type(scope): description

   [en]
   Detailed description in English.

   [pt-BR]
   Descrição detalhada em português.

   Closes #123
   EOF
   )"
   ```

### Step 6: Final Verification

- [ ] `git log -1 --format='%s'` shows the correct subject
- [ ] **Human path (5b):** `git log -1 --show-signature` shows a valid GPG signature
- [ ] **Warriors-default-author path (5a):** `git log -1 --format='%an <%ae>'` shows `ahrena-bot[bot]` and the commit displays the **Verified** badge on GitHub
- [ ] **Warriors-default-author path (5a):** the commit body contains the `Co-authored-by: <human>` trailer when `warriors_default_author.commit_co_author=human`
- [ ] The commit contains only the intended changes
- [ ] The subject is in English and follows Conventional Commits
- [ ] The commit is atomic (single logical change)

## Outputs

| Output | Format | Destination |
|--------|--------|-------------|
| Signed and formatted commit | Git commit | Local repository |

## Constraints

- Never commit without verifying compliance with all 4 Lexis
- Never mix unrelated changes in a single commit
- On the human path (Step 5b), never commit without a configured GPG signature — if GPG is not configured, alert the user and guide the setup
- On the warriors-default-author path (Step 5a), the signature is served by the GitHub App installation token; no local GPG is required
- Never silence a failure of `ahrena-api-commit.sh` — always inform the user when there is a fallback to the human path
